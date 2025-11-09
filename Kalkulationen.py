import streamlit as st

# -----------------------------------
# 🔒 Zugriffskontrolle
# -----------------------------------
# Liste der erlaubten Nutzer + Passwort (kann angepasst werden)
ALLOWED_USERS = {
    "user1": "pass1",
    "user2": "pass2",
    "sas": "geheim123"
}

if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

if not st.session_state["login_status"]:
    st.title("🔒 Login")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    if st.button("Login"):
        if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
            st.session_state["login_status"] = True
            st.success(f"Willkommen {username}!")
            st.experimental_rerun()
        else:
            st.error("Benutzername oder Passwort falsch!")
else:
    # ---------------------------
    # Hier kommt der komplette App-Code hin
    # ---------------------------
    st.title("📊 Kalkulations-App")
    st.sidebar.info("Zugriff erlaubt für autorisierte Nutzer")
