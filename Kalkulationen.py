import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import math
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
import json

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
# Hier kommt dein alter, kompletter DE-Code 1:1
# DE & GB bekommen exakt die gleiche Logik
# =====================================================

# ==========================================
# Platform
# ==========================================
def show_platform():
    st.header(f"🏁 Platform Kalkulation ({country})")
    col1, col2 = st.columns([2, 1.5])
    with col1:
        st.subheader("Eingaben")
        revenue = st.number_input("Revenue on platform (€)", 0.0, step=250.0)
        commission_pct = st.number_input("Commission (%)", 14.0, step=1.0)
        avg_order_value = st.number_input("Average order value (€)", 25.0, step=5.0)
        service_fee = st.number_input("Service Fee (€)", 0.69, step=0.1)
        toprank_per_order = st.number_input("TopRank per Order (€)", 0.0, step=0.1)

        cost_platform = revenue * (commission_pct / 100) + (0.7 * revenue / avg_order_value if avg_order_value else 0) * service_fee
        sum_of_orders = revenue / avg_order_value if avg_order_value else 0
        toprank_cost = sum_of_orders * toprank_per_order
        total_cost = cost_platform + toprank_cost

        st.markdown(f"### 💶 Cost on Platform: {total_cost:,.2f} €")

# ==========================================
# Cardpayment
# ==========================================
def show_cardpayment():
    st.header(f"💳 Cardpayment Vergleich ({country})")
    revenue = st.number_input("Revenue (€)", 0.0, step=250.0)
    sum_payments = st.number_input("Sum of payments", 0.0, step=20.0)
    mrr_a = st.number_input("Monthly Fee (€) Actual", 0.0, step=5.0)
    comm_a = st.number_input("Commission (%) Actual", 1.39, step=0.01)
    auth_a = st.number_input("Authentification Fee (€) Actual", 0.0)
    mrr_o = st.number_input("Monthly Fee (€) Offer", 0.0, step=5.0)
    comm_o = st.number_input("Commission (%) Offer", 1.19, step=0.01)
    auth_o = st.number_input("Authentification Fee (€) Offer", 0.06)

    total_actual = revenue*(comm_a/100) + sum_payments*auth_a + mrr_a
    total_offer = revenue*(comm_o/100) + sum_payments*auth_o + mrr_o
    saving = total_offer - total_actual
    st.markdown(f"**Saving:** {saving:,.2f} €")

# ==========================================
# Pricing
# ==========================================
def show_pricing():
    st.header(f"💰 Pricing Kalkulation ({country})")
    st.write("Hier kommt dein alter Pricing-Code 1:1 rein.")

# ==========================================
# Radien
# ==========================================
def show_radien():
    st.header(f"🗺️ Radien oder PLZ-Flächen ({country})")
    st.write("Hier kommt dein alter Radien-Code 1:1 rein.")

# ==========================================
# Contract Numbers
# ==========================================
def show_contractnumbers():
    st.header(f"📑 Contract Numbers ({country})")
    st.write("Hier kommt dein alter Contract Numbers-Code 1:1 rein.")

# ==========================================
# Pipeline
# ==========================================
def show_pipeline():
    st.header(f"📈 Pipeline ({country})")
    st.write("Hier kommt dein alter Pipeline-Code 1:1 rein.")

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
