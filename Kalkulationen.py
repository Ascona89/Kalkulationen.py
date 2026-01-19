import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

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

    if not df.empty:
        df["Datum"] = pd.to_datetime(df["created_at"]).dt.date
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df[df["success"]].groupby("Datum").size())

    new_pw = st.text_input("Neues User Passwort", type="password")
    if st.button("Passwort ändern") and new_pw:
        st.session_state["USER_PASSWORD"] = new_pw
        st.success("✅ Passwort geändert")

    st.stop()

# =====================================================
# 🔧 App Setup
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio("Wähle eine Kalkulation:", ["Platform", "Cardpayment", "Pricing"])

# =====================================================
# 🏁 PLATFORM
# =====================================================
if page == "Platform":
    st.header("🏁 Platform Kalkulation")

    st.session_state.setdefault("revenue", 0.0)
    st.session_state.setdefault("commission_pct", 14.0)
    st.session_state.setdefault("avg_order_value", 25.0)
    st.session_state.setdefault("service_fee", 0.69)
    st.session_state.setdefault("OTF", 0.0)
    st.session_state.setdefault("MRR", 0.0)
    st.session_state.setdefault("contract_length", 24)

    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Revenue (€)", step=250.0, key="revenue")
        st.number_input("Commission (%)", step=1.0, key="commission_pct")
        st.number_input("Avg Order Value (€)", step=5.0, key="avg_order_value")
        st.number_input("Service Fee (€)", step=0.1, key="service_fee")

    total_cost = (
        st.session_state.revenue * st.session_state.commission_pct / 100 +
        (0.7 * st.session_state.revenue / st.session_state.avg_order_value)
        * st.session_state.service_fee
    )

    with col2:
        st.number_input("OTF (€)", step=100.0, key="OTF")
        st.number_input("MRR (€)", step=10.0, key="MRR")
        st.number_input("Contract (Monate)", step=12, key="contract_length")

    transaction = 0.7 * st.session_state.revenue / 5 * 0.35
    cost_monthly = st.session_state.MRR + transaction

    st.info(
        f"Platform Cost: {total_cost:,.2f} €\n"
        f"Monthly Cost: {cost_monthly:,.2f} €"
    )

# =====================================================
# 💳 CARDPAYMENT
# =====================================================
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")

    for k, v in {
        "rev_a": 0.0, "sum_a": 0, "mrr_a": 0.0, "comm_a": 1.39, "auth_a": 0.0,
        "rev_o": 0.0, "sum_o": 0, "mrr_o": 0.0, "comm_o": 1.19, "auth_o": 0.06
    }.items():
        st.session_state.setdefault(k, v)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Actual")
        for k in ["rev_a","sum_a","mrr_a","comm_a","auth_a"]:
            st.number_input(k, key=k)

    with col2:
        st.subheader("Offer")
        st.session_state.rev_o = st.session_state.rev_a
        st.session_state.sum_o = st.session_state.sum_a
        for k in ["rev_o","sum_o","mrr_o","comm_o","auth_o"]:
            st.number_input(k, key=k)

    total_a = (
        st.session_state.rev_a * st.session_state.comm_a / 100 +
        st.session_state.sum_a * st.session_state.auth_a +
        st.session_state.mrr_a
    )

    total_o = (
        st.session_state.rev_o * st.session_state.comm_o / 100 +
        st.session_state.sum_o * st.session_state.auth_o +
        st.session_state.mrr_o
    )

    st.success(f"Ersparnis: {total_o - total_a:,.2f} €")

# =====================================================
# 💰 PRICING
# =====================================================
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    # ---------- SOFTWARE (inkl. CONNECT) ----------
    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 0, 0],
        "List_OTF": [999, 49, 999, 49, 0, 0],
        "Min_MRR": [50, 15, 49, 5, 15, 0],
        "List_MRR": [119, 49, 89, 25, 15, 0]
    })

    # ---------- HARDWARE ----------
    df_hw = pd.DataFrame({
        "Produkt": [
            "Ordermanager", "POS inkl 1 Printer", "Cash Drawer",
            "Extra Printer", "Additional Display", "PAX"
        ],
        "Min_OTF": [135, 350, 50, 99, 100, 225],
        "List_OTF": [299, 1699, 149, 199, 100, 299],
        "Min_MRR": [0]*6,
        "List_MRR": [0]*6
    })

    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(df_hw)):
        st.session_state.setdefault(f"hw_{i}", 0)

    df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

    # ---------- BERECHNUNG ----------
    list_otf = (df_sw["Menge"] * df_sw["List_OTF"]).sum() + (df_hw["Menge"] * df_hw["List_OTF"]).sum()
    min_otf  = (df_sw["Menge"] * df_sw["Min_OTF"]).sum()  + (df_hw["Menge"] * df_hw["Min_OTF"]).sum()
    list_mrr = (df_sw["Menge"] * df_sw["List_MRR"]).sum()
    min_mrr  = (df_sw["Menge"] * df_sw["Min_MRR"]).sum()

    # ---------- LIST PREISE (OBEN) ----------
    st.markdown("### 🧾 LIST PREISE")
    st.markdown(f"**OTF LIST gesamt:** {list_otf:,.2f} €")
    st.markdown(f"**MRR LIST gesamt:** {list_mrr:,.2f} €")
    st.markdown("---")

    # ---------- RABATT ----------
    col_discount, col_reason = st.columns([1, 3])
    with col_discount:
        discount = st.selectbox("Rabatt (%)", options=[0,5,10,15,20,25,30,35,40,45,50], index=0)
    with col_reason:
        reason = st.text_input("Grund")

    if discount > 0:
        list_otf_discounted = list_otf * (1 - discount/100)
        list_mrr_discounted = list_mrr * (1 - discount/100)
        st.info(f"Rabatt angewendet ({discount}%) – Grund: {reason}\n"
                f"OTF nach Rabatt: {list_otf_discounted:,.2f} €\n"
                f"MRR nach Rabatt: {list_mrr_discounted:,.2f} €")
    else:
        list_otf_discounted = list_otf
        list_mrr_discounted = list_mrr

    # ---------- EINGABEN ----------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Software")
        for i, p in enumerate(df_sw["Produkt"]):
            if p != "GAW":
                st.number_input(p, min_value=0, step=1, key=f"sw_{i}")

    with col2:
        st.subheader("Hardware")
        for i, p in enumerate(df_hw["Produkt"]):
            st.number_input(p, min_value=0, step=1, key=f"hw_{i}")

    # ---------- MIN PREISE (UNTEN) ----------
    st.markdown("---")
    st.markdown("### 🔻 MIN PREISE")
    st.markdown(f"**OTF MIN gesamt:** {min_otf:,.2f} €")
    st.markdown(f"**MRR MIN gesamt:** {min_mrr:,.2f} €")

# =====================================================
# Footer
# =====================================================
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
