import requests
import streamlit as st


GEOCODING_URL = (
    "https://api.mapbox.com/search/geocode/v6/forward"
)

DIRECTIONS_BASE_URL = (
    "https://api.mapbox.com/directions/v5/mapbox/driving"
)


def get_mapbox_token():
    return st.secrets["MAPBOX_TOKEN"]


def zoek_locatie(zoektekst):
    """
    Zet een adres/plaatsnaam om naar coordinaten.
    Gericht op Nederland.
    """

    if not zoektekst or not zoektekst.strip():
        return None

    params = {
        "q": zoektekst.strip(),
        "access_token": get_mapbox_token(),
        "country": "nl",
        "language": "nl",
        "limit": 1,
        "autocomplete": "false",
    }

    try:
        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        features = data.get("features", [])

        if not features:
            return None

        feature = features[0]

        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])

        if len(coordinates) < 2:
            return None

        properties = feature.get("properties", {})

        return {
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "naam": (
                properties.get("full_address")
                or properties.get("name")
                or zoektekst
            ),
        }

    except requests.RequestException:
        return None


def bereken_route(van, naar):
    """
    Zoekt beide locaties op en berekent daarna
    de autoroute ertussen.
    """

    van_locatie = zoek_locatie(van)
    naar_locatie = zoek_locatie(naar)

    if not van_locatie:
        return {
            "success": False,
            "error": f"Startlocatie niet gevonden: {van}",
        }

    if not naar_locatie:
        return {
            "success": False,
            "error": f"Bestemming niet gevonden: {naar}",
        }

    coordinaten = (
        f"{van_locatie['longitude']},"
        f"{van_locatie['latitude']};"
        f"{naar_locatie['longitude']},"
        f"{naar_locatie['latitude']}"
    )

    url = f"{DIRECTIONS_BASE_URL}/{coordinaten}"

    params = {
        "access_token": get_mapbox_token(),
        "overview": "false",
        "steps": "false",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        routes = data.get("routes", [])

        if not routes:
            return {
                "success": False,
                "error": "Geen autoroute gevonden.",
            }

        route = routes[0]

        afstand_meter = route.get("distance", 0)
        duur_seconden = route.get("duration", 0)

        return {
            "success": True,
            "van": van_locatie["naam"],
            "naar": naar_locatie["naam"],
            "afstand_km": round(
                afstand_meter / 1000,
                1,
            ),
            "duur_minuten": round(
                duur_seconden / 60
            ),
            "van_latitude": van_locatie["latitude"],
            "van_longitude": van_locatie["longitude"],
            "naar_latitude": naar_locatie["latitude"],
            "naar_longitude": naar_locatie["longitude"],
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Route kon niet worden berekend: {e}",
        }