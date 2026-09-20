import streamlit as st
from supabase_client import get_supabase


def login():
    supabase = get_supabase()

    st.title("🚗 AutoMaatje")
    st.caption("Log in om verder te gaan.")

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

                st.session_state["user"] = response.user
                st.session_state["access_token"] = (
                    response.session.access_token
                )
                st.session_state["refresh_token"] = (
                    response.session.refresh_token
                )

                st.rerun()

            else:
                st.error("Inloggen is niet gelukt.")

        except Exception as e:
            st.error(
                "E-mailadres of wachtwoord is niet correct."
            )
            st.exception(e)


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

        # Zet de sessie expliciet op DEZE client
        session_response = supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"],
        )

        # Tokens bijwerken indien Supabase ze heeft vernieuwd
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

        st.session_state.pop("user", None)
        st.session_state.pop("access_token", None)
        st.session_state.pop("refresh_token", None)

        st.warning(
            "Je sessie is verlopen. Log opnieuw in."
        )

        login()
        st.stop()


def logout():

    supabase = get_supabase()

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.pop("user", None)
    st.session_state.pop("access_token", None)
    st.session_state.pop("refresh_token", None)

    st.cache_data.clear()

    st.rerun()