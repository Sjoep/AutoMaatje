import streamlit as st
import pandas as pd
import plotly.express as px

from streamlit_elements import elements, mui
from supabase_client import get_supabase


# ─────────────────────────────────────────────
# Pagina
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AutoMaatje",
    page_icon="🚗",
    layout="wide",
)

supabase = get_supabase()


# ─────────────────────────────────────────────
# Data ophalen
# ─────────────────────────────────────────────

@st.cache_data(ttl=60)
def load_data():

    tank_response = (
        supabase
        .table("tankbeurten")
        .select("*")
        .order("datum", desc=True)
        .execute()
    )

    rit_response = (
        supabase
        .table("ritten")
        .select("*")
        .order("datum", desc=True)
        .execute()
    )

    tank_df = pd.DataFrame(tank_response.data)
    rit_df = pd.DataFrame(rit_response.data)

    return tank_df, rit_df


try:
    tank_df, rit_df = load_data()

except Exception as e:
    st.error("De gegevens konden niet uit Supabase worden geladen.")
    st.exception(e)
    st.stop()


# ─────────────────────────────────────────────
# Ritten voorbereiden
# ─────────────────────────────────────────────

if not rit_df.empty:

    rit_df["datum"] = pd.to_datetime(
        rit_df["datum"],
        errors="coerce"
    )

    rit_df["kilometers"] = pd.to_numeric(
        rit_df["kilometers"],
        errors="coerce"
    )

    rit_df["vergoeding_per_km"] = pd.to_numeric(
        rit_df["vergoeding_per_km"],
        errors="coerce"
    )

    rit_df["belastingvrij_per_km"] = pd.to_numeric(
        rit_df["belastingvrij_per_km"],
        errors="coerce"
    )

    rit_df["belastingpercentage"] = pd.to_numeric(
        rit_df["belastingpercentage"],
        errors="coerce"
    )


    # Alleen zakelijke en woon-werkritten tellen mee
    zakelijke_df = rit_df[
        rit_df["type_rit"].isin(
            ["Zakelijk", "Woon-werk"]
        )
    ].copy()


    zakelijke_df["bruto_vergoeding"] = (
        zakelijke_df["kilometers"]
        * zakelijke_df["vergoeding_per_km"]
    )


    zakelijke_df["belastingvrij_bedrag"] = (
        zakelijke_df["kilometers"]
        * zakelijke_df[
            [
                "vergoeding_per_km",
                "belastingvrij_per_km"
            ]
        ].min(axis=1)
    )


    zakelijke_df["belast_bedrag"] = (
        zakelijke_df["bruto_vergoeding"]
        - zakelijke_df["belastingvrij_bedrag"]
    ).clip(lower=0)


    zakelijke_df["belasting"] = (
        zakelijke_df["belast_bedrag"]
        * (zakelijke_df["belastingpercentage"] / 100)
    )


    zakelijke_df["netto_vergoeding"] = (
        zakelijke_df["bruto_vergoeding"]
        - zakelijke_df["belasting"]
    )


    totaal_km = zakelijke_df["kilometers"].sum()
    totaal_netto = zakelijke_df["netto_vergoeding"].sum()

else:

    zakelijke_df = pd.DataFrame()

    totaal_km = 0
    totaal_netto = 0


# ─────────────────────────────────────────────
# Tankdata voorbereiden
# ─────────────────────────────────────────────

