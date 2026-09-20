import streamlit as st


st.set_page_config(
    page_title="E-mail bevestigd",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Sidebar verbergen
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="collapsedControl"] {
        display: none;
    }

    .block-container {
        max-width: 620px;
        padding-top: 8rem;
        padding-bottom: 4rem;
    }

    div[data-testid="stButton"] > button {
        border-radius: 12px;
        height: 52px;
        font-size: 16px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Bovenruimte
st.write("")


# Icoon
st.markdown(
    """
    <div style="
        text-align:center;
        font-size:64px;
        margin-bottom:12px;
    ">
        ✅
    </div>
    """,
    unsafe_allow_html=True,
)


# Titel
st.markdown(
    """
    <h1 style="
        text-align:center;
        font-size:36px;
        margin-bottom:12px;
    ">
        E-mailadres bevestigd
    </h1>
    """,
    unsafe_allow_html=True,
)


# Tekst
st.markdown(
    """
    <p style="
        text-align:center;
        font-size:18px;
        color:#6b7280;
        line-height:1.6;
        margin-bottom:8px;
    ">
        Je AutoMaatje-account is succesvol geverifieerd.
    </p>

    <p style="
        text-align:center;
        font-size:17px;
        color:#6b7280;
        line-height:1.6;
        margin-bottom:32px;
    ">
        Je kunt nu inloggen en je ritten, tankbeurten
        en kilometervergoeding bijhouden.
    </p>
    """,
    unsafe_allow_html=True,
)


# Knop naar hoofdpagina
if st.button(
    "🚗 Naar AutoMaatje",
    use_container_width=True,
    type="primary",
):
    st.switch_page("App.py")