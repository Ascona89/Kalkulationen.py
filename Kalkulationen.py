import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import math
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# =====================================================
# 🔐 Passwörter
# =====================================================
USER_PASSWORD = "welovekb"
ADMIN_PASSWORD = "sebaforceo"

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
# 🧠 Session State
# =====================================================
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("is_admin", False)
st.session_state.setdefault("USER_PASSWORD", USER_PASSWORD)
st.session_state.setdefault("show_map", False)

# =====================================================
# 🔐 Login
# =====================================================
def login(password):
    if password == st.session_state["USER_PASSWORD"]:
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        log_login("User", True)
        st.rerun()
    elif password == ADMIN_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = True
        log_login("Admin", True)
        st.rerun()
    else:
        log_login("Unknown", False)
        st.error("❌ Falsches Passwort")

if not st.session_state.logged_in:
    st.title("🔐 Login erforderlich")
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        login(pw)
    st.stop()

# =====================================================
# 👑 Admin
# =====================================================
if st.session_state.is_admin:
    st.header("👑 Admin Dashboard")
    data = supabase.table("login_events").select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(data.data)
    st.dataframe(df, use_container_width=True)
    st.stop()

# =====================================================
# 🔧 App Setup
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

# =====================================================
# 📂 Sidebar
# =====================================================
page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    [
        "Platform",
        "Cardpayment",
        "Pricing",
        "Radien",
        "Telesales",
        "Contract Numbers"  # 🆕
    ]
)

# =====================================================
# 📑 CONTRACT NUMBERS
# =====================================================
if page == "Contract Numbers":

    st.header("📑 Contract Numbers")

    # Produkte aus Pricing
    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "GAW"],
        "Typ": ["Software"] * 6
    })

    df_hw = pd.DataFrame({
        "Produkt": [
            "Ordermanager",
            "POS inkl 1 Printer",
            "Cash Drawer",
            "Extra Printer",
            "Additional Display",
            "PAX"
        ],
        "Typ": ["Hardware"] * 6
    })

    df_products = pd.concat([df_sw, df_hw], ignore_index=True)

    # -------------------------
    # Eingaben Gesamtwerte
    # -------------------------
    col1, col2 = st.columns(2)
    with col1:
        total_mrr = st.number_input("💶 Gesamt MRR (€)", min_value=0.0, step=50.0)
    with col2:
        total_otf = st.number_input("💶 Gesamt OTF (€)", min_value=0.0, step=100.0)

    st.markdown("---")
    st.subheader("📦 Verkäufe pro Produkt")

    for i in df_products.index:
        st.session_state.setdefault(f"cn_qty_{i}", 0)

    total_units = sum(st.session_state[f"cn_qty_{i}"] for i in df_products.index)

    results = []

    for i, row in df_products.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        qty = col2.number_input(
            row["Produkt"],
            min_value=0,
            step=1,
            key=f"cn_qty_{i}"
        )

        mrr_month = (total_mrr / total_units) * qty if total_units > 0 else 0
        mrr_week = mrr_month / 4

        col1.write(row["Produkt"])
        col3.write(f"{mrr_month:,.2f} €")
        col4.write(f"{mrr_week:,.2f} €")

        results.append({
            "Produkt": row["Produkt"],
            "Typ": row["Typ"],
            "Menge": qty,
            "MRR_Monat": mrr_month
        })

    df_result = pd.DataFrame(results)

    # -------------------------
    # OTF Verteilung
    # -------------------------
    st.markdown("---")
    st.subheader("🧾 OTF Aufteilung")

    total_qty = df_result["Menge"].sum()

    df_result["OTF_Anteil"] = (
        total_otf * df_result["Menge"] / total_qty
        if total_qty > 0 else 0
    )

    otf_software = df_result[df_result["Typ"] == "Software"]["OTF_Anteil"].sum()
    otf_hardware = df_result[df_result["Typ"] == "Hardware"]["OTF_Anteil"].sum()

    col1, col2 = st.columns(2)
    col1.metric("💻 SUF (Software OTF)", f"{otf_software:,.2f} €")
    col2.metric("🖨️ Hardware OTF", f"{otf_hardware:,.2f} €")

    # -------------------------
    # Kontrollübersicht
    # -------------------------
    st.markdown("---")
    st.subheader("✅ Kontrollübersicht")

    total_mrr_calc = df_result["MRR_Monat"].sum()
    total_otf_calc = df_result["OTF_Anteil"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💻 SUF (Software)", f"{otf_software:,.2f} €")
        st.metric("🖨️ Hardware", f"{otf_hardware:,.2f} €")

    with col2:
        st.metric("🧾 OTF berechnet", f"{total_otf_calc:,.2f} €")
        st.metric("🧾 OTF Eingabe", f"{total_otf:,.2f} €")

    with col3:
        st.metric("💰 MRR / Monat", f"{total_mrr_calc:,.2f} €")
        st.metric("📆 MRR / Woche", f"{total_mrr_calc/4:,.2f} €")

    st.markdown("---")
    st.dataframe(df_result.round(2), use_container_width=True)
