import streamlit as st
import pandas as pd

from datetime import date
from auth import require_login
from ui_styles import apply_global_styles


# ============================================================
# PAGINA
# ============================================================

st.set_page_config(
    page_title="Tanken",
    page_icon="⛽",
    layout="centered",
)

apply_global_styles()

user, supabase = require_login()


# ============================================================
# TOAST NA OPSLAAN
# ============================================================

if st.session_state.get("tank_saved"):

    st.toast(
        st.session_state["tank_saved"],
        icon="✅"
    )

    del st.session_state["tank_saved"]


# ============================================================
# HEADER
# ============================================================

st.title("⛽ Tanken")

st.caption(
    "Registreer tankbeurten en houd je brandstofkosten overzichtelijk bij."
)


# ============================================================
# INVOER
# ============================================================

with st.container(
    border=True
):

    st.markdown(
        "#### 📅 Tankmoment"
    )

    col1, col2 = st.columns(2)

    with col1:

        datum = st.date_input(
            "Datum",
            value=date.today(),
        )

    with col2:

        kilometerstand = st.number_input(
            "Kilometerstand",
            min_value=0,
            step=1,
        )


with st.container(
    border=True
):

    st.markdown(
        "#### ⛽ Brandstof"
    )

    col3, col4 = st.columns(2)

    with col3:

        liters = st.number_input(
            "Aantal liters",
            min_value=0.0,
            step=0.1,
            format="%.2f",
        )

        tankstation = st.text_input(
            "Tankstation",
            placeholder="Bijvoorbeeld: Shell Hoorn",
        )

    with col4:

        prijs_per_liter = st.number_input(
            "Prijs per liter (€)",
            min_value=0.0,
            step=0.001,
            format="%.3f",
        )

        volle_tank = st.toggle(
            "Volle tank",
            value=True,
        )


# ============================================================
# BEREKENING
# ============================================================

totaalbedrag = (
    liters
    * prijs_per_liter
)


# ============================================================
# SAMENVATTING
# ============================================================

st.markdown(
    "### Samenvatting"
)

m1, m2, m3 = st.columns(3)

m1.metric(
    "Totaalbedrag",
    f"€ {totaalbedrag:.2f}"
)

m2.metric(
    "Liters",
    f"{liters:.2f} L"
)

m3.metric(
    "Prijs per liter",
    f"€ {prijs_per_liter:.3f}"
)


# ============================================================
# OPSLAAN
# ============================================================

st.write("")

if st.button(
    "💾 Tankbeurt opslaan",
    use_container_width=True,
    type="primary",
):

    if kilometerstand <= 0:

        st.error(
            "Vul een geldige kilometerstand in."
        )

    elif liters <= 0:

        st.error(
            "Vul het aantal liters in."
        )

    elif prijs_per_liter <= 0:

        st.error(
            "Vul de prijs per liter in."
        )

    else:

        try:

            data = {
                "user_id":
                    user.id,

                "datum":
                    datum.isoformat(),

                "kilometerstand":
                    kilometerstand,

                "liters":
                    liters,

                "prijs_per_liter":
                    prijs_per_liter,

                "totaalbedrag":
                    round(
                        totaalbedrag,
                        2
                    ),

                "tankstation":
                    tankstation.strip(),

                "volle_tank":
                    volle_tank,
            }


            (
                supabase
                .table("tankbeurten")
                .insert(data)
                .execute()
            )


            st.cache_data.clear()


            st.session_state["tank_saved"] = (
                f"Tankbeurt opgeslagen: "
                f"{liters:.2f} liter voor "
                f"€ {totaalbedrag:.2f}"
            )


            st.rerun()


        except Exception as e:

            st.error(
                "Opslaan is niet gelukt."
            )

            st.exception(e)


# ============================================================
# DATA OPHALEN
# ============================================================

st.divider()

st.subheader(
    "📊 Tankoverzicht"
)


