import streamlit as st
import pandas as pd
import plotly.express as px

from auth import require_login, logout
from ui_styles import apply_global_styles


# ============================================================
# PAGINA
# ============================================================

st.set_page_config(
    page_title="AutoMaatje",
    page_icon="🚗",
    layout="wide",
)

apply_global_styles()


# ============================================================
# EXTRA DASHBOARD STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* Dashboard iets smaller houden op grote schermen */
    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* KPI cards */
    div[data-testid="stMetric"] {
        padding: 20px 22px;

        border:
            1px solid rgba(128, 128, 128, 0.18);

        border-radius: 16px;

        background:
            rgba(255, 255, 255, 0.025);

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);

        box-shadow:
            0 8px 24px rgba(0, 0, 0, 0.07);

        border-color:
            rgba(128, 128, 128, 0.35);
    }


    /* Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
    }


    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border:
            1px solid rgba(128, 128, 128, 0.16);

        border-radius: 14px;

        overflow: hidden;
    }


    /* Buttons */
    div[data-testid="stButton"] > button {
        min-height: 42px;
        border-radius: 11px;
        font-weight: 600;
    }


    /* Mobiel */
    @media (max-width: 768px) {

        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
        }

        [data-testid="column"] {
            flex: 1 1 100% !important;
            width: 100% !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AUTH
# ============================================================

user, supabase = require_login()


# ============================================================
# DATA
# ============================================================

@st.cache_data(ttl=60)
def load_data(user_id):

    tank_response = (
        supabase
        .table("tankbeurten")
        .select("*")
        .eq(
            "user_id",
            user_id
        )
        .order(
            "datum",
            desc=True
        )
        .execute()
    )

    rit_response = (
        supabase
        .table("ritten")
        .select("*")
        .eq(
            "user_id",
            user_id
        )
        .order(
            "datum",
            desc=True
        )
        .execute()
    )

    tank_df = pd.DataFrame(
        tank_response.data
    )

    rit_df = pd.DataFrame(
        rit_response.data
    )

    return tank_df, rit_df


try:

    with st.spinner(
        "AutoMaatje laden..."
    ):

        tank_df, rit_df = load_data(
            user.id
        )

except Exception as e:

    st.error(
        "De gegevens konden niet "
        "uit Supabase worden geladen."
    )

    st.exception(e)

    st.stop()


# ============================================================
# RITTEN VOORBEREIDEN
# ============================================================

if not rit_df.empty:

    rit_df["datum"] = pd.to_datetime(
        rit_df["datum"],
        errors="coerce"
    )

    numerieke_rit_kolommen = [
        "kilometers",
        "vergoeding_per_km",
        "belastingvrij_per_km",
        "belastingpercentage",
    ]

    for kolom in numerieke_rit_kolommen:

        if kolom in rit_df.columns:

            rit_df[kolom] = pd.to_numeric(
                rit_df[kolom],
                errors="coerce"
            )


    zakelijke_df = rit_df[
        rit_df["type_rit"].isin(
            [
                "Zakelijk",
                "Woon-werk"
            ]
        )
    ].copy()


    if not zakelijke_df.empty:

        zakelijke_df["bruto_vergoeding"] = (
            zakelijke_df["kilometers"]
            * zakelijke_df["vergoeding_per_km"]
        )


        zakelijke_df["belastingvrij_bedrag"] = (
            zakelijke_df["kilometers"]
            * zakelijke_df[
                [
                    "vergoeding_per_km",
                    "belastingvrij_per_km",
                ]
            ].min(
                axis=1
            )
        )


        zakelijke_df["belast_bedrag"] = (
            zakelijke_df["bruto_vergoeding"]
            - zakelijke_df["belastingvrij_bedrag"]
        ).clip(
            lower=0
        )


        zakelijke_df["belasting"] = (
            zakelijke_df["belast_bedrag"]
            * (
                zakelijke_df["belastingpercentage"]
                / 100
            )
        )


        zakelijke_df["netto_vergoeding"] = (
            zakelijke_df["bruto_vergoeding"]
            - zakelijke_df["belasting"]
        )


else:

    zakelijke_df = pd.DataFrame()


# ============================================================
# TANKDATA VOORBEREIDEN
# ============================================================

if not tank_df.empty:

    tank_df["datum"] = pd.to_datetime(
        tank_df["datum"],
        errors="coerce"
    )

    numerieke_tank_kolommen = [
        "kilometerstand",
        "liters",
        "prijs_per_liter",
        "totaalbedrag",
    ]

    for kolom in numerieke_tank_kolommen:

        if kolom in tank_df.columns:

            tank_df[kolom] = pd.to_numeric(
                tank_df[kolom],
                errors="coerce"
            )


# ============================================================
# PERIODEFILTER
# ============================================================

vandaag = pd.Timestamp.today()

periode = st.session_state.get(
    "dashboard_periode",
    "Dit jaar"
)


def filter_periode(
    dataframe,
    gekozen_periode
):

    if dataframe.empty:
        return dataframe

    df = dataframe.copy()

    if "datum" not in df.columns:
        return df


    if gekozen_periode == "Deze maand":

        return df[
            (df["datum"].dt.year == vandaag.year)
            &
            (df["datum"].dt.month == vandaag.month)
        ]


    if gekozen_periode == "Vorige maand":

        vorige = (
            vandaag
            - pd.DateOffset(
                months=1
            )
        )

        return df[
            (df["datum"].dt.year == vorige.year)
            &
            (df["datum"].dt.month == vorige.month)
        ]


    if gekozen_periode == "Dit jaar":

        return df[
            df["datum"].dt.year
            == vandaag.year
        ]


    return df


# ============================================================
# HEADER
# ============================================================

header1, header2 = st.columns(
    [5, 1]
)


with header1:

    st.title(
        "🚗 AutoMaatje"
    )

    st.caption(
        "Je auto-administratie in één overzicht."
    )


with header2:

    st.write("")

    if st.button(
        "Uitloggen",
        use_container_width=True,
    ):

        logout()


# ============================================================
# SNELLE ACTIES
# ============================================================

st.markdown(
    "### Wat wil je doen?"
)


actie1, actie2 = st.columns(2)


with actie1:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 🛣️ Rit registreren"
        )

        st.caption(
            "Voeg een zakelijke, woon-werk- "
            "of privérit toe."
        )

        st.page_link(
            "pages/2_Ritten.py",
            label="Nieuwe rit",
            icon="➕",
            use_container_width=True,
        )


