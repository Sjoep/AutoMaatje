import streamlit as st

from auth import require_login
from ui_styles import apply_global_styles


# ============================================================
# PAGINA
# ============================================================

st.set_page_config(
    page_title="Instellingen",
    page_icon="⚙️",
    layout="wide",
)

apply_global_styles()

user, supabase = require_login()


# ============================================================
# HEADER
# ============================================================

st.title("⚙️ Instellingen")

st.caption(
    "Stel hier je standaardwaarden in voor AutoMaatje."
)


# ============================================================
# INSTELLINGEN OPHALEN
# ============================================================

try:

    response = (
        supabase
        .table("instellingen")
        .select("*")
        .eq("user_id", user.id)
        .limit(1)
        .execute()
    )

    instellingen = (
        response.data[0]
        if response.data
        else None
    )

except Exception as e:

    st.error(
        "Instellingen konden niet worden geladen."
    )

    st.exception(e)

    instellingen = None


# ============================================================
# STANDAARDWAARDEN
# ============================================================

kilometervergoeding_default = (
    float(instellingen["kilometervergoeding"])
    if instellingen
    and instellingen.get("kilometervergoeding") is not None
    else 0.31
)

belastingvrij_default = (
    float(instellingen["belastingvrij_per_km"])
    if instellingen
    and instellingen.get("belastingvrij_per_km") is not None
    else 0.25
)

belastingpercentage_default = (
    float(instellingen["belastingpercentage"])
    if instellingen
    and instellingen.get("belastingpercentage") is not None
    else 35.75
)

standaard_type_rit_default = (
    instellingen.get(
        "standaard_type_rit",
        "Woon-werk"
    )
    if instellingen
    else "Woon-werk"
)

standaard_retourrit_default = (
    instellingen.get(
        "standaard_retourrit",
        True
    )
    if instellingen
    else True
)

standaard_tankstation_default = (
    instellingen.get(
        "standaard_tankstation",
        ""
    )
    if instellingen
    else ""
)


# ============================================================
# RITINSTELLINGEN
# ============================================================

with st.container(border=True):

    st.markdown("#### 🛣️ Ritten")

    st.caption(
        "Deze waarden worden straks automatisch "
        "gebruikt bij het invoeren van een nieuwe rit."
    )

    col1, col2 = st.columns(2)

    with col1:

        kilometervergoeding = st.number_input(
            "Kilometervergoeding werkgever (€ / km)",
            min_value=0.0,
            value=kilometervergoeding_default,
            step=0.01,
            format="%.2f",
        )

        belastingvrij_per_km = st.number_input(
            "Belastingvrij bedrag (€ / km)",
            min_value=0.0,
            value=belastingvrij_default,
            step=0.01,
            format="%.2f",
        )

        belastingpercentage = st.number_input(
            "Belastingpercentage belast deel (%)",
            min_value=0.0,
            max_value=100.0,
            value=belastingpercentage_default,
            step=0.25,
            format="%.2f",
        )

    with col2:

        type_opties = [
            "Zakelijk",
            "Woon-werk",
            "Privé",
        ]

        try:
            type_index = type_opties.index(
                standaard_type_rit_default
            )
        except ValueError:
            type_index = 1

        standaard_type_rit = st.selectbox(
            "Standaard type rit",
            options=type_opties,
            index=type_index,
        )

        standaard_retourrit = st.toggle(
            "Standaard retourrit",
            value=standaard_retourrit_default,
        )


# ============================================================
# TANKINSTELLINGEN
# ============================================================

with st.container(border=True):

    st.markdown("#### ⛽ Tanken")

    st.caption(
        "Stel standaardwaarden in voor tankbeurten."
    )

    standaard_tankstation = st.text_input(
        "Standaard tankstation",
        value=standaard_tankstation_default,
        placeholder="Bijvoorbeeld Shell, BP of Tango",
    )


# ============================================================
# ACCOUNT
# ============================================================

with st.container(border=True):

    st.markdown("#### 👤 Account")

    st.text_input(
        "E-mailadres",
        value=user.email or "",
        disabled=True,
    )

    st.caption(
        "Je accountgegevens worden beheerd via Supabase Auth."
    )


# ============================================================
# OPSLAAN
# ============================================================

if st.button(
    "💾 Instellingen opslaan",
    type="primary",
    use_container_width=True,
):

    try:

        data = {
            "user_id":
                user.id,

            "kilometervergoeding":
                kilometervergoeding,

            "belastingvrij_per_km":
                belastingvrij_per_km,

            "belastingpercentage":
                belastingpercentage,

            "standaard_type_rit":
                standaard_type_rit,

            "standaard_retourrit":
                standaard_retourrit,

            "standaard_tankstation":
                standaard_tankstation.strip()
                if standaard_tankstation
                else None,
        }


        if instellingen:

            (
                supabase
                .table("instellingen")
                .update(data)
                .eq("id", instellingen["id"])
                .execute()
            )

        else:

            (
                supabase
                .table("instellingen")
                .insert(data)
                .execute()
            )


        st.cache_data.clear()

        st.session_state[
            "instellingen_saved"
        ] = True

        st.rerun()


    except Exception as e:

        st.error(
            "Instellingen opslaan is niet gelukt."
        )

        st.exception(e)


# ============================================================
# TOAST
# ============================================================

if st.session_state.get(
    "instellingen_saved"
):

    st.toast(
        "Instellingen opgeslagen",
        icon="✅",
    )

    del st.session_state[
        "instellingen_saved"
    ]