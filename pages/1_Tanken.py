import streamlit as st
from datetime import date

from supabase_client import get_supabase


st.set_page_config(
    page_title="Tanken",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Tankbeurt toevoegen")
st.caption("Registreer een nieuwe tankbeurt.")

supabase = get_supabase()


col1, col2 = st.columns(2)

with col1:
    datum = st.date_input(
        "Datum",
        value=date.today()
    )

    kilometerstand = st.number_input(
        "Kilometerstand",
        min_value=0,
        step=1
    )

    liters = st.number_input(
        "Aantal liters",
        min_value=0.0,
        step=0.1,
        format="%.2f"
    )

with col2:
    prijs_per_liter = st.number_input(
        "Prijs per liter (€)",
        min_value=0.0,
        step=0.001,
        format="%.3f"
    )

    tankstation = st.text_input(
        "Tankstation"
    )

    volle_tank = st.checkbox(
        "Volle tank",
        value=True
    )


totaalbedrag = liters * prijs_per_liter

st.metric(
    "Totaalbedrag",
    f"€ {totaalbedrag:.2f}"
)


if st.button(
    "💾 Tankbeurt opslaan",
    use_container_width=True
):

    st.divider()

st.subheader("📊 Tankoverzicht")

try:
    response = (
        supabase
        .table("tankbeurten")
        .select("*")
        .order("datum", desc=True)
        .execute()
    )

    tankbeurten = response.data

    if tankbeurten:
        import pandas as pd

        df = pd.DataFrame(tankbeurten)

        # Numerieke kolommen goed omzetten
        df["liters"] = pd.to_numeric(df["liters"], errors="coerce")
        df["prijs_per_liter"] = pd.to_numeric(df["prijs_per_liter"], errors="coerce")
        df["totaalbedrag"] = pd.to_numeric(df["totaalbedrag"], errors="coerce")
        df["kilometerstand"] = pd.to_numeric(df["kilometerstand"], errors="coerce")

        # Kerncijfers
        totale_kosten = df["totaalbedrag"].sum()
        totaal_liters = df["liters"].sum()
        gem_prijs = df["prijs_per_liter"].mean()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Totale brandstofkosten",
            f"€ {totale_kosten:.2f}"
        )

        c2.metric(
            "Totaal getankte liters",
            f"{totaal_liters:.1f} L"
        )

        c3.metric(
            "Gem. prijs per liter",
            f"€ {gem_prijs:.3f}"
        )

        st.divider()

        st.subheader("🧾 Tankhistorie")

        overzicht = df[
            [
                "datum",
                "kilometerstand",
                "liters",
                "prijs_per_liter",
                "totaalbedrag",
                "tankstation",
                "volle_tank"
            ]
        ].copy()

        overzicht = overzicht.rename(
            columns={
                "datum": "Datum",
                "kilometerstand": "Kilometerstand",
                "liters": "Liters",
                "prijs_per_liter": "Prijs per liter",
                "totaalbedrag": "Totaalbedrag",
                "tankstation": "Tankstation",
                "volle_tank": "Volle tank"
            }
        )

        overzicht["Prijs per liter"] = overzicht["Prijs per liter"].map(
            lambda x: f"€ {x:.3f}"
        )

        overzicht["Totaalbedrag"] = overzicht["Totaalbedrag"].map(
            lambda x: f"€ {x:.2f}"
        )

        overzicht["Liters"] = overzicht["Liters"].map(
            lambda x: f"{x:.2f}"
        )

        st.dataframe(
            overzicht,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Er zijn nog geen tankbeurten opgeslagen.")

except Exception as e:
    st.error("Tankhistorie kon niet worden geladen.")
    st.exception(e)