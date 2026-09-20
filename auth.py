import streamlit as st
from supabase_client import get_supabase


# ============================================================
# LOGIN
# ============================================================

def login():
    supabase = get_supabase()

    st.title("🚗 AutoMaatje")
    st.caption("Log in of maak een account aan.")

    keuze = st.radio(
        "Kies een optie",
        ["Inloggen", "Account aanmaken"],
        horizontal=True,
        key="auth_keuze",
    )

    st.divider()

    if keuze == "Inloggen":
        login_form(supabase)

    else:
        register(supabase)


# ============================================================
# LOGIN FORMULIER
# ============================================================

def login_form(supabase):

    st.subheader("Inloggen")

    email = st.text_input(
        "E-mailadres",
        key="login_email",
    )

    password = st.text_input(
        "Wachtwoord",
        type="password",
        key="login_password",
    )

    if st.button(
        "Inloggen",
        use_container_width=True,
        type="primary",
        key="login_button",
    ):

        if not email or not password:
            st.error(
                "Vul je e-mailadres en wachtwoord in."
            )
            return

        try:
            response = (
                supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password,
                    }
                )
            )

            if (
                response.user is not None
                and response.session is not None
            ):

                st.session_state["user"] = (
                    response.user
                )

                st.session_state["access_token"] = (
                    response.session.access_token
                )

                st.session_state["refresh_token"] = (
                    response.session.refresh_token
                )

                st.rerun()

            else:
                st.error(
                    "Inloggen is niet gelukt."
                )

        except Exception as e:

            foutmelding = str(e)

            if "Email not confirmed" in foutmelding:
                st.error(
                    "Je e-mailadres is nog niet bevestigd. "
                    "Controleer je e-mail en klik op de verificatielink."
                )

            elif "Invalid login credentials" in foutmelding:
                st.error(
                    "E-mailadres of wachtwoord is niet correct."
                )

            else:
                st.error(
                    "Inloggen is niet gelukt."
                )
                st.exception(e)


# ============================================================
# REGISTREREN
# ============================================================

def register(supabase):

    st.subheader("Account aanmaken")

    email = st.text_input(
        "E-mailadres",
        key="register_email",
    )

    password = st.text_input(
        "Wachtwoord",
        type="password",
        key="register_password",
    )

    password_check = st.text_input(
        "Herhaal wachtwoord",
        type="password",
        key="register_password_check",
    )

    if st.button(
        "Account aanmaken",
        use_container_width=True,
        type="primary",
        key="register_button",
    ):

        if not email:
            st.error(
                "Vul een e-mailadres in."
            )
            return

        if not password:
            st.error(
                "Vul een wachtwoord in."
            )
            return

        if len(password) < 6:
            st.error(
                "Gebruik een wachtwoord van minimaal 6 tekens."
            )
            return

        if password != password_check:
            st.error(
                "De wachtwoorden komen niet overeen."
            )
            return

        try:
            response = (
                supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                        "options": {
                            "email_redirect_to": (
                                "https://automaatje.streamlit.app/Verificatie"
                            )
                        },
                    }
                )
            )

            if response.user is not None:

                st.success(
                    "Account aangemaakt!"
                )

                st.info(
                    "Controleer je e-mail en klik op de verificatielink. "
                    "Daarna kun je inloggen bij AutoMaatje."
                )

            else:
                st.error(
                    "Account aanmaken is niet gelukt."
                )

        except Exception as e:

            foutmelding = str(e)

            if "already registered" in foutmelding.lower():
                st.error(
                    "Er bestaat al een account met dit e-mailadres."
                )

            else:
                st.error(
                    "Account aanmaken is niet gelukt."
                )
                st.exception(e)


# ============================================================
# LOGIN VERPLICHTEN
# ============================================================

def require_login():

    if (
        "user" not in st.session_state
        or "access_token" not in st.session_state
        or "refresh_token" not in st.session_state
    ):
        login()
        st.stop()

    try:
        supabase = get_supabase()

        session_response = (
            supabase.auth.set_session(
                st.session_state["access_token"],
                st.session_state["refresh_token"],
            )
        )

        if session_response.session is not None:

            st.session_state["access_token"] = (
                session_response.session.access_token
            )

            st.session_state["refresh_token"] = (
                session_response.session.refresh_token
            )

            if session_response.user is not None:
                st.session_state["user"] = (
                    session_response.user
                )

        return (
            st.session_state["user"],
            supabase,
        )

    except Exception:

        st.session_state.pop(
            "user",
            None
        )

        st.session_state.pop(
            "access_token",
            None
        )

        st.session_state.pop(
            "refresh_token",
            None
        )

        st.warning(
            "Je sessie is verlopen. Log opnieuw in."
        )

        login()
        st.stop()


# ============================================================
# UITLOGGEN
# ============================================================

def logout():

    supabase = get_supabase()

    try:
        supabase.auth.sign_out()

    except Exception:
        pass

    st.session_state.pop(
        "user",
        None
    )

    st.session_state.pop(
        "access_token",
        None
    )

    st.session_state.pop(
        "refresh_token",
        None
    )

    st.cache_data.clear()

    st.rerun()