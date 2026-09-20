import streamlit as st
import pandas as pd
from datetime import date, timedelta

from supabase_client import get_supabase


# ============================================================
# PAGINA INSTELLINGEN
# ============================================================

st.set_page_config(
    page_title="Ritten",
    page_icon="🛣️",
    layout="wide",
)

st.title("🛣️ Ritten")
st.caption(
    "Registreer één of meerdere ritten en bekijk zakelijke en privéritten apart."
)

supabase = get_supabase()


# ============================================================
# HELPERS
# ============================================================

@st.cache_data(ttl=30)
def load_ritten():
    """
    Haal alle ritten uit Supabase op
    en bereid de belangrijkste kolommen voor.
    """

    response = (
        supabase
        .table("ritten")
        .select("*")
        .order("datum", desc=True)
        .execute()
    )

    df = pd.DataFrame(response.data)

    if df.empty:
        return df

    # Datum
    df["datum"] = pd.to_datetime(
        df["datum"],
        errors="coerce"
    )

    # Numerieke kolommen
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

    # Belastingvrij bedrag
    df["belastingvrij_bedrag"] = (
        df["kilometers"]
        * df[
            [
                "vergoeding_per_km",
                "belastingvrij_per_km"
            ]
        ].min(axis=1)
    )

    # Belast gedeelte
    df["belast_bedrag"] = (
        df["bruto_vergoeding"]
        - df["belastingvrij_bedrag"]
    ).clip(lower=0)

    # Geschatte belasting
    df["belasting"] = (
        df["belast_bedrag"]
        * (
            df["belastingpercentage"]
            / 100
        )
    )

    # Geschatte netto vergoeding
    df["netto_vergoeding"] = (
        df["bruto_vergoeding"]
        - df["belasting"]
    )

    # Privéritten krijgen geen vergoeding
    prive_mask = (
        df["type_rit"] == "Privé"
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
    """
    Maak één lijst van alle eerder gebruikte
    vertrek- en bestemmingslocaties.
    """

    if df.empty:
        return []

    locaties = set()

    if "van" in df.columns:
        for locatie in df["van"].dropna():
            locatie = str(locatie).strip()

            if locatie:
                locaties.add(locatie)

    if "naar" in df.columns:
        for locatie in df["naar"].dropna():
            locatie = str(locatie).strip()

            if locatie:
                locaties.add(locatie)

    return sorted(
        locaties,
        key=str.lower
    )


def format_overzicht(
    df,
    inclusief_vergoeding=True
):
    """
    Maak een nette dataframe voor weergave
    in Streamlit.
    """

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

    overzicht = df[kolommen].copy()

    overzicht["datum"] = (
        overzicht["datum"]
        .dt.strftime("%d-%m-%Y")
    )

    rename = {
        "datum": "Datum",
        "van": "Van",
        "naar": "Naar",
        "omschrijving": "Omschrijving",
        "type_rit": "Type",
        "kilometers": "Kilometers",
        "vergoeding_per_km": "€/km",
        "bruto_vergoeding": "Bruto vergoeding",
        "netto_vergoeding": "Geschat netto",
    }

    overzicht = overzicht.rename(
        columns=rename
    )

    if inclusief_vergoeding:

        overzicht["€/km"] = (
            overzicht["€/km"]
            .apply(
                lambda x: (
                    f"€ {x:.3f}"
                    if pd.notna(x)
                    else "-"
                )
            )
        )

        overzicht["Bruto vergoeding"] = (
            overzicht["Bruto vergoeding"]
            .apply(
                lambda x: f"€ {x:.2f}"
            )
        )

        overzicht["Geschat netto"] = (
            overzicht["Geschat netto"]
            .apply(
                lambda x: f"€ {x:.2f}"
            )
        )

    return overzicht


def verwijder_rit(
    dataframe,
    type_label,
    key_prefix
):
    """
    Toon een selectieveld waarmee één rit
    verwijderd kan worden.
    """

    if dataframe.empty:
        return

    st.divider()

    with st.expander(
        f"🗑️ {type_label} verwijderen"
    ):

        rit_opties = {}

        for _, row in dataframe.iterrows():

            datum_text = (
                row["datum"].strftime("%d-%m-%Y")
                if pd.notna(row["datum"])
                else "Onbekende datum"
            )

            label = (
                f"{datum_text} | "
                f"{row['van']} → {row['naar']} | "
                f"{row['kilometers']:.1f} km"
            )

            # ID toevoegen indien twee ritten exact dezelfde omschrijving hebben
            label = f"{label} | #{row['id']}"

            rit_opties[label] = row["id"]

        geselecteerde_rit = st.selectbox(
            "Selecteer een rit",
            options=list(
                rit_opties.keys()
            ),
            index=None,
            placeholder="Kies een rit...",
            key=f"{key_prefix}_select",
        )

        if geselecteerde_rit is not None:

            verwijder_id = (
                rit_opties[
                    geselecteerde_rit
                ]
            )

            bevestigen = st.checkbox(
                "Ik weet zeker dat ik deze rit wil verwijderen",
                key=f"{key_prefix}_confirm",
            )

            if st.button(
                "🗑️ Rit definitief verwijderen",
                disabled=not bevestigen,
                key=f"{key_prefix}_button",
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

                    st.success(
                        "Rit verwijderd."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Rit verwijderen is niet gelukt."
                    )

                    st.exception(e)


# ============================================================
# DATA LADEN
# ============================================================

try:

    ritten_df = load_ritten()

except Exception as e:

    st.error(
        "Ritten konden niet uit Supabase worden geladen."
    )

    st.exception(e)

    ritten_df = pd.DataFrame()


# Eerder gebruikte locaties ophalen
opgeslagen_locaties = (
    get_opgeslagen_locaties(
        ritten_df
    )
)


# ============================================================
# TABS
# ============================================================

tab_nieuw, tab_zakelijk, tab_prive = st.tabs(
    [
        "➕ Nieuwe rit",
        "💼 Zakelijk",
        "🏠 Privé",
    ]
)


# ============================================================
# TAB 1 - NIEUWE RIT
# ============================================================

with tab_nieuw:

    st.subheader("Nieuwe rit")

    # --------------------------------------------------------
    # Één dag / meerdere dagen
    # --------------------------------------------------------

    invoer_type = st.radio(
        "Rit invoeren voor",
        [
            "Eén dag",
            "Meerdere dagen"
        ],
        horizontal=True,
    )

    # --------------------------------------------------------
    # Datumselectie
    # --------------------------------------------------------

    if invoer_type == "Eén dag":

        geselecteerde_datums = [
            st.date_input(
                "Datum",
                value=date.today(),
                key="enkele_datum",
            )
        ]

    else:

        datum_col1, datum_col2 = (
            st.columns(2)
        )

        with datum_col1:

            datum_van = st.date_input(
                "Van datum",
                value=date.today(),
                key="datum_van",
            )

        with datum_col2:

            datum_tot = st.date_input(
                "Tot datum",
                value=date.today(),
                key="datum_tot",
            )

        weekdagen = st.multiselect(
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

        dag_mapping = {
            "Maandag": 0,
            "Dinsdag": 1,
            "Woensdag": 2,
            "Donderdag": 3,
            "Vrijdag": 4,
            "Zaterdag": 5,
            "Zondag": 6,
        }

        geselecteerde_weekdagen = [
            dag_mapping[dag]
            for dag in weekdagen
        ]

        geselecteerde_datums = []

        if datum_tot >= datum_van:

            huidige_datum = datum_van

            while (
                huidige_datum
                <= datum_tot
            ):

                if (
                    huidige_datum.weekday()
                    in geselecteerde_weekdagen
                ):

                    geselecteerde_datums.append(
                        huidige_datum
                    )

                huidige_datum += timedelta(
                    days=1
                )

        if datum_tot < datum_van:

            st.warning(
                "De einddatum moet op of na de begindatum liggen."
            )

        elif not weekdagen:

            st.warning(
                "Selecteer minimaal één weekdag."
            )

        elif geselecteerde_datums:

            st.info(
                f"{len(geselecteerde_datums)} "
                f"ritten geselecteerd."
            )

            with st.expander(
                "Bekijk geselecteerde datums"
            ):

                for geselecteerde_datum in (
                    geselecteerde_datums
                ):

                    st.write(
                        geselecteerde_datum.strftime(
                            "%d-%m-%Y"
                        )
                    )


    # --------------------------------------------------------
    # Ritgegevens
    # --------------------------------------------------------

    st.divider()

    st.subheader("📍 Route")

    col1, col2 = st.columns(2)


    # ========================================================
    # LINKER KOLOM
    # ========================================================

    with col1:

        # ----------------------------------------------------
        # VAN
        # ----------------------------------------------------

        van_keuze = st.selectbox(
            "Van",
            options=[
                "Nieuwe locatie..."
            ] + opgeslagen_locaties,
            index=None,
            placeholder="Kies een locatie...",
            key="van_keuze",
        )

        if (
            van_keuze
            == "Nieuwe locatie..."
        ):

            van = st.text_input(
                "Nieuwe vertreklocatie",
                placeholder=(
                    "Bijvoorbeeld: Hoorn"
                ),
                key="van_nieuw",
            )

        else:

            van = (
                van_keuze
                if van_keuze
                else ""
            )


        # ----------------------------------------------------
        # NAAR
        # ----------------------------------------------------

        naar_keuze = st.selectbox(
            "Naar",
            options=[
                "Nieuwe locatie..."
            ] + opgeslagen_locaties,
            index=None,
            placeholder="Kies een bestemming...",
            key="naar_keuze",
        )

        if (
            naar_keuze
            == "Nieuwe locatie..."
        ):

            naar = st.text_input(
                "Nieuwe bestemming",
                placeholder=(
                    "Bijvoorbeeld: Amsterdam"
                ),
                key="naar_nieuw",
            )

        else:

            naar = (
                naar_keuze
                if naar_keuze
                else ""
            )


        # ----------------------------------------------------
        # OMSCHRIJVING
        # ----------------------------------------------------

        omschrijving = st.text_input(
            "Omschrijving",
            placeholder=(
                "Bijvoorbeeld: kantoor, "
                "klantbezoek, project"
            ),
        )


    # ========================================================
    # RECHTER KOLOM
    # ========================================================

    with col2:

        type_rit = st.selectbox(
            "Type rit",
            [
                "Zakelijk",
                "Woon-werk",
                "Privé",
            ],
        )

        enkele_km = st.number_input(
            "Afstand enkele reis (km)",
            min_value=0.0,
            step=1.0,
            format="%.1f",
        )

        retourrit = st.checkbox(
            "Retourrit",
            value=True,
        )

        vergoeding_per_km = (
            st.number_input(
                "Kilometervergoeding werkgever (€ / km)",
                min_value=0.0,
                value=0.31,
                step=0.01,
                format="%.3f",
                disabled=(
                    type_rit
                    == "Privé"
                ),
            )
        )


    # --------------------------------------------------------
    # Kilometerberekening
    # --------------------------------------------------------

    if retourrit:

        km_per_rit = (
            enkele_km * 2
        )

    else:

        km_per_rit = (
            enkele_km
        )


    aantal_ritten = len(
        geselecteerde_datums
    )

    totaal_km_selectie = (
        km_per_rit
        * aantal_ritten
    )


    # ========================================================
    # VERGOEDING
    # ========================================================

    st.divider()

    st.subheader(
        "💶 Vergoeding"
    )


    if type_rit in [
        "Zakelijk",
        "Woon-werk"
    ]:

        col3, col4 = (
            st.columns(2)
        )

        with col3:

            belastingvrij_per_km = (
                st.number_input(
                    "Belastingvrij bedrag per km (€)",
                    min_value=0.0,
                    value=0.25,
                    step=0.01,
                    format="%.3f",
                )
            )

        with col4:

            belastingpercentage = (
                st.number_input(
                    "Belastingpercentage belast deel (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=35.75,
                    step=0.1,
                    format="%.2f",
                )
            )


        # Bruto per rit
        bruto_per_rit = (
            km_per_rit
            * vergoeding_per_km
        )


        # Belastingvrij per rit
        belastingvrij_per_rit = (
            km_per_rit
            * min(
                vergoeding_per_km,
                belastingvrij_per_km,
            )
        )


        # Belast deel
        belast_per_rit = max(
            bruto_per_rit
            - belastingvrij_per_rit,
            0,
        )


        # Belasting
        belasting_per_rit = (
            belast_per_rit
            * (
                belastingpercentage
                / 100
            )
        )


        # Netto
        netto_per_rit = (
            bruto_per_rit
            - belasting_per_rit
        )


    else:

        belastingvrij_per_km = 0
        belastingpercentage = 0

        bruto_per_rit = 0
        belastingvrij_per_rit = 0
        belast_per_rit = 0
        belasting_per_rit = 0
        netto_per_rit = 0

        st.info(
            "Privérit geselecteerd: "
            "er wordt geen kilometervergoeding berekend."
        )


    # --------------------------------------------------------
    # Totalen
    # --------------------------------------------------------

    bruto_totaal = (
        bruto_per_rit
        * aantal_ritten
    )

    netto_totaal = (
        netto_per_rit
        * aantal_ritten
    )


    # ========================================================
    # KPI'S
    # ========================================================

    k1, k2, k3, k4 = (
        st.columns(4)
    )

    k1.metric(
        "Aantal ritten",
        f"{aantal_ritten}",
    )

    k2.metric(
        "Totaal kilometers",
        f"{totaal_km_selectie:.1f} km",
    )

    k3.metric(
        "Bruto vergoeding",
        f"€ {bruto_totaal:.2f}",
    )

    k4.metric(
        "Geschat netto",
        f"€ {netto_totaal:.2f}",
    )


    # --------------------------------------------------------
    # Extra informatie
    # --------------------------------------------------------

    if (
        retourrit
        and enkele_km > 0
    ):

        st.caption(
            f"Per rit: "
            f"{enkele_km:.1f} km heen + "
            f"{enkele_km:.1f} km terug = "
            f"{km_per_rit:.1f} km."
        )


    if (
        invoer_type
        == "Meerdere dagen"
        and aantal_ritten > 0
    ):

        st.caption(
            f"{aantal_ritten} ritten × "
            f"{km_per_rit:.1f} km = "
            f"{totaal_km_selectie:.1f} km totaal."
        )


    # ========================================================
    # OPSLAAN
    # ========================================================

    st.divider()

    if st.button(
        "💾 Rit opslaan",
        use_container_width=True,
        type="primary",
    ):

        if not geselecteerde_datums:

            st.error(
                "Selecteer minimaal één geldige datum."
            )


        elif not van.strip():

            st.error(
                "Selecteer of vul een vertrekpunt in."
            )


        elif not naar.strip():

            st.error(
                "Selecteer of vul een bestemming in."
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
                                vergoeding_per_km
                                if type_rit
                                != "Privé"
                                else 0,

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


                # Cache leegmaken zodat nieuwe locatie
                # direct beschikbaar wordt
                st.cache_data.clear()


                if type_rit == "Privé":

                    st.success(
                        f"{len(records)} rit"
                        f"{'ten' if len(records) != 1 else ''} "
                        f"opgeslagen. "
                        f"Totaal "
                        f"{totaal_km_selectie:.1f} km."
                    )

                else:

                    st.success(
                        f"{len(records)} rit"
                        f"{'ten' if len(records) != 1 else ''} "
                        f"opgeslagen. "
                        f"Totaal "
                        f"{totaal_km_selectie:.1f} km "
                        f"met een geschatte netto vergoeding "
                        f"van € {netto_totaal:.2f}."
                    )


                st.rerun()


            except Exception as e:

                st.error(
                    "Opslaan is niet gelukt."
                )

                st.exception(e)


# ============================================================
# TAB 2 - ZAKELIJK
# ============================================================

with tab_zakelijk:

    st.subheader(
        "💼 Zakelijke ritten"
    )

    st.caption(
        "Zakelijke en woon-werkritten inclusief kilometervergoeding."
    )


    if ritten_df.empty:

        st.info(
            "Er zijn nog geen ritten opgeslagen."
        )


    else:

        zakelijke_df = ritten_df[
            ritten_df["type_rit"].isin(
                [
                    "Zakelijk",
                    "Woon-werk"
                ]
            )
        ].copy()


        if zakelijke_df.empty:

            st.info(
                "Er zijn nog geen zakelijke "
                "of woon-werkritten opgeslagen."
            )


        else:

            # ------------------------------------------------
            # KPI'S
            # ------------------------------------------------

            totaal_zakelijke_km = (
                zakelijke_df[
                    "kilometers"
                ].sum()
            )

            totaal_bruto = (
                zakelijke_df[
                    "bruto_vergoeding"
                ].sum()
            )

            totaal_netto = (
                zakelijke_df[
                    "netto_vergoeding"
                ].sum()
            )

            aantal_zakelijke_ritten = (
                len(zakelijke_df)
            )


            c1, c2, c3, c4 = (
                st.columns(4)
            )


            c1.metric(
                "Aantal ritten",
                f"{aantal_zakelijke_ritten}",
            )

            c2.metric(
                "Zakelijke kilometers",
                f"{totaal_zakelijke_km:.1f} km",
            )

            c3.metric(
                "Bruto vergoeding",
                f"€ {totaal_bruto:.2f}",
            )

            c4.metric(
                "Geschat netto",
                f"€ {totaal_netto:.2f}",
            )


            # ------------------------------------------------
            # FILTER
            # ------------------------------------------------

            st.divider()

            filter_type = st.multiselect(
                "Toon type rit",
                [
                    "Zakelijk",
                    "Woon-werk",
                ],
                default=[
                    "Zakelijk",
                    "Woon-werk",
                ],
                key="filter_zakelijk",
            )


            zakelijke_filter = (
                zakelijke_df[
                    zakelijke_df[
                        "type_rit"
                    ].isin(
                        filter_type
                    )
                ]
                .copy()
            )


            # ------------------------------------------------
            # TABEL
            # ------------------------------------------------

            if zakelijke_filter.empty:

                st.info(
                    "Geen ritten voor deze selectie."
                )

            else:

                overzicht = (
                    format_overzicht(
                        zakelijke_filter,
                        inclusief_vergoeding=True,
                    )
                )


                st.dataframe(
                    overzicht,
                    use_container_width=True,
                    hide_index=True,
                )


                # --------------------------------------------
                # VERWIJDEREN
                # --------------------------------------------

                verwijder_rit(
                    zakelijke_filter,
                    "Zakelijke rit",
                    "delete_zakelijk",
                )


# ============================================================
# TAB 3 - PRIVÉ
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
            "Er zijn nog geen ritten opgeslagen."
        )


    else:

        prive_df = ritten_df[
            ritten_df["type_rit"]
            == "Privé"
        ].copy()


        if prive_df.empty:

            st.info(
                "Er zijn nog geen privéritten opgeslagen."
            )


        else:

            # ------------------------------------------------
            # KPI'S
            # ------------------------------------------------

            totaal_prive_km = (
                prive_df[
                    "kilometers"
                ].sum()
            )

            aantal_prive_ritten = (
                len(prive_df)
            )

            gemiddelde_rit = (
                prive_df[
                    "kilometers"
                ].mean()
            )

            langste_rit = (
                prive_df[
                    "kilometers"
                ].max()
            )


            p1, p2, p3, p4 = (
                st.columns(4)
            )


            p1.metric(
                "Aantal ritten",
                f"{aantal_prive_ritten}",
            )

            p2.metric(
                "Privékilometers",
                f"{totaal_prive_km:.1f} km",
            )

            p3.metric(
                "Gem. ritafstand",
                f"{gemiddelde_rit:.1f} km",
            )

            p4.metric(
                "Langste rit",
                f"{langste_rit:.1f} km",
            )


            # ------------------------------------------------
            # TABEL
            # ------------------------------------------------

            st.divider()

            overzicht = (
                format_overzicht(
                    prive_df,
                    inclusief_vergoeding=False,
                )
            )


            st.dataframe(
                overzicht,
                use_container_width=True,
                hide_index=True,
            )


            # ------------------------------------------------
            # VERWIJDEREN
            # ------------------------------------------------

            verwijder_rit(
                prive_df,
                "Privérit",
                "delete_prive",
            )