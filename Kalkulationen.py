import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client
import math
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import json
import requests

# =====================================================
# 🔐 Passwörter
# =====================================================
USER_PASSWORD = "oyysouth"
SILENT_USER_PASSWORD = "silentlogin"
ADMIN_PASSWORD = "sebaforceo"
PIPELINE_PASSWORDS = ["south", "mids", "east", "north"]

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
# 🔐 Login Funktion
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
# 👑 Admin Dashboard
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

    cost_platform = revenue * (commission_pct / 100) + (0.7 * revenue / avg_order_value if avg_order_value else 0) * service_fee
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

    transaction = 0.7 * revenue / 5 * 0.35
    cost_monthly = MRR + transaction
    saving_monthly = total_cost - cost_monthly
    saving_over_contract = saving_monthly * contract_length

    st.markdown("---")
    st.subheader("📊 Kennzahlen")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div style='color:red; font-size:28px;'>💶 {total_cost:,.2f} €</div>", unsafe_allow_html=True)
    col1.caption("Total Platform Cost")
    col2.markdown(f"<div style='color:blue; font-size:28px;'>💳 {cost_monthly:,.2f} €</div>", unsafe_allow_html=True)
    col2.caption("Cost Monthly (MRR + Transaction)")
    col3.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving_monthly:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Saving Monthly")
    col4.markdown(f"<div style='color:orange; font-size:28px;'>💸 {saving_over_contract:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Saving over Contract Length")

# =====================================================
# 💳 Cardpayment
# =====================================================
def show_cardpayment():
    st.header("💳 Cardpayment Vergleich")
    col_rev, col_sum = st.columns(2)
    with col_rev:
        revenue = persistent_number_input("Revenue (€)", "revenue", 0.0, step=250.0)
    with col_sum:
        sum_payments = persistent_number_input("Sum of payments", "sum_payments", 0.0, step=20.0)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Actual")
        mrr_a = persistent_number_input("Monthly Fee (€)", "mrr_a", 0.0, step=5.0)
        comm_a = persistent_number_input("Commission (%)", "comm_a", 1.39, step=0.01)
        auth_a = persistent_number_input("Authentification Fee (€)", "auth_a", 0.0)
    with col2:
        st.subheader("Offer")
        mrr_o = persistent_number_input("Monthly Fee (€)", "mrr_o", 0.0, step=5.0)
        comm_o = persistent_number_input("Commission (%)", "comm_o", 1.19, step=0.01)
        auth_o = persistent_number_input("Authentification Fee (€)", "auth_o", 0.06)

    total_actual = revenue * (comm_a/100) + sum_payments * auth_a + mrr_a
    total_offer = revenue * (comm_o/100) + sum_payments * auth_o + mrr_o
    saving = total_offer - total_actual
    saving_per_year = saving * 12

    st.markdown("---")
    col3, col4, col5, col6 = st.columns(4)
    col3.markdown(f"<div style='color:red; font-size:28px;'>💳 {total_actual:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Total Actual")
    col4.markdown(f"<div style='color:blue; font-size:28px;'>💳 {total_offer:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Total Offer")
    col5.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving:,.2f} €</div>", unsafe_allow_html=True)
    col5.caption("Ersparnis (Offer - Actual)")
    col6.markdown(f"<div style='color:orange; font-size:28px;'>💸 {saving_per_year:,.2f} €</div>", unsafe_allow_html=True)
    col6.caption("Ersparnis pro Jahr")

# =====================================================
# 💰 Pricing
# =====================================================
def show_pricing():
    st.header("💰 Pricing Kalkulation")
    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 0, 0],
        "List_OTF": [999, 49, 999, 49, 0, 0],
        "Min_MRR": [50, 15, 49, 5, 15, 0],
        "List_MRR": [119, 49, 89, 25, 15, 0]
    })
    df_hw = pd.DataFrame({
        "Produkt":["Ordermanager","POS inkl 1 Printer","Cash Drawer","Extra Printer","Additional Display","PAX"],
        "Min_OTF":[135,350,50,99,100,225],
        "List_OTF":[299,1699,149,199,100,299],
        "Min_MRR":[0]*6,
        "List_MRR":[0]*6
    })

    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(df_hw)):
        st.session_state.setdefault(f"hw_{i}", 0)

    st.subheader("💻 Software")
    sw_cols = st.columns(len(df_sw))
    for i, p in enumerate(df_sw["Produkt"]):
        with sw_cols[i]:
            st.session_state[f"sw_{i}"] = st.number_input(
                p, min_value=0, step=1,
                value=st.session_state[f"sw_{i}"],
                key=f"sw_ui_{i}"
            )

    st.subheader("🖨️ Hardware")
    hw_cols = st.columns(len(df_hw))
    for i, p in enumerate(df_hw["Produkt"]):
        with hw_cols[i]:
            st.session_state[f"hw_{i}"] = st.number_input(
                p, min_value=0, step=1,
                value=st.session_state[f"hw_{i}"],
                key=f"hw_ui_{i}"
            )

    df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]
