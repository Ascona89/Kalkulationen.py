import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# ------------------------------------------------------------
# 🔐 PASSWÖRTER
# ------------------------------------------------------------
USER_PASSWORD = "welovekb"
ADMIN_PASSWORD = "sebaforceo"

# ------------------------------------------------------------
# 🧠 SUPABASE INITIALISIERUNG
# ------------------------------------------------------------
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def log_attempt(role, success):
    supabase.table("login_events").insert({
        "role": role,
        "success": success
    }).execute()

# ------------------------------------------------------------
# 🧠 SESSION STATE
# ------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ------------------------------------------------------------
# 🔐 LOGIN
# ------------------------------------------------------------
def login(password_input):
    if password_input == USER_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        log_attempt("User", True)
        st.rerun()
    elif password_input == ADMIN_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = True
        log_attempt("Admin", True)
        st.rerun()
    else:
        log_attempt("Unknown", False)
        st.error("❌ Falsches Passwort")

if not st.session_state.logged_in:
    st.title("🔐 Login erforderlich")
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        login(pw)
    st.stop()

# ------------------------------------------------------------
# 👑 ADMIN BACKEND
# ------------------------------------------------------------
if st.session_state.is_admin:
    st.header("👑 Admin Dashboard")

    data = supabase.table("login_events").select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(data.data)

    if not df.empty:
        df["Datum"] = pd.to_datetime(df["created_at"]).dt.date

        st.subheader("📄 Login-Historie")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Logins pro Tag")
        logins_per_day = (
            df[df["success"] == True]
            .groupby("Datum")
            .size()
            .reset_index(name="Logins")
        )
        st.dataframe(logins_per_day, use_container_width=True)
        st.bar_chart(logins_per_day.set_index("Datum"))

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("CSV Export", csv, "login_history.csv", "text/csv")
    else:
        st.info("Noch keine Login-Daten vorhanden.")

    st.stop()

# ------------------------------------------------------------
# 🔧 APP KONFIGURATION
# ------------------------------------------------------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio("Bereich wählen", ["Platform", "Cardpayment", "Pricing"])

# ------------------------------------------------------------
# 🏁 PLATFORM
# ------------------------------------------------------------
if page == "Platform":
    st.header("🏁 Platform Kalkulation")
    revenue = st.number_input("Revenue (€)", 0.0, step=250.0)
    commission = st.number_input("Commission (%)", 14.0)
    aov = st.number_input("Average Order Value (€)", 25.0)
    fee = st.number_input("Service Fee (€)", 0.69)

    total_cost = revenue * (commission / 100) + (
        (0.7 * revenue / aov if aov else 0) * fee
    )

    st.markdown("### 💶 Cost on Platform")
    st.markdown(
        f"<div style='font-size:28px;color:red'>{total_cost:,.2f} €</div>",
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# 💳 CARDPAYMENT
# ------------------------------------------------------------
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")

    rev = st.number_input("Revenue (€)", 0.0)
    tx = st.number_input("Transactions", 0)
    comm = st.number_input("Commission (%)", 1.39)
    auth = st.number_input("Auth Fee (€)", 0.0)
    mrr = st.number_input("Monthly Fee (€)", 0.0)

    total = rev * (comm / 100) + tx * auth + mrr

    st.markdown(
        f"<div style='font-size:28px;color:blue'>💳 {total:,.2f} €</div>",
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# 💰 PRICING
# ------------------------------------------------------------
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    # Software Daten
    software = {
        "Produkt": ["Shop", "App", "POS", "Pay", "GAW"],
        "List_MRR": [119, 49, 89, 25, 100],
        "Min_MRR": [50, 15, 49, 5, 100]
    }

    # Hardware Daten
    hardware = {
        "Produkt": ["Ordermanager", "POS inkl Printer", "PAX"],
        "List_OTF": [299, 1699, 299],
        "Min_OTF": [135, 350, 225]
    }

    df_sw = pd.DataFrame(software)
    df_hw = pd.DataFrame(hardware)

    col_sw, col_hw = st.columns(2)

    # --- Software Menge ---
    with col_sw:
        st.subheader("🧩 Software")
        qty_sw = []
        for p in df_sw["Produkt"]:
            qty_sw.append(st.number_input(p, 0, step=1))

    # --- Hardware Menge ---
    with col_hw:
        st.subheader("🖥️ Hardware")
        qty_hw = []
        for p in df_hw["Produkt"]:
            qty_hw.append(st.number_input(p, 0, step=1))

    df_sw["Menge"] = qty_sw
    df_hw["Menge"] = qty_hw

    # --- List Prices Anzeige ---
    list_mrr = (df_sw["Menge"] * df_sw["List_MRR"]).sum()
    list_otf = (df_hw["Menge"] * df_hw["List_OTF"]).sum()

    col_sw.header(f"🧩 Software (MRR List: {list_mrr:,.2f} €)")
    col_hw.header(f"🖥️ Hardware (OTF List: {list_otf:,.2f} €)")

    # --- Min Werte unterhalb ---
    min_mrr = (df_sw["Menge"] * df_sw["Min_MRR"]).sum()
    min_otf = (df_hw["Menge"] * df_hw["Min_OTF"]).sum()

    st.markdown("---")
    st.markdown(f"### 🔻 MRR Min: {min_mrr:,.2f} €")
    st.markdown(f"### 🔻 OTF Min: {min_otf:,.2f} €")

# ------------------------------------------------------------
# 😉 FOOTER
# ------------------------------------------------------------
st.markdown("""
<hr>
<p style='text-align:center;color:gray;font-size:0.8rem'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