if not tank_df.empty:

    tank_df["datum"] = pd.to_datetime(
        tank_df["datum"],
        errors="coerce"
    )

    tank_df["kilometerstand"] = pd.to_numeric(
        tank_df["kilometerstand"],
        errors="coerce"
    )

    tank_df["liters"] = pd.to_numeric(
        tank_df["liters"],
        errors="coerce"
    )

    tank_df["prijs_per_liter"] = pd.to_numeric(
        tank_df["prijs_per_liter"],
        errors="coerce"
    )

    tank_df["totaalbedrag"] = pd.to_numeric(
        tank_df["totaalbedrag"],
        errors="coerce"
    )


    totale_brandstofkosten = tank_df[
        "totaalbedrag"
    ].sum()


    # ── Verbruik uit volle tankbeurten
    volle_tanks = tank_df[
        tank_df["volle_tank"] == True
    ].copy()

    volle_tanks = volle_tanks.sort_values(
        "kilometerstand"
    )

    volle_tanks["gereden_km"] = (
        volle_tanks["kilometerstand"].diff()
    )

    volle_tanks["verbruik"] = (
        volle_tanks["liters"]
        / volle_tanks["gereden_km"]
        * 100
    )

    volle_tanks.loc[
        (volle_tanks["gereden_km"] <= 0)
        | (volle_tanks["gereden_km"].isna()),
        "verbruik"
    ] = pd.NA


    gem_verbruik = volle_tanks[
        "verbruik"
    ].mean()

else:

    totale_brandstofkosten = 0
    gem_verbruik = None


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────

st.title("🚗 AutoMaatje")

st.caption(
    "Alles over je kilometers, brandstof en autokosten op één plek."
)


# ─────────────────────────────────────────────
# Mooie KPI cards met Streamlit Elements
# ─────────────────────────────────────────────

if pd.notna(gem_verbruik):
    verbruik_text = f"{gem_verbruik:.2f} L/100 km"
else:
    verbruik_text = "-"


with elements("dashboard_kpis"):

    with mui.Box(
        sx={
            "display": "grid",
            "gridTemplateColumns": {
                "xs": "1fr",
                "sm": "repeat(2, 1fr)",
                "md": "repeat(4, 1fr)",
            },
            "gap": 2,
            "marginTop": 2,
            "marginBottom": 2,
        }
    ):


        # Kilometers
        with mui.Paper(
            elevation=0,
            sx={
                "padding": 3,
                "borderRadius": 4,
                "border": "1px solid #e5e7eb",
            }
        ):

            mui.Typography(
                "Zakelijke kilometers",
                variant="body2",
                color="text.secondary"
            )

            mui.Typography(
                f"{totaal_km:,.0f} km",
                variant="h4",
                sx={
                    "fontWeight": 700,
                    "marginTop": 1
                }
            )


        # Netto vergoeding
        with mui.Paper(
            elevation=0,
            sx={
                "padding": 3,
                "borderRadius": 4,
                "border": "1px solid #e5e7eb",
            }
        ):

            mui.Typography(
                "Geschatte netto vergoeding",
                variant="body2",
                color="text.secondary"
            )

            mui.Typography(
                f"€ {totaal_netto:,.2f}",
                variant="h4",
                sx={
                    "fontWeight": 700,
                    "marginTop": 1
                }
            )


        # Brandstof
        with mui.Paper(
            elevation=0,
            sx={
                "padding": 3,
                "borderRadius": 4,
                "border": "1px solid #e5e7eb",
            }
        ):

            mui.Typography(
                "Brandstofkosten",
                variant="body2",
                color="text.secondary"
            )

            mui.Typography(
                f"€ {totale_brandstofkosten:,.2f}",
                variant="h4",
                sx={
                    "fontWeight": 700,
                    "marginTop": 1
                }
            )


        # Verbruik
        with mui.Paper(
            elevation=0,
            sx={
                "padding": 3,
                "borderRadius": 4,
                "border": "1px solid #e5e7eb",
            }
        ):

            mui.Typography(
                "Gemiddeld verbruik",
                variant="body2",
                color="text.secondary"
            )

            mui.Typography(
                verbruik_text,
                variant="h4",
                sx={
                    "fontWeight": 700,
                    "marginTop": 1
                }
            )


st.divider()


# ─────────────────────────────────────────────
# Grafieken
# ─────────────────────────────────────────────

st.subheader("📊 Ontwikkeling")

grafiek1, grafiek2 = st.columns(2)