with actie2:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### ⛽ Tankbeurt registreren"
        )

        st.caption(
            "Houd liters, prijs en "
            "kilometerstand bij."
        )

        st.page_link(
            "pages/1_Tanken.py",
            label="Nieuwe tankbeurt",
            icon="➕",
            use_container_width=True,
        )


# ============================================================
# DASHBOARD FILTER
# ============================================================

st.write("")

filter_col1, filter_col2 = st.columns(
    [4, 1]
)


with filter_col1:

    st.markdown(
        "### 📊 Overzicht"
    )


with filter_col2:

    periode = st.selectbox(
        "Periode",
        [
            "Alles",
            "Deze maand",
            "Vorige maand",
            "Dit jaar",
        ],
        index=3,
        key="dashboard_periode",
    )


# ============================================================
# FILTER DATA
# ============================================================

zakelijke_filter = filter_periode(
    zakelijke_df,
    periode
)

tank_filter = filter_periode(
    tank_df,
    periode
)


# ============================================================
# KPI BEREKENINGEN
# ============================================================

if not zakelijke_filter.empty:

    totaal_km = (
        zakelijke_filter[
            "kilometers"
        ].sum()
    )

    totaal_netto = (
        zakelijke_filter[
            "netto_vergoeding"
        ].sum()
    )

    aantal_ritten = len(
        zakelijke_filter
    )

else:

    totaal_km = 0
    totaal_netto = 0
    aantal_ritten = 0


if not tank_filter.empty:

    totale_brandstofkosten = (
        tank_filter[
            "totaalbedrag"
        ].sum()
    )

    totaal_liters = (
        tank_filter[
            "liters"
        ].sum()
    )

