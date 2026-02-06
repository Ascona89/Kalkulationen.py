import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import math
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# =====================================================
# 🔐 Passwörter
# =====================================================
USER_PASSWORD = "oyysouth"
SILENT_USER_PASSWORD = "silentlogin"
ADMIN_PASSWORD = "sebaforceo"
PIPELINE_PASSWORDS = {
    "south": "south",
    "mids": "mids",
    "east": "east",
    "north": "north"
}

# =====================================================
# 🧠 Supabase
# =====================================================
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def log_login(role, success):
    supabase.table("login_events").insert({
        "role": role,
        "success": success,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

# =====================================================
# 🧠 Session State Initialisierung
# =====================================================
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("is_admin", False)
st.session_state.setdefault("USER_PASSWORD", USER_PASSWORD)
st.session_state.setdefault("show_map", False)

# =====================================================
# 🔐 Login
# =====================================================
def login(password):
    user_pw = st.session_state.get("USER_PASSWORD", USER_PASSWORD)

    if password == user_pw:
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        log_login("User", True)
        st.rerun()
    elif password == SILENT_USER_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        st.rerun()
    elif password == ADMIN_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = True
        log_login("Admin", True)
        st.rerun()
    else:
        log_login("Unknown", False)
        st.error("❌ Falsches Passwort")

# =====================================================
# 👑 Admin Backend
# =====================================================
if st.session_state.is_admin:
    st.header("👑 Admin Dashboard")
    data = supabase.table("login_events").select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(data.data)
    if not df.empty:
        df["Datum"] = pd.to_datetime(df["created_at"]).dt.date
        st.subheader("📄 Login-Historie")
        st.dataframe(df, use_container_width=True)
        st.subheader("📊 Logins pro Tag")
        logins_per_day = df[df["success"]==True].groupby("Datum").size().reset_index(name="Logins")
        st.dataframe(logins_per_day, use_container_width=True)
        st.bar_chart(logins_per_day.set_index("Datum"))
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("CSV Export", csv, "login_history.csv", "text/csv")
    else:
        st.info("Noch keine Login-Daten vorhanden.")

    st.subheader("🔑 User Passwort ändern")
    new_password = st.text_input("Neues User-Passwort", type="password")
    if st.button("Update User Passwort"):
        if new_password:
            st.session_state['USER_PASSWORD'] = new_password
            st.success("✅ Passwort erfolgreich geändert!")
        else:
            st.warning("Bitte ein gültiges Passwort eingeben.")
    st.stop()

# =====================================================
# 🔐 Login Abfrage
# =====================================================
if not st.session_state.get("logged_in", False):
    st.header("🔐 Login")
    pw = st.text_input("Passwort eingeben", type="password")
    if st.button("Login"):
        login(pw)
    st.stop()

# =====================================================
# 🌍 Länder Auswahl
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

COUNTRIES = {
    "Germany": {"flag": "🇩🇪", "features": True},
    "Great Britain": {"flag": "🇬🇧", "features": True},
    "Maldives": {"flag": "🇲🇻", "features": False},
    "Denmark": {"flag": "🇩🇰", "features": False},
    "Finland": {"flag": "🇫🇮", "features": False},
    "Sweden": {"flag": "🇸🇪", "features": False},
    "Norway": {"flag": "🇳🇴", "features": False},
    "Netherlands": {"flag": "🇳🇱", "features": False},
    "Belgium": {"flag": "🇧🇪", "features": False},
    "Austria": {"flag": "🇦🇹", "features": False},
    "Switzerland": {"flag": "🇨🇭", "features": False}
}

st.subheader("🌎 Select your country")
cols = st.columns(len(COUNTRIES))
for idx, country in enumerate(COUNTRIES):
    if cols[idx].button(f"{COUNTRIES[country]['flag']} {country}"):
        st.session_state["country_selected"] = country

if "country_selected" not in st.session_state:
    st.info("Please select a country to continue")
    st.stop()

country = st.session_state["country_selected"]

# =====================================================
# Länder-Funktionen aktiv / inaktiv
# =====================================================
if not COUNTRIES[country]["features"]:
    st.warning("Nothing to work here, this country is only available for vacation")
    st.stop()

# =====================================================
# ===================== CALCULATION FUNCTIONS =====================
# Hier kommen deine aktuellen DE-Kalkulationen rein
# Du kannst sie 1:1 kopieren, auch GB bekommt sie gleich
# =====================================================

# ------------------- Platform -------------------
def show_platform():
    st.header(f"🏁 Platform Kalkulation ({country})")
    # Hier DE/GB Funktionen eins zu eins übernehmen
    # … DE/GB Logik bleibt unverändert …
    # (alles aus deinem alten show_platform() Code)

# ------------------- Cardpayment -------------------
def show_cardpayment():
    st.header(f"💳 Cardpayment Vergleich ({country})")
    # Hier DE/GB Funktionen eins zu eins übernehmen
    # … DE/GB Logik bleibt unverändert …

# ------------------- Pricing -------------------
def show_pricing():
    st.header(f"💰 Pricing Kalkulation ({country})")
    # Hier DE/GB Funktionen eins zu eins übernehmen
    # … DE/GB Logik bleibt unverändert …

# ------------------- Radien -------------------
def show_radien():
    st.header(f"🗺️ Radien oder PLZ-Flächen anzeigen ({country})")
    # Hier DE/GB Funktionen eins zu eins übernehmen
    # … DE/GB Logik bleibt unverändert …

# ------------------- Contract Numbers -------------------
def show_contractnumbers():
    st.header(f"📑 Contract Numbers ({country})")
    # Hier DE/GB Funktionen eins zu eins übernehmen
    # … DE/GB Logik bleibt unverändert …

# ------------------- Pipeline -------------------
def show_pipeline():
    st.header(f"📈 Pipeline ({country})")
    # Hier DE/GB Funktionen eins zu eins übernehmen
    # … DE/GB Logik bleibt unverändert …

# =====================================================
# Seitenlogik
# =====================================================
page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Radien", "Contractnumbers", "Pipeline"]
)

if page == "Platform":
    show_platform()
elif page == "Cardpayment":
    show_cardpayment()
elif page == "Pricing":
    show_pricing()
elif page == "Radien":
    show_radien()
elif page == "Contractnumbers":
    show_contractnumbers()
elif page == "Pipeline":
    show_pipeline()