# Kilometers per maand
with grafiek1:

    st.markdown("#### Kilometers per maand")

    if not rit_df.empty:

        rit_maand = rit_df.dropna(
            subset=["datum"]
        ).copy()

        rit_maand["Maand"] = (
            rit_maand["datum"]
            .dt.to_period("M")
            .astype(str)
        )

        km_per_maand = (
            rit_maand
            .groupby("Maand")["kilometers"]
            .sum()
            .reset_index()
        )

        fig_km = px.bar(
            km_per_maand,
            x="Maand",
            y="kilometers",
            labels={
                "kilometers": "Kilometers",
                "Maand": ""
            }
        )

        fig_km.update_layout(
            height=330,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),
        )

        st.plotly_chart(
            fig_km,
            use_container_width=True
        )

    else:

        st.info(
            "Voeg ritten toe om hier je kilometers te zien."
        )


# Brandstofkosten per maand
with grafiek2:

    st.markdown("#### Brandstofkosten per maand")

    if not tank_df.empty:

        tank_maand = tank_df.dropna(
            subset=["datum"]
        ).copy()

        tank_maand["Maand"] = (
            tank_maand["datum"]
            .dt.to_period("M")
            .astype(str)
        )

        kosten_per_maand = (
            tank_maand
            .groupby("Maand")["totaalbedrag"]
            .sum()
            .reset_index()
        )

        fig_kosten = px.bar(
            kosten_per_maand,
            x="Maand",
            y="totaalbedrag",
            labels={
                "totaalbedrag": "Brandstofkosten (€)",
                "Maand": ""
            }
        )

        fig_kosten.update_layout(
            height=330,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),
        )

        st.plotly_chart(
            fig_kosten,
            use_container_width=True
        )

    else:

        st.info(
            "Voeg tankbeurten toe om hier brandstofkosten te zien."
        )


st.divider()


# ─────────────────────────────────────────────
# Recente activiteit
# ─────────────────────────────────────────────

st.subheader("🕘 Recente activiteit")

recent1, recent2 = st.columns(2)


# Laatste ritten
with recent1:

    st.markdown("#### 🛣️ Laatste ritten")

    if not rit_df.empty:

        recente_ritten = (
            rit_df
            .sort_values(
                "datum",
                ascending=False
            )
            .head(5)
        )

        kolommen = [
            "datum",
            "van",
            "naar",
            "kilometers",
            "type_rit"
        ]

        recente_ritten = recente_ritten[
            kolommen
        ].copy()

        recente_ritten["datum"] = (
            recente_ritten["datum"]
            .dt.strftime("%d-%m-%Y")
        )

        recente_ritten = recente_ritten.rename(
            columns={
                "datum": "Datum",
                "van": "Van",
                "naar": "Naar",
                "kilometers": "Km",
                "type_rit": "Type"
            }
        )

        st.dataframe(
            recente_ritten,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Nog geen ritten geregistreerd.")


# Laatste tankbeurten
with recent2:

    st.markdown("#### ⛽ Laatste tankbeurten")

    if not tank_df.empty:

        recente_tanks = (
            tank_df
            .sort_values(
                "datum",
                ascending=False
            )
            .head(5)
        )

        recente_tanks = recente_tanks[
            [
                "datum",
                "tankstation",
                "liters",
                "totaalbedrag"
            ]
        ].copy()

        recente_tanks["datum"] = (
            recente_tanks["datum"]
            .dt.strftime("%d-%m-%Y")
        )

        recente_tanks["totaalbedrag"] = (
            recente_tanks["totaalbedrag"]
            .apply(
                lambda x: f"€ {x:.2f}"
            )
        )

        recente_tanks = recente_tanks.rename(
            columns={
                "datum": "Datum",
                "tankstation": "Tankstation",
                "liters": "Liters",
                "totaalbedrag": "Bedrag"
            }
        )

        st.dataframe(
            recente_tanks,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Nog geen tankbeurten geregistreerd.")