else:

    totale_brandstofkosten = 0
    totaal_liters = 0


# ============================================================
# VERBRUIK
# ============================================================

gem_verbruik = None


if not tank_filter.empty:

    volle_tanks = tank_filter[
        tank_filter["volle_tank"] == True
    ].copy()


    volle_tanks = (
        volle_tanks
        .sort_values(
            "kilometerstand"
        )
    )


    if len(volle_tanks) >= 2:

        volle_tanks["gereden_km"] = (
            volle_tanks[
                "kilometerstand"
            ].diff()
        )


        volle_tanks["verbruik"] = (
            volle_tanks["liters"]
            / volle_tanks["gereden_km"]
            * 100
        )


        volle_tanks.loc[
            (
                volle_tanks[
                    "gereden_km"
                ] <= 0
            )
            |
            (
                volle_tanks[
                    "gereden_km"
                ].isna()
            ),
            "verbruik"
        ] = pd.NA


        gem_verbruik = (
            volle_tanks[
                "verbruik"
            ].mean()
        )


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(4)


k1.metric(
    "🛣️ Zakelijke kilometers",
    f"{totaal_km:,.0f} km",
    help=(
        "Zakelijke en woon-werkritten "
        "binnen de geselecteerde periode."
    ),
)


k2.metric(
    "💶 Geschat netto",
    f"€ {totaal_netto:,.2f}",
    help=(
        "Geschatte netto "
        "kilometervergoeding."
    ),
)


k3.metric(
    "⛽ Brandstofkosten",
    f"€ {totale_brandstofkosten:,.2f}",
)


k4.metric(
    "📉 Gem. verbruik",
    (
        f"{gem_verbruik:.2f} L/100 km"
        if pd.notna(gem_verbruik)
        else "-"
    ),
)


# ============================================================
# EXTRA SAMENVATTING
# ============================================================

st.write("")


samenvatting1, samenvatting2 = st.columns(2)


with samenvatting1:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 🚘 Ritten"
        )

        r1, r2 = st.columns(2)

        r1.metric(
            "Aantal",
            aantal_ritten
        )

        r2.metric(
            "Kilometers",
            f"{totaal_km:,.0f} km"
        )


with samenvatting2:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### ⛽ Brandstof"
        )

        b1, b2 = st.columns(2)

        b1.metric(
            "Getankt",
            f"{totaal_liters:.1f} L"
        )

        b2.metric(
            "Kosten",
            f"€ {totale_brandstofkosten:.2f}"
        )


# ============================================================
# ONTWIKKELING
# ============================================================

st.divider()

st.subheader(
    "📈 Ontwikkeling"
)

st.caption(
    "Bekijk hoe kilometers en brandstofkosten "
    "zich door de tijd ontwikkelen."
)


grafiek1, grafiek2 = st.columns(2)


# ============================================================
# KILOMETERS PER MAAND
# ============================================================

