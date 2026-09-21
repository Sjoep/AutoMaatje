import streamlit as st


def apply_global_styles():
    """
    Centrale styling en subtiele animaties voor AutoMaatje.
    """

    st.markdown(
        """
        <style>

        /* ================================================
           PAGINA FADE-IN
           ================================================ */

        @keyframes pageFadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .block-container {
            animation: pageFadeIn 0.45s ease-out;
        }


        /* ================================================
           KPI / METRIC CARDS
           ================================================ */

        @keyframes metricEnter {
            from {
                opacity: 0;
                transform: translateY(8px) scale(0.98);
            }

            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 16px;
            padding: 18px;

            animation: metricEnter 0.45s ease-out;

            transition:
                transform 0.20s ease,
                box-shadow 0.20s ease,
                border-color 0.20s ease;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);

            box-shadow:
                0 8px 24px rgba(0, 0, 0, 0.08);

            border-color:
                rgba(128, 128, 128, 0.32);
        }


        /* ================================================
           KNOPPEN
           ================================================ */

        div[data-testid="stButton"] > button {
            border-radius: 12px;

            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease,
                opacity 0.18s ease;
        }

        div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px);

            box-shadow:
                0 6px 18px rgba(0, 0, 0, 0.10);
        }

        div[data-testid="stButton"] > button:active {
            transform: translateY(0);
        }


        /* ================================================
           DOWNLOAD BUTTONS
           ================================================ */

        div[data-testid="stDownloadButton"] > button {
            border-radius: 12px;

            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease;
        }

        div[data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-2px);

            box-shadow:
                0 6px 18px rgba(0, 0, 0, 0.10);
        }


        /* ================================================
           INPUT VELDEN
           ================================================ */

        div[data-baseweb="input"] {
            border-radius: 10px;
        }

        div[data-baseweb="select"] > div {
            border-radius: 10px;
        }


        /* ================================================
           DATAFRAME
           ================================================ */

        div[data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
        }


        /* ================================================
           ALERTS
           ================================================ */

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }


        /* ================================================
           TABS
           ================================================ */

        button[data-baseweb="tab"] {
            transition:
                opacity 0.2s ease,
                transform 0.2s ease;
        }

        button[data-baseweb="tab"]:hover {
            transform: translateY(-1px);
        }


        /* ================================================
           EXPANDERS
           ================================================ */

        div[data-testid="stExpander"] {
            border-radius: 12px;
            overflow: hidden;
        }


        /* ================================================
           ACCESSIBILITY
           Animaties uitschakelen wanneer gebruiker
           reduced motion heeft ingesteld
           ================================================ */

        @media (prefers-reduced-motion: reduce) {

            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def success_toast(message):
    """
    Kleine succesmelding rechtsboven.
    """

    st.toast(
        message,
        icon="✅",
    )


def error_toast(message):
    """
    Kleine foutmelding rechtsboven.
    """

    st.toast(
        message,
        icon="❌",
    )