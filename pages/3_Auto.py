import streamlit as st
import pandas as pd

from datetime import date

from auth import require_login
from rdw import get_vehicle_by_plate
from ui_styles import apply_global_styles


# ============================================================
# PAGINA
# ============================================================

st.set_page_config(
    page_title="Mijn auto",
    page_icon="🚘",
    layout="wide",
)

apply_global_styles()

user, supabase = require_login()


# ============================================================
# HEADER
# ============================================================

st.title("🚘 Mijn auto")

st.caption(
    "Haal voertuiggegevens automatisch op bij de RDW "
    "en beheer je eigen autogegevens."
)


# ============================================================
# BESTAANDE AUTO OPHALEN
# ============================================================

try:

    response = (
        supabase
        .table("autos")
        .select("*")
        .eq(
            "user_id",
            user.id
        )
        .limit(1)
        .execute()
    )

    bestaande_auto = (
        response.data[0]
        if response.data
        else None
    )

except Exception as e:

    st.error(
        "Autogegevens konden niet worden geladen."
    )

    st.exception(e)

    bestaande_auto = None


# ============================================================
# KENTEKEN
# ============================================================

with st.container(
    border=True
):

    st.markdown(
        "#### 🔎 Kenteken opzoeken"
    )

    st.caption(
        "Voer je kenteken in. AutoMaatje haalt "
        "de voertuiggegevens automatisch bij de RDW op."
    )


    kenteken = st.text_input(
        "Kenteken",
        value=(
            bestaande_auto.get(
                "kenteken",
                ""
            )
            if bestaande_auto
            else ""
        ),
        placeholder="Bijvoorbeeld: 35-RV-VJ",
    )


    if st.button(
        "🔎 Gegevens ophalen bij RDW",
        use_container_width=True,
        type="primary",
    ):

        if not kenteken.strip():

            st.error(
                "Vul eerst een kenteken in."
            )

        else:

            with st.spinner(
                "RDW-gegevens ophalen..."
            ):

                rdw_auto = (
                    get_vehicle_by_plate(
                        kenteken
                    )
                )


            if rdw_auto:

                st.session_state[
                    "rdw_auto"
                ] = rdw_auto

                st.toast(
                    "Voertuig gevonden",
                    icon="✅"
                )

            else:

                st.error(
                    "Geen voertuig gevonden voor dit kenteken."
                )


# ============================================================
# RDW DATA
# ============================================================

rdw_auto = st.session_state.get(
    "rdw_auto"
)


