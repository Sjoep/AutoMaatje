import streamlit as st
import pandas as pd

from datetime import date, timedelta
from auth import require_login


# ============================================================
# PAGINA
# ============================================================

st.set_page_config(
    page_title="Ritten",
    page_icon="🛣️",
    layout="wide",
)


# ============================================================
# UX / UI
# ============================================================

st.markdown(
    """
    <style>

    /* ─────────────────────────────────────────────
       Pagina animatie
       ───────────────────────────────────────────── */

    @keyframes pageFade {
        from {
            opacity: 0;
            transform: translateY(8px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 4rem;

        animation:
            pageFade 0.35s ease-out;
    }


    /* ─────────────────────────────────────────────
       KPI cards
       ───────────────────────────────────────────── */

    div[data-testid="stMetric"] {
        padding: 18px 20px;

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
        transform:
            translateY(-2px);

        box-shadow:
            0 8px 24px rgba(0, 0, 0, 0.07);

        border-color:
            rgba(128, 128, 128, 0.35);
    }


    /* ─────────────────────────────────────────────
       Buttons
       ───────────────────────────────────────────── */

    div[data-testid="stButton"] > button {
        min-height: 46px;

        border-radius: 12px;

        font-weight: 600;

        transition:
            transform 0.16s ease,
            box-shadow 0.16s ease;
    }

    div[data-testid="stButton"] > button:hover {
        transform:
            translateY(-1px);

        box-shadow:
            0 6px 16px rgba(0, 0, 0, 0.10);
    }

    div[data-testid="stButton"] > button:active {
        transform:
            translateY(0);
    }


    /* ─────────────────────────────────────────────
       Inputvelden
       ───────────────────────────────────────────── */

    div[data-baseweb="input"] > div {
        border-radius: 11px !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: 11px !important;
    }


    /* ─────────────────────────────────────────────
       Tabellen
       ───────────────────────────────────────────── */

    div[data-testid="stDataFrame"] {
        border:
            1px solid rgba(128, 128, 128, 0.16);

        border-radius: 14px;

        overflow: hidden;
    }


    /* ─────────────────────────────────────────────
       Expanders
       ───────────────────────────────────────────── */

    div[data-testid="stExpander"] {
        border-radius: 14px;
        overflow: hidden;
    }


    /* ─────────────────────────────────────────────
       Tabs
       ───────────────────────────────────────────── */

    button[data-baseweb="tab"] {
        font-weight: 600;

        padding-left: 1rem;
        padding-right: 1rem;
    }


    /* ─────────────────────────────────────────────
       Mobiel
       ───────────────────────────────────────────── */

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


    /* ─────────────────────────────────────────────
       Reduced motion
       ───────────────────────────────────────────── */

    @media (prefers-reduced-motion: reduce) {

        *,
        *::before,
        *::after {
            animation-duration:
                0.01ms !important;

            transition-duration:
                0.01ms !important;
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
# GEBRUIKERSINSTELLINGEN OPHALEN
# ============================================================

def load_instellingen(user_id):
    try:
        response = (
            supabase
            .table("instellingen")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception:
        pass

    # Fallback als gebruiker nog geen instellingen heeft opgeslagen
    return {
        "kilometervergoeding": 0.31,
        "belastingvrij_per_km": 0.25,
        "belastingpercentage": 35.75,
        "standaard_type_rit": "Woon-werk",
        "standaard_retourrit": True,
    }


instellingen = load_instellingen(user.id)


DEFAULT_KILOMETERVERGOEDING = float(
    instellingen.get("kilometervergoeding") or 0.31
)

DEFAULT_BELASTINGVRIJ = float(
    instellingen.get("belastingvrij_per_km") or 0.25
)

DEFAULT_BELASTINGPERCENTAGE = float(
    instellingen.get("belastingpercentage") or 35.75
)

DEFAULT_TYPE_RIT = instellingen.get(
    "standaard_type_rit"
) or "Woon-werk"

DEFAULT_RETOURRIT = instellingen.get(
    "standaard_retourrit"
)

if DEFAULT_RETOURRIT is None:
    DEFAULT_RETOURRIT = True
# ============================================================
# HEADER
# ============================================================

st.title("🛣️ Ritten")

st.caption(
    "Registreer je ritten, bereken je kilometervergoeding "
    "en houd zakelijk en privé gescheiden."
)


# ============================================================
# HELPERS
# ============================================================

@st.cache_data(ttl=30)
def load_ritten(user_id):

    response = (
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

    df = pd.DataFrame(
        response.data
    )

    if df.empty:
        return df


    # Datum
    df["datum"] = pd.to_datetime(
        df["datum"],
        errors="coerce"
    )


    # Numerieke velden
    numerieke_kolommen = [
        "kilometers",
        "vergoeding_per_km",
        "belastingvrij_per_km",
        "belastingpercentage",
    ]

    for kolom in numerieke_kolommen:

        if kolom in df.columns:

            df[kolom] = pd.to_numeric(
                df[kolom],
                errors="coerce"
            )


    # Bruto vergoeding
    df["bruto_vergoeding"] = (
        df["kilometers"]
        * df["vergoeding_per_km"]
    )


    # Belastingvrij
    df["belastingvrij_bedrag"] = (
        df["kilometers"]
        * df[
            [
                "vergoeding_per_km",
                "belastingvrij_per_km"
            ]
        ].min(
            axis=1
        )
    )


    # Belast gedeelte
    df["belast_bedrag"] = (
        df["bruto_vergoeding"]
        - df["belastingvrij_bedrag"]
    ).clip(
        lower=0
    )


    # Belasting
    df["belasting"] = (
        df["belast_bedrag"]
        * (
            df["belastingpercentage"]
            / 100
        )
    )


    # Netto
    df["netto_vergoeding"] = (
        df["bruto_vergoeding"]
        - df["belasting"]
    )


    # Privé = geen vergoeding
    prive_mask = (
        df["type_rit"]
        == "Privé"
    )

    df.loc[
        prive_mask,
        [
            "bruto_vergoeding",
            "belastingvrij_bedrag",
            "belast_bedrag",
            "belasting",
            "netto_vergoeding",
        ],
    ] = 0


    return df


def get_opgeslagen_locaties(df):

    if df.empty:
        return []

    locaties = set()

    for kolom in [
        "van",
        "naar"
    ]:

        if kolom in df.columns:

            for locatie in (
                df[kolom]
                .dropna()
            ):

                locatie = (
                    str(locatie)
                    .strip()
                )

                if locatie:
                    locaties.add(
                        locatie
                    )

    return sorted(
        locaties,
        key=str.lower
    )


def filter_periode(
    dataframe,
    periode
):

    if dataframe.empty:
        return dataframe

    vandaag = pd.Timestamp.today()

    df = dataframe.copy()


    if periode == "Deze maand":

        return df[
            (df["datum"].dt.year == vandaag.year)
            &
            (df["datum"].dt.month == vandaag.month)
        ]


    if periode == "Vorige maand":

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


    if periode == "Dit jaar":

        return df[
            df["datum"].dt.year
            == vandaag.year
        ]


    return df


def format_overzicht(
    df,
    inclusief_vergoeding=True
):

    if inclusief_vergoeding:

        kolommen = [
            "datum",
            "van",
            "naar",
            "omschrijving",
            "type_rit",
            "kilometers",
            "vergoeding_per_km",
            "bruto_vergoeding",
            "netto_vergoeding",
        ]

    else:

        kolommen = [
            "datum",
            "van",
            "naar",
            "omschrijving",
            "kilometers",
        ]


    overzicht = (
        df[kolommen]
        .copy()
    )


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

            "van":
                "Van",

            "naar":
                "Naar",

            "omschrijving":
                "Omschrijving",

            "type_rit":
                "Type",

            "kilometers":
                "Kilometers",

            "vergoeding_per_km":
                "€/km",

            "bruto_vergoeding":
                "Bruto",

            "netto_vergoeding":
                "Netto",
        }
    )


    if inclusief_vergoeding:

        overzicht["€/km"] = (
            overzicht["€/km"]
            .apply(
                lambda x:
                    f"€ {x:.3f}"
                    if pd.notna(x)
                    else "-"
            )
        )


        overzicht["Bruto"] = (
            overzicht["Bruto"]
            .apply(
                lambda x:
                    f"€ {x:.2f}"
            )
        )


        overzicht["Netto"] = (
            overzicht["Netto"]
            .apply(
                lambda x:
                    f"€ {x:.2f}"
            )
        )


    return overzicht


def verwijder_rit(
    dataframe,
    key_prefix
):

    if dataframe.empty:
        return


    with st.expander(
        "⚠️ Gevarenzone"
    ):

        st.caption(
            "Verwijder hier een opgeslagen rit. "
            "Deze actie kan niet ongedaan worden gemaakt."
        )


        rit_opties = {}


        for _, row in (
            dataframe.iterrows()
        ):

            datum_text = (
                row["datum"]
                .strftime(
                    "%d-%m-%Y"
                )
                if pd.notna(
                    row["datum"]
                )
                else
                "Onbekende datum"
            )


            label = (
                f"{datum_text} · "
                f"{row['van']} → "
                f"{row['naar']} · "
                f"{row['kilometers']:.1f} km"
            )


            rit_opties[
                label
            ] = row["id"]


        geselecteerde_rit = (
            st.selectbox(
                "Selecteer rit",
                options=list(
                    rit_opties.keys()
                ),
                index=None,
                placeholder=(
                    "Kies een rit..."
                ),
                key=(
                    f"{key_prefix}_select"
                ),
            )
        )


        if (
            geselecteerde_rit
            is not None
        ):

            verwijder_id = (
                rit_opties[
                    geselecteerde_rit
                ]
            )


            bevestigen = (
                st.checkbox(
                    "Ik weet zeker dat "
                    "ik deze rit wil verwijderen",
                    key=(
                        f"{key_prefix}_confirm"
                    ),
                )
            )


            if st.button(
                "🗑️ Rit verwijderen",
                disabled=not bevestigen,
                key=(
                    f"{key_prefix}_button"
                ),
                use_container_width=True,
            ):

                try:

                    (
                        supabase
                        .table("ritten")
                        .delete()
                        .eq(
                            "id",
                            verwijder_id
                        )
                        .execute()
                    )


                    st.cache_data.clear()


                    st.toast(
                        "Rit verwijderd",
                        icon="🗑️"
                    )


                    st.rerun()


                except Exception as e:

                    st.error(
                        "Rit verwijderen "
                        "is niet gelukt."
                    )

                    st.exception(e)


# ============================================================
# DATA
# ============================================================

try:

    with st.spinner(
        "Ritten laden..."
    ):

        ritten_df = load_ritten(
            user.id
        )


except Exception as e:

    st.error(
        "Ritten konden niet "
        "uit Supabase worden geladen."
    )

    st.exception(e)

    ritten_df = (
        pd.DataFrame()
    )


opgeslagen_locaties = (
    get_opgeslagen_locaties(
        ritten_df
    )
)


# ============================================================
# TABS
# ============================================================

tab_nieuw, tab_zakelijk, tab_prive = (
    st.tabs(
        [
            "➕ Nieuwe rit",
            "💼 Zakelijk",
            "🏠 Privé",
        ]
    )
)


# ============================================================
# TAB 1 — NIEUWE RIT
# ============================================================

with tab_nieuw:

    st.subheader(
        "Nieuwe rit"
    )

    st.caption(
        "Voer één rit in of voeg dezelfde "
        "rit direct voor meerdere dagen toe."
    )


    # ========================================================
    # 1. DATUM
    # ========================================================

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 📅 Wanneer?"
        )


        invoer_type = st.radio(
            "Rit invoeren voor",
            [
                "Eén dag",
                "Meerdere dagen"
            ],
            horizontal=True,
            label_visibility="collapsed",
        )


        if invoer_type == "Eén dag":

            geselecteerde_datums = [
                st.date_input(
                    "Datum",
                    value=date.today(),
                    key="enkele_datum",
                )
            ]


        else:

            datum1, datum2 = (
                st.columns(2)
            )


            with datum1:

                datum_van = (
                    st.date_input(
                        "Van datum",
                        value=date.today(),
                        key="datum_van",
                    )
                )


            with datum2:

                datum_tot = (
                    st.date_input(
                        "Tot datum",
                        value=date.today(),
                        key="datum_tot",
                    )
                )


            weekdagen = (
                st.multiselect(
                    "Welke dagen?",
                    [
                        "Maandag",
                        "Dinsdag",
                        "Woensdag",
                        "Donderdag",
                        "Vrijdag",
                        "Zaterdag",
                        "Zondag",
                    ],
                    default=[
                        "Maandag",
                        "Dinsdag",
                        "Woensdag",
                        "Donderdag",
                        "Vrijdag",
                    ],
                )
            )


            dag_mapping = {
                "Maandag": 0,
                "Dinsdag": 1,
                "Woensdag": 2,
                "Donderdag": 3,
                "Vrijdag": 4,
                "Zaterdag": 5,
                "Zondag": 6,
            }


            gekozen_dagen = [
                dag_mapping[
                    dag
                ]
                for dag
                in weekdagen
            ]


            geselecteerde_datums = []


            if (
                datum_tot
                >= datum_van
            ):

                huidige = (
                    datum_van
                )


                while (
                    huidige
                    <= datum_tot
                ):

                    if (
                        huidige.weekday()
                        in gekozen_dagen
                    ):

                        geselecteerde_datums.append(
                            huidige
                        )


                    huidige += timedelta(
                        days=1
                    )


            if (
                datum_tot
                < datum_van
            ):

                st.warning(
                    "De einddatum ligt "
                    "vóór de begindatum."
                )


            elif not weekdagen:

                st.warning(
                    "Selecteer minimaal "
                    "één weekdag."
                )


            elif geselecteerde_datums:

                st.success(
                    f"{len(geselecteerde_datums)} "
                    f"dagen geselecteerd."
                )


                with st.expander(
                    "Geselecteerde datums bekijken"
                ):

                    for datum_item in (
                        geselecteerde_datums
                    ):

                        st.write(
                            datum_item.strftime(
                                "%d-%m-%Y"
                            )
                        )


    # ========================================================
    # 2. ROUTE
    # ========================================================

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 📍 Route"
        )


        col1, col2 = (
            st.columns(2)
        )


        # ----------------------------------------------------
        # VAN
        # ----------------------------------------------------

        with col1:

            van_keuze = (
                st.selectbox(
                    "Van",
                    options=[
                        "Nieuwe locatie..."
                    ]
                    + opgeslagen_locaties,
                    index=None,
                    placeholder=(
                        "Kies vertrekpunt..."
                    ),
                    key="van_keuze",
                )
            )


            if (
                van_keuze
                == "Nieuwe locatie..."
            ):

                van = (
                    st.text_input(
                        "Nieuwe vertreklocatie",
                        placeholder=(
                            "Bijvoorbeeld: Hoorn"
                        ),
                        key="van_nieuw",
                    )
                )


            else:

                van = (
                    van_keuze
                    or ""
                )


        # ----------------------------------------------------
        # NAAR
        # ----------------------------------------------------

        with col2:

            naar_keuze = (
                st.selectbox(
                    "Naar",
                    options=[
                        "Nieuwe locatie..."
                    ]
                    + opgeslagen_locaties,
                    index=None,
                    placeholder=(
                        "Kies bestemming..."
                    ),
                    key="naar_keuze",
                )
            )


            if (
                naar_keuze
                == "Nieuwe locatie..."
            ):

                naar = (
                    st.text_input(
                        "Nieuwe bestemming",
                        placeholder=(
                            "Bijvoorbeeld: Amsterdam"
                        ),
                        key="naar_nieuw",
                    )
                )


            else:

                naar = (
                    naar_keuze
                    or ""
                )


        omschrijving = (
            st.text_input(
                "Omschrijving",
                placeholder=(
                    "Bijvoorbeeld: kantoor, "
                    "klantbezoek of project"
                ),
            )
        )


        rit1, rit2 = (
            st.columns(2)
        )


        with rit1:

            type_rit = (
                st.selectbox(
                    "Type rit",
                    [
                        "Zakelijk",
                        "Woon-werk",
                        "Privé",
                    ],
                )
            )


        with rit2:

            enkele_km = (
                st.number_input(
                    "Afstand enkele reis (km)",
                    min_value=0.0,
                    step=1.0,
                    format="%.1f",
                )
            )


        retourrit = st.toggle(
            "Retourrit",
            value=True,
        )


    # ========================================================
    # KILOMETERS
    # ========================================================

    if retourrit:

        km_per_rit = (
            enkele_km
            * 2
        )

    else:

        km_per_rit = (
            enkele_km
        )


    aantal_ritten = len(
        geselecteerde_datums
    )


    totaal_km = (
        km_per_rit
        * aantal_ritten
    )


    # ========================================================
    # 3. VERGOEDING
    # ========================================================

    with st.container(
        border=True
    ):

        st.markdown(
            "#### 💶 Vergoeding"
        )


        if type_rit in [
            "Zakelijk",
            "Woon-werk"
        ]:

            vergoeding1, vergoeding2 = (
                st.columns(2)
            )


            with vergoeding1:

                vergoeding_per_km = (
                    st.number_input(
                        "Vergoeding werkgever (€ / km)",
                        min_value=0.0,
                        value=DEFAULT_KILOMETERVERGOEDING,
                        step=0.01,
                        format="%.3f",
                    )
                )


            with vergoeding2:

                belastingvrij_per_km = (
                    st.number_input(
                        "Belastingvrij (€ / km)",
                        min_value=0.0,
                        value=DEFAULT_BELASTINGVRIJ,
                        step=0.01,
                        format="%.3f",
                    )
                )


            belastingpercentage = (
                st.number_input(
                    "Belastingpercentage belast deel (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=DEFAULT_BELASTINGPERCENTAGE,
                    step=0.1,
                    format="%.2f",
                )
            )


            bruto_per_rit = (
                km_per_rit
                * vergoeding_per_km
            )


            belastingvrij_per_rit = (
                km_per_rit
                * min(
                    vergoeding_per_km,
                    belastingvrij_per_km
                )
            )


            belast_per_rit = max(
                bruto_per_rit
                - belastingvrij_per_rit,
                0
            )


            belasting_per_rit = (
                belast_per_rit
                * (
                    belastingpercentage
                    / 100
                )
            )


            netto_per_rit = (
                bruto_per_rit
                - belasting_per_rit
            )


        else:

            vergoeding_per_km = 0
            belastingvrij_per_km = 0
            belastingpercentage = 0

            bruto_per_rit = 0
            netto_per_rit = 0


            st.info(
                "Voor een privérit wordt "
                "geen kilometervergoeding berekend."
            )


    # ========================================================
    # 4. SAMENVATTING
    # ========================================================

    bruto_totaal = (
        bruto_per_rit
        * aantal_ritten
    )


    netto_totaal = (
        netto_per_rit
        * aantal_ritten
    )


    st.markdown(
        "### Samenvatting"
    )


    k1, k2, k3, k4 = (
        st.columns(4)
    )


    k1.metric(
        "Aantal ritten",
        aantal_ritten
    )


    k2.metric(
        "Totaal",
        f"{totaal_km:.1f} km"
    )


    k3.metric(
        "Bruto",
        f"€ {bruto_totaal:.2f}"
    )


    k4.metric(
        "Geschat netto",
        f"€ {netto_totaal:.2f}"
    )


    if (
        enkele_km > 0
        and retourrit
    ):

        st.caption(
            f"{enkele_km:.1f} km heen + "
            f"{enkele_km:.1f} km terug = "
            f"{km_per_rit:.1f} km per rit."
        )


    # ========================================================
    # OPSLAAN
    # ========================================================

    st.write("")


    if st.button(
        "💾 Rit opslaan",
        use_container_width=True,
        type="primary",
    ):

        if not geselecteerde_datums:

            st.error(
                "Selecteer minimaal "
                "één datum."
            )


        elif not van.strip():

            st.error(
                "Selecteer of vul "
                "een vertrekpunt in."
            )


        elif not naar.strip():

            st.error(
                "Selecteer of vul "
                "een bestemming in."
            )


        elif (
            van.strip().lower()
            == naar.strip().lower()
        ):

            st.error(
                "Vertrekpunt en bestemming "
                "kunnen niet hetzelfde zijn."
            )


        elif km_per_rit <= 0:

            st.error(
                "Vul een geldige afstand in."
            )


        else:

            try:

                records = []


                for rit_datum in (
                    geselecteerde_datums
                ):

                    records.append(
                        {
                            "user_id":
                                user.id,

                            "datum":
                                rit_datum.isoformat(),

                            "van":
                                van.strip(),

                            "naar":
                                naar.strip(),

                            "omschrijving":
                                omschrijving.strip(),

                            "kilometers":
                                km_per_rit,

                            "type_rit":
                                type_rit,

                            "vergoeding_per_km":
                                vergoeding_per_km,

                            "belastingvrij_per_km":
                                belastingvrij_per_km,

                            "belastingpercentage":
                                belastingpercentage,
                        }
                    )


                (
                    supabase
                    .table("ritten")
                    .insert(records)
                    .execute()
                )


                st.cache_data.clear()


                st.toast(
                    (
                        f"{len(records)} rit"
                        f"{'ten' if len(records) != 1 else ''} "
                        f"opgeslagen"
                    ),
                    icon="✅"
                )


                st.rerun()


            except Exception as e:

                st.error(
                    "Opslaan is niet gelukt."
                )

                st.exception(e)


# ============================================================
# TAB 2 — ZAKELIJK
# ============================================================

with tab_zakelijk:

    st.subheader(
        "💼 Zakelijke ritten"
    )

    st.caption(
        "Zakelijke en woon-werkritten "
        "inclusief kilometervergoeding."
    )


    if ritten_df.empty:

        st.info(
            "Nog geen zakelijke ritten."
        )


    else:

        zakelijke_df = ritten_df[
            ritten_df[
                "type_rit"
            ].isin(
                [
                    "Zakelijk",
                    "Woon-werk"
                ]
            )
        ].copy()


        if zakelijke_df.empty:

            st.info(
                "Nog geen zakelijke "
                "of woon-werkritten."
            )


        else:

            filter1, filter2 = (
                st.columns(2)
            )


            with filter1:

                periode = (
                    st.selectbox(
                        "Periode",
                        [
                            "Alles",
                            "Deze maand",
                            "Vorige maand",
                            "Dit jaar",
                        ],
                        key="zakelijk_periode",
                    )
                )


            with filter2:

                types = (
                    st.multiselect(
                        "Type",
                        [
                            "Zakelijk",
                            "Woon-werk",
                        ],
                        default=[
                            "Zakelijk",
                            "Woon-werk",
                        ],
                        key="zakelijk_type",
                    )
                )


            zakelijk_filter = (
                zakelijke_df[
                    zakelijke_df[
                        "type_rit"
                    ].isin(types)
                ]
                .copy()
            )


            zakelijk_filter = (
                filter_periode(
                    zakelijk_filter,
                    periode
                )
            )


            if zakelijk_filter.empty:

                st.info(
                    "Geen ritten binnen "
                    "de geselecteerde filters."
                )


            else:

                totaal_km_zakelijk = (
                    zakelijk_filter[
                        "kilometers"
                    ].sum()
                )


                totaal_bruto = (
                    zakelijk_filter[
                        "bruto_vergoeding"
                    ].sum()
                )


                totaal_netto = (
                    zakelijk_filter[
                        "netto_vergoeding"
                    ].sum()
                )


                aantal = len(
                    zakelijk_filter
                )


                z1, z2, z3, z4 = (
                    st.columns(4)
                )


                z1.metric(
                    "Ritten",
                    aantal
                )


                z2.metric(
                    "Kilometers",
                    f"{totaal_km_zakelijk:.1f} km"
                )


                z3.metric(
                    "Bruto",
                    f"€ {totaal_bruto:.2f}"
                )


                z4.metric(
                    "Netto",
                    f"€ {totaal_netto:.2f}"
                )


                st.write("")


                overzicht = (
                    format_overzicht(
                        zakelijk_filter,
                        inclusief_vergoeding=True,
                    )
                )


                st.dataframe(
                    overzicht,
                    use_container_width=True,
                    hide_index=True,
                )


                verwijder_rit(
                    zakelijk_filter,
                    "delete_zakelijk"
                )


# ============================================================
# TAB 3 — PRIVÉ
# ============================================================

with tab_prive:

    st.subheader(
        "🏠 Privéritten"
    )

    st.caption(
        "Overzicht van je privé gereden kilometers."
    )


    if ritten_df.empty:

        st.info(
            "Nog geen privéritten."
        )


    else:

        prive_df = ritten_df[
            ritten_df[
                "type_rit"
            ]
            == "Privé"
        ].copy()


        if prive_df.empty:

            st.info(
                "Nog geen privéritten."
            )


        else:

            periode_prive = (
                st.selectbox(
                    "Periode",
                    [
                        "Alles",
                        "Deze maand",
                        "Vorige maand",
                        "Dit jaar",
                    ],
                    key="prive_periode",
                )
            )


            prive_filter = (
                filter_periode(
                    prive_df,
                    periode_prive
                )
            )


            if prive_filter.empty:

                st.info(
                    "Geen privéritten binnen "
                    "de geselecteerde periode."
                )


            else:

                aantal = len(
                    prive_filter
                )


                totaal = (
                    prive_filter[
                        "kilometers"
                    ].sum()
                )


                gemiddeld = (
                    prive_filter[
                        "kilometers"
                    ].mean()
                )


                langste = (
                    prive_filter[
                        "kilometers"
                    ].max()
                )


                p1, p2, p3, p4 = (
                    st.columns(4)
                )


                p1.metric(
                    "Ritten",
                    aantal
                )


                p2.metric(
                    "Kilometers",
                    f"{totaal:.1f} km"
                )


                p3.metric(
                    "Gemiddelde rit",
                    f"{gemiddeld:.1f} km"
                )


                p4.metric(
                    "Langste rit",
                    f"{langste:.1f} km"
                )


                st.write("")


                overzicht = (
                    format_overzicht(
                        prive_filter,
                        inclusief_vergoeding=False,
                    )
                )


                st.dataframe(
                    overzicht,
                    use_container_width=True,
                    hide_index=True,
                )


                verwijder_rit(
                    prive_filter,
                    "delete_prive"
                )