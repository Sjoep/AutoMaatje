import streamlit as st


st.set_page_config(
    page_title="E-mail bevestigd",
    page_icon="✅",
    layout="centered",
)

st.markdown(
    """
    <style>
        .verify-card {
            max-width: 560px;
            margin: 80px auto 0 auto;
            padding: 42px;
            border: 1px solid #e5e7eb;
            border-radius: 24px;
            text-align: center;
            background: white;
        }

        .verify-icon {
            font-size: 64px;
            margin-bottom: 16px;
        }

        .verify-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .verify-text {
            font-size: 17px;
            color: #6b7280;
            line-height: 1.6;
            margin-bottom: 28px;
        }
    </style>

    <div class="verify-card">

        <div class="verify-icon">
            ✅
        </div>

        <div class="verify-title">
            E-mailadres bevestigd
        </div>

        <div class="verify-text">
            Je account voor AutoMaatje is succesvol geverifieerd.
            Je kunt nu inloggen en je ritten en tankbeurten beheren.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)

st.page_link(
    "App.py",
    label="🚗 Naar AutoMaatje",
    use_container_width=True,
)