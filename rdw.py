import requests


RDW_VOERTUIG_URL = (
    "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
)

RDW_BRANDSTOF_URL = (
    "https://opendata.rdw.nl/resource/8ys7-d773.json"
)


def normaliseer_kenteken(kenteken):
    """
    Zet bijvoorbeeld 35-RV-VJ om naar 35RVVJ.
    """

    if not kenteken:
        return ""

    return (
        kenteken
        .replace("-", "")
        .replace(" ", "")
        .upper()
        .strip()
    )


def rdw_datum_naar_iso(waarde):
    """
    RDW gebruikt voor sommige datumvelden YYYYMMDD.
    Zet dat om naar YYYY-MM-DD.
    """

    if not waarde:
        return None

    waarde = str(waarde)

    if len(waarde) != 8:
        return None

    try:
        return (
            f"{waarde[0:4]}-"
            f"{waarde[4:6]}-"
            f"{waarde[6:8]}"
        )

    except Exception:
        return None


def get_vehicle_by_plate(kenteken):
    """
    Haal voertuiggegevens op bij RDW.
    """

    kenteken_schoon = normaliseer_kenteken(
        kenteken
    )

    if not kenteken_schoon:
        return None


    params = {
        "kenteken": kenteken_schoon
    }


    try:

        response = requests.get(
            RDW_VOERTUIG_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        resultaten = response.json()


        if not resultaten:
            return None


        voertuig = resultaten[0]


        # ----------------------------------------
        # Brandstof apart ophalen
        # ----------------------------------------

        brandstof = None
        vermogen_kw = None

        try:

            brandstof_response = requests.get(
                RDW_BRANDSTOF_URL,
                params=params,
                timeout=10,
            )

            brandstof_response.raise_for_status()

            brandstof_resultaten = brandstof_response.json()

            if brandstof_resultaten:

                brandstof_data = brandstof_resultaten[0]

                brandstof = brandstof_data.get(
                    "brandstof_omschrijving"
                )

                vermogen_kw = brandstof_data.get(
                    "nettomaximumvermogen"
                )

        except Exception:
            pass


        # ----------------------------------------
        # Gegevens netjes teruggeven
        # ----------------------------------------

        return {
            "kenteken":
                kenteken_schoon,

            "merk":
                voertuig.get(
                    "merk"
                ),

            "handelsbenaming":
                voertuig.get(
                    "handelsbenaming"
                ),

            "vermogen_kw": vermogen_kw,

            "voertuigsoort":
                voertuig.get(
                    "voertuigsoort"
                ),

            "datum_eerste_toelating":
                rdw_datum_naar_iso(
                    voertuig.get(
                        "datum_eerste_toelating"
                    )
                ),

            "vervaldatum_apk":
                rdw_datum_naar_iso(
                    voertuig.get(
                        "vervaldatum_apk"
                    )
                ),

            "catalogusprijs":
                voertuig.get(
                    "catalogusprijs"
                ),

            "massa_ledig_voertuig":
                voertuig.get(
                    "massa_ledig_voertuig"
                ),

            "massa_rijklaar":
                voertuig.get(
                    "massa_rijklaar"
                ),

            "aantal_cilinders":
                voertuig.get(
                    "aantal_cilinders"
                ),

            "cilinderinhoud":
                voertuig.get(
                    "cilinderinhoud"
                ),

            "kleur":
                voertuig.get(
                    "eerste_kleur"
                ),

            "brandstof":
                brandstof,
        }


    except requests.RequestException:

        return None