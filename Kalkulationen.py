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
        # bewusst KEIN log_login
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
# 🔧 App Setup
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Radien", "Contractnumbers", "Pipeline"]
)

# ==========================
# Hilfsfunktionen für persistente Inputs
# ==========================
def persistent_number_input(label, key, value=0.0, **kwargs):
    st.session_state.setdefault(key, value)
    st.session_state[key] = st.number_input(label, value=st.session_state[key], key=f"ui_{key}", **kwargs)
    return st.session_state[key]

def persistent_text_input(label, key, value="", **kwargs):
    st.session_state.setdefault(key, value)
    st.session_state[key] = st.text_input(label, value=st.session_state[key], key=f"ui_{key}", **kwargs)
    return st.session_state[key]

def persistent_selectbox(label, key, options, index=0, **kwargs):
    st.session_state.setdefault(key, options[index])
    st.session_state[key] = st.selectbox(label, options, index=options.index(st.session_state[key]), **kwargs)
    return st.session_state[key]

# =====================================================
# 🏁 Platform
# =====================================================
def show_platform():
    st.header("🏁 Platform Kalkulation")
    col1, col2 = st.columns([2, 1.5])

    with col1:
        st.subheader("Eingaben")
        revenue = persistent_number_input("Revenue on platform (€)", "revenue", 0.0, step=250.0)
        commission_pct = persistent_number_input("Commission (%)", "commission_pct", 14.0, step=1.0)
        avg_order_value = persistent_number_input("Average order value (€)", "avg_order_value", 25.0, step=5.0)
        service_fee = persistent_number_input("Service Fee (€)", "service_fee", 0.69, step=0.1)
        toprank_per_order = persistent_number_input("TopRank per Order (€)", "toprank_per_order", 0.0, step=0.1)

        # ==============================
        # 🧮 Berechnung Cost on Platform direkt nach Eingaben
        # ==============================
        cost_platform = revenue * (commission_pct / 100) + \
                        (0.7 * revenue / avg_order_value if avg_order_value else 0) * service_fee

        sum_of_orders = revenue / avg_order_value if avg_order_value else 0
        toprank_cost = sum_of_orders * toprank_per_order

        total_cost = cost_platform + toprank_cost

        st.markdown("### 💶 Cost on Platform")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Vertragsdetails")
        OTF = persistent_number_input("One Time Fee (OTF) (€)", "OTF", 0.0, step=100.0)
        MRR = persistent_number_input("Monthly Recurring Revenue (MRR) (€)", "MRR", 0.0, step=10.0)
        contract_length = persistent_number_input("Contract length (Monate)", "contract_length", 24, step=12)

# =====================================================
# 💳 Cardpayment
# =====================================================
def show_cardpayment():
    st.header("💳 Cardpayment Vergleich")
    # ... (Rest des Codes unverändert)
    st.write("Hier kommt der Cardpayment-Code 1:1 hin")  

# =====================================================
# Pricing
# =====================================================
def show_pricing():
    st.header("💰 Pricing Kalkulation")
    st.write("Hier kommt der Pricing-Code 1:1 hin")  

# =====================================================
# Radien
# =====================================================
def show_radien():
    st.header("🗺️ Radien oder PLZ-Flächen anzeigen")
    st.write("Hier kommt der Radien-Code 1:1 hin")  

# =====================================================
# Contract Numbers
# =====================================================
def show_contractnumbers():
    st.header("📑 Contract Numbers")
    st.write("Hier kommt der Contract Numbers-Code 1:1 hin")  

# =====================================================
# Pipeline
# =====================================================
def show_pipeline():
    st.header("📈 Pipeline")
    st.write("Hier kommt der Pipeline-Code 1:1 hin")  

# =====================================================
# 🏗 Seitenlogik
# =====================================================
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