with grafiek1:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 🛣️ Kilometers per maand"
        )


        if not zakelijke_df.empty:

            rit_maand = (
                zakelijke_df
                .dropna(
                    subset=["datum"]
                )
                .copy()
            )


            rit_maand["Maand"] = (
                rit_maand["datum"]
                .dt.to_period("M")
                .astype(str)
            )


            km_per_maand = (
                rit_maand
                .groupby(
                    "Maand"
                )["kilometers"]
                .sum()
                .reset_index()
            )


            fig_km = px.bar(
                km_per_maand,
                x="Maand",
                y="kilometers",
                labels={
                    "kilometers":
                        "Kilometers",

                    "Maand":
                        "",
                },
            )


            fig_km.update_layout(
                height=300,

                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10,
                ),

                showlegend=False,

                xaxis_title=None,
            )


            fig_km.update_xaxes(
                showgrid=False
            )


            st.plotly_chart(
                fig_km,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


        else:

            st.info(
                "Voeg ritten toe om "
                "ontwikkeling te zien."
            )


# ============================================================
# BRANDSTOFKOSTEN PER MAAND
# ============================================================

with grafiek2:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### ⛽ Brandstofkosten per maand"
        )


        if not tank_df.empty:

            tank_maand = (
                tank_df
                .dropna(
                    subset=["datum"]
                )
                .copy()
            )


            tank_maand["Maand"] = (
                tank_maand["datum"]
                .dt.to_period("M")
                .astype(str)
            )


            kosten_per_maand = (
                tank_maand
                .groupby(
                    "Maand"
                )["totaalbedrag"]
                .sum()
                .reset_index()
            )


            fig_kosten = px.bar(
                kosten_per_maand,
                x="Maand",
                y="totaalbedrag",
                labels={
                    "totaalbedrag":
                        "Kosten (€)",

                    "Maand":
                        "",
                },
            )


            fig_kosten.update_layout(
                height=300,

                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10,
                ),

                showlegend=False,

                xaxis_title=None,
            )


            fig_kosten.update_xaxes(
                showgrid=False
            )


            st.plotly_chart(
                fig_kosten,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


        else:

            st.info(
                "Voeg tankbeurten toe "
                "om ontwikkeling te zien."
            )


# ============================================================
# RECENTE ACTIVITEIT
# ============================================================

st.divider()

st.subheader(
    "🕘 Recente activiteit"
)

st.caption(
    "Je laatst geregistreerde ritten en tankbeurten."
)


recent1, recent2 = st.columns(2)


# ============================================================
# LAATSTE RITTEN
# ============================================================

with recent1:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 🛣️ Laatste ritten"
        )


        if not rit_df.empty:

            recente_ritten = (
                rit_df
                .sort_values(
                    "datum",
                    ascending=False
                )
                .head(5)
                .copy()
            )


            recente_ritten = recente_ritten[
                [
                    "datum",
                    "van",
                    "naar",
                    "kilometers",
                    "type_rit",
                ]
            ]


            recente_ritten["datum"] = (
                recente_ritten["datum"]
                .dt.strftime(
                    "%d-%m-%Y"
                )
            )


            recente_ritten = (
                recente_ritten.rename(
                    columns={
                        "datum":
                            "Datum",

                        "van":
                            "Van",

                        "naar":
                            "Naar",

                        "kilometers":
                            "Km",

                        "type_rit":
                            "Type",
                    }
                )
            )


            st.dataframe(
                recente_ritten,
                use_container_width=True,
                hide_index=True,
            )


            st.page_link(
                "pages/2_Ritten.py",
                label="Alle ritten bekijken",
            )


        else:

            st.info(
                "Nog geen ritten geregistreerd."
            )


# ============================================================
# LAATSTE TANKBEURTEN
# ============================================================

with recent2:

    with st.container(
        border=True
    ):

        st.markdown(
            "#### ⛽ Laatste tankbeurten"
        )


        if not tank_df.empty:

            recente_tanks = (
                tank_df
                .sort_values(
                    "datum",
                    ascending=False
                )
                .head(5)
                .copy()
            )


            recente_tanks = recente_tanks[
                [
                    "datum",
                    "tankstation",
                    "liters",
                    "totaalbedrag",
                ]
            ]


            recente_tanks["datum"] = (
                recente_tanks["datum"]
                .dt.strftime(
                    "%d-%m-%Y"
                )
            )


            recente_tanks["liters"] = (
                recente_tanks["liters"]
                .apply(
                    lambda x:
                        f"{x:.1f} L"
                )
            )


            recente_tanks["totaalbedrag"] = (
                recente_tanks["totaalbedrag"]
                .apply(
                    lambda x:
                        f"€ {x:.2f}"
                )
            )


            recente_tanks = (
                recente_tanks.rename(
                    columns={
                        "datum":
                            "Datum",

                        "tankstation":
                            "Tankstation",

                        "liters":
                            "Liters",

                        "totaalbedrag":
                            "Bedrag",
                    }
                )
            )


            st.dataframe(
                recente_tanks,
                use_container_width=True,
                hide_index=True,
            )


            st.page_link(
                "pages/1_Tanken.py",
                label="Alle tankbeurten bekijken",
                use_container_width=True,
            )


        else:

            st.info(
                "Nog geen tankbeurten geregistreerd."
            )