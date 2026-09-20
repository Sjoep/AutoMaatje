import streamlit as st
from textwrap import dedent


st.set_page_config(
    page_title="E-mail bevestigd",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Zijbalk op deze pagina verbergen
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
        max-width: 720px;
        padding-top: 8rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Bevestigingskaart
st.markdown(
    dedent(
        """
        <div style="
            max-width: 580px;
            margin: 0 auto;
            padding: 48px 42px;
            border: 1px solid #e5e7eb;
            border-radius: 24px;
            background: white;
            text-align: center;
        ">

            <div style="
                width: 72px;
                height: 72px;
                margin: 0 auto 24px auto;
                border-radius: 50%;
                background: #ecfdf3;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 34px;
            ">
                ✓
            </div>

            <div style="
                font-size: 34px;
                font-weight: 700;
                margin-bottom: 14px;
                color: #111827;
            ">
                E-mailadres bevestigd
            </div>

            <div style="
                font-size: 17px;
                line-height: 1.6;
                color: #6b7280;
                margin-bottom: 10px;
            ">
                Je AutoMaatje-account is succesvol geverifieerd.
            </div>

            <div style="
                font-size: 17px;
                line-height: 1.6;
                color: #6b7280;
            ">
                Je kunt nu inloggen en je ritten, tankbeurten
                en kilometervergoeding bijhouden.
            </div>

        </div>
        """
    ),
    unsafe_allow_html=True,
)


st.write("")

st.page_link(
    "App.py",
    label="🚗 Naar AutoMaatje",
    use_container_width=True,
)