try:

    response = (
        supabase
        .table("tankbeurten")
        .select("*")
        .eq(
            "user_id",
            user.id
        )
        .order(
            "datum",
            desc=True
        )
        .execute()
    )

    tankbeurten = response.data


    if tankbeurten:

        df = pd.DataFrame(
            tankbeurten
        )


        # ----------------------------------------------------
        # DATATYPES
        # ----------------------------------------------------

        df["datum"] = pd.to_datetime(
            df["datum"],
            errors="coerce"
        )

        df["liters"] = pd.to_numeric(
            df["liters"],
            errors="coerce"
        )

        df["prijs_per_liter"] = pd.to_numeric(
            df["prijs_per_liter"],
            errors="coerce"
        )

        df["totaalbedrag"] = pd.to_numeric(
            df["totaalbedrag"],
            errors="coerce"
        )

        df["kilometerstand"] = pd.to_numeric(
            df["kilometerstand"],
            errors="coerce"
        )


        # ====================================================
        # FILTER
        # ====================================================

        periode = st.selectbox(
            "Periode",
            [
                "Alles",
                "Deze maand",
                "Vorige maand",
                "Dit jaar",
            ],
            key="tank_periode",
        )


        vandaag = pd.Timestamp.today()

        df_filter = df.copy()


        if periode == "Deze maand":

            df_filter = df_filter[
                (df_filter["datum"].dt.year == vandaag.year)
                &
                (df_filter["datum"].dt.month == vandaag.month)
            ]


        elif periode == "Vorige maand":

            vorige = (
                vandaag
                - pd.DateOffset(
                    months=1
                )
            )

            df_filter = df_filter[
                (df_filter["datum"].dt.year == vorige.year)
                &
                (df_filter["datum"].dt.month == vorige.month)
            ]


        elif periode == "Dit jaar":

            df_filter = df_filter[
                df_filter["datum"].dt.year
                == vandaag.year
            ]


        # ====================================================
        # KPI'S
        # ====================================================

        totale_kosten = (
            df_filter[
                "totaalbedrag"
            ].sum()
        )

        totaal_liters = (
            df_filter[
                "liters"
            ].sum()
        )

        gem_prijs = (
            df_filter[
                "prijs_per_liter"
            ].mean()
        )


        k1, k2, k3 = (
            st.columns(3)
        )


        k1.metric(
            "Totale brandstofkosten",
            f"€ {totale_kosten:.2f}"
        )

        k2.metric(
            "Totaal liters",
            f"{totaal_liters:.1f} L"
        )

        k3.metric(
            "Gem. prijs per liter",
            (
                f"€ {gem_prijs:.3f}"
                if pd.notna(gem_prijs)
                else "-"
            )
        )


        # ====================================================
        # HISTORIE
        # ====================================================

        st.write("")

        st.subheader(
            "🧾 Tankhistorie"
        )


        if df_filter.empty:

            st.info(
                "Geen tankbeurten binnen deze periode."
            )

        else:

            overzicht = df_filter[
                [
                    "datum",
                    "kilometerstand",
                    "liters",
                    "prijs_per_liter",
                    "totaalbedrag",
                    "tankstation",
                    "volle_tank",
                ]
            ].copy()


            overzicht["datum"] = (
                overzicht["datum"]
                .dt.strftime(
                    "%d-%m-%Y"
                )
            )


            overzicht = overzicht.rename(
                columns={
                    "datum":
                        "Datum",

                    "kilometerstand":
                        "Kilometerstand",

                    "liters":
                        "Liters",

                    "prijs_per_liter":
                        "Prijs per liter",

                    "totaalbedrag":
                        "Totaalbedrag",

                    "tankstation":
                        "Tankstation",

                    "volle_tank":
                        "Volle tank",
                }
            )


            overzicht["Liters"] = (
                overzicht["Liters"]
                .apply(
                    lambda x:
                        f"{x:.2f}"
                )
            )


            overzicht[
                "Prijs per liter"
            ] = (
                overzicht[
                    "Prijs per liter"
                ]
                .apply(
                    lambda x:
                        f"€ {x:.3f}"
                )
            )


            overzicht[
                "Totaalbedrag"
            ] = (
                overzicht[
                    "Totaalbedrag"
                ]
                .apply(
                    lambda x:
                        f"€ {x:.2f}"
                )
            )


            st.dataframe(
                overzicht,
                use_container_width=True,
                hide_index=True,
            )


    else:

        st.info(
            "Nog geen tankbeurten opgeslagen."
        )


except Exception as e:

    st.error(
        "Tankhistorie kon niet worden geladen."
    )

    st.exception(e)