if rdw_auto:

    st.write("")

    st.subheader(
        "Voertuiggegevens"
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    k1, k2, k3, k4 = st.columns(4)


    k1.metric(
        "Merk",
        rdw_auto.get(
            "merk"
        )
        or "-"
    )


    k2.metric(
        "Model",
        rdw_auto.get(
            "handelsbenaming"
        )
        or "-"
    )


    k3.metric(
        "Brandstof",
        rdw_auto.get(
            "brandstof"
        )
        or "-"
    )


    k4.metric(
        "Kleur",
        rdw_auto.get(
            "kleur"
        )
        or "-"
    )


    # ========================================================
    # RDW DETAILS
    # ========================================================

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 📋 RDW gegevens"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.text_input(
                "Voertuigsoort",
                value=(
                    rdw_auto.get(
                        "voertuigsoort"
                    )
                    or ""
                ),
                disabled=True,
            )


            st.text_input(
                "Datum eerste toelating",
                value=(
                    rdw_auto.get(
                        "datum_eerste_toelating"
                    )
                    or ""
                ),
                disabled=True,
            )


            st.text_input(
                "APK geldig tot",
                value=(
                    rdw_auto.get(
                        "vervaldatum_apk"
                    )
                    or ""
                ),
                disabled=True,
            )


        with col2:

            st.text_input(
                "Massa rijklaar",
                value=(
                    f"{rdw_auto.get('massa_rijklaar')} kg"
                    if rdw_auto.get(
                        "massa_rijklaar"
                    )
                    else ""
                ),
                disabled=True,
            )


            st.text_input(
                "Cilinderinhoud",
                value=(
                    f"{rdw_auto.get('cilinderinhoud')} cc"
                    if rdw_auto.get(
                        "cilinderinhoud"
                    )
                    else ""
                ),
                disabled=True,
            )


            st.text_input(
                "Aantal cilinders",
                value=(
                    str(
                        rdw_auto.get(
                            "aantal_cilinders"
                        )
                    )
                    if rdw_auto.get(
                        "aantal_cilinders"
                    )
                    else ""
                ),
                disabled=True,
            )

            vermogen_kw = rdw_auto.get("vermogen_kw")

            if vermogen_kw:
                vermogen_kw = float(vermogen_kw)
                vermogen_pk = vermogen_kw * 1.35962

                st.text_input(
                    "Vermogen",
                    value=f"{vermogen_kw:.0f} kW / {vermogen_pk:.0f} pk",
                    disabled=True,
                )
            else:
                st.text_input(
                    "Vermogen",
                    value="",
                    disabled=True,
                )
    # ========================================================
    # EIGEN GEGEVENS
    # ========================================================

    with st.container(
        border=True
    ):

        st.markdown(
            "#### ✏️ Mijn gegevens"
        )

        st.caption(
            "Deze gegevens komen niet van de RDW "
            "en worden alleen in AutoMaatje opgeslagen."
        )


        col3, col4 = st.columns(2)


        with col3:

            huidige_km = st.number_input(
                "Huidige kilometerstand",
                min_value=0,
                value=(
                    int(
                        bestaande_auto.get(
                            "huidige_kilometerstand",
                            0
                        )
                    )
                    if bestaande_auto
                    and bestaande_auto.get(
                        "huidige_kilometerstand"
                    )
                    else 0
                ),
                step=1,
            )


            aankoopdatum = st.date_input(
                "Aankoopdatum",
                value=(
                    pd.to_datetime(
                        bestaande_auto[
                            "aankoopdatum"
                        ]
                    ).date()
                    if bestaande_auto
                    and bestaande_auto.get(
                        "aankoopdatum"
                    )
                    else date.today()
                ),
            )


            aankoopprijs = st.number_input(
                "Aankoopprijs (€)",
                min_value=0.0,
                value=(
                    float(
                        bestaande_auto.get(
                            "aankoopprijs",
                            0
                        )
                    )
                    if bestaande_auto
                    and bestaande_auto.get(
                        "aankoopprijs"
                    )
                    else 0.0
                ),
                step=100.0,
            )


        with col4:

            verzekeraar = st.text_input(
                "Verzekeraar",
                value=(
                    bestaande_auto.get(
                        "verzekeraar",
                        ""
                    )
                    if bestaande_auto
                    else ""
                ),
            )


            verzekeringspremie = (
                st.number_input(
                    "Verzekeringspremie (€)",
                    min_value=0.0,
                    value=(
                        float(
                            bestaande_auto.get(
                                "verzekeringspremie",
                                0
                            )
                        )
                        if bestaande_auto
                        and bestaande_auto.get(
                            "verzekeringspremie"
                        )
                        else 0.0
                    ),
                    step=1.0,
                )
            )


        notities = st.text_area(
            "Notities",
            value=(
                bestaande_auto.get(
                    "notities",
                    ""
                )
                if bestaande_auto
                else ""
            ),
            placeholder=(
                "Bijvoorbeeld onderhoud, banden, "
                "bijzonderheden..."
            ),
        )


    # ========================================================
    # OPSLAAN
    # ========================================================

    if st.button(
        "💾 Auto opslaan",
        use_container_width=True,
        type="primary",
    ):

        try:

            data = {
                "user_id":
                    user.id,

                "kenteken":
                    rdw_auto.get(
                        "kenteken"
                    ),

                "merk":
                    rdw_auto.get(
                        "merk"
                    ),

                "vermogen_kw": (
                    float(rdw_auto.get("vermogen_kw"))
                    if rdw_auto.get("vermogen_kw")
                    else None
                ),

                "handelsbenaming":
                    rdw_auto.get(
                        "handelsbenaming"
                    ),

                "voertuigsoort":
                    rdw_auto.get(
                        "voertuigsoort"
                    ),

                "datum_eerste_toelating":
                    rdw_auto.get(
                        "datum_eerste_toelating"
                    ),

                "vervaldatum_apk":
                    rdw_auto.get(
                        "vervaldatum_apk"
                    ),

                "catalogusprijs":
                    rdw_auto.get(
                        "catalogusprijs"
                    ),

                "massa_ledig_voertuig":
                    rdw_auto.get(
                        "massa_ledig_voertuig"
                    ),

                "massa_rijklaar":
                    rdw_auto.get(
                        "massa_rijklaar"
                    ),

                "aantal_cilinders":
                    rdw_auto.get(
                        "aantal_cilinders"
                    ),

                "cilinderinhoud":
                    rdw_auto.get(
                        "cilinderinhoud"
                    ),

                "kleur":
                    rdw_auto.get(
                        "kleur"
                    ),

                "huidige_kilometerstand":
                    huidige_km,

                "aankoopdatum":
                    aankoopdatum.isoformat(),

                "aankoopprijs":
                    aankoopprijs,

                "verzekeraar":
                    verzekeraar.strip(),

                "verzekeringspremie":
                    verzekeringspremie,

                "notities":
                    notities.strip(),
            }


            if bestaande_auto:

                (
                    supabase
                    .table("autos")
                    .update(data)
                    .eq(
                        "id",
                        bestaande_auto[
                            "id"
                        ]
                    )
                    .execute()
                )

            else:

                (
                    supabase
                    .table("autos")
                    .insert(data)
                    .execute()
                )


            st.cache_data.clear()


            st.toast(
                "Autogegevens opgeslagen",
                icon="✅"
            )


            st.rerun()


        except Exception as e:

            st.error(
                "Autogegevens opslaan is niet gelukt."
            )

            st.exception(e)


# ============================================================
# BESTAANDE AUTO
# ============================================================

elif bestaande_auto:

    st.info(
        "Je hebt al een auto opgeslagen. "
        "Klik op 'Gegevens ophalen bij RDW' "
        "om de gegevens opnieuw te laden."
    )


else:

    st.info(
        "Voer hierboven een kenteken in "
        "om je auto toe te voegen."
    )