import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# -------------------------------
# 🔐 Passwörter
# -------------------------------
USER_PASSWORD = "welovekb"
ADMIN_PASSWORD = "sebaforceo"

# -------------------------------
# 🧠 Supabase-Client
# -------------------------------
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

# -------------------------------
# 🧠 Session State
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "USER_PASSWORD" not in st.session_state:
    st.session_state["USER_PASSWORD"] = USER_PASSWORD

# -------------------------------
# 🔐 Login
# -------------------------------
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

# -------------------------------
# 🔧 App Setup
# -------------------------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio("Wähle eine Kalkulation:", ["Platform", "Cardpayment", "Pricing"])

# ======================================================
# 💰 PRICING
# ======================================================
if page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    # -------------------------------
    # Daten
    # -------------------------------
    software_data = {
        "Produkt": ["Shop", "App", "POS", "Pay", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 0],
        "List_OTF": [999, 49, 999, 49, 0],
        "Min_MRR": [50, 15, 49, 5, 0],
        "List_MRR": [119, 49, 89, 25, 0]
    }

    hardware_data = {
        "Produkt": [
            "Ordermanager",
            "POS inkl 1 Printer",
            "Cash Drawer",
            "Extra Printer",
            "Additional Display",
            "PAX"
        ],
        "Min_OTF": [135, 350, 50, 99, 100, 225],
        "List_OTF": [299, 1699, 149, 199, 100, 299],
        "Min_MRR": [0, 0, 0, 0, 0, 0],
        "List_MRR": [0, 0, 0, 0, 0, 0]
    }

    df_sw = pd.DataFrame(software_data)
    df_hw = pd.DataFrame(hardware_data)

    # -------------------------------
    # Session Init
    # -------------------------------
    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(df_hw)):
        st.session_state.setdefault(f"hw_{i}", 0)

    st.session_state.setdefault("gaw_qty", 1)
    st.session_state.setdefault("gaw_value", 50.0)

    col_sw, col_hw = st.columns(2)

    # -------------------------------
    # Software
    # -------------------------------
    with col_sw:
        st.subheader("🧩 Software")
        for i in range(len(df_sw)):
            if df_sw.loc[i, "Produkt"] != "GAW":
                st.number_input(df_sw.loc[i, "Produkt"], min_value=0, step=1, key=f"sw_{i}")

        st.number_input("GAW Menge", min_value=0, step=1, key="gaw_qty")
        st.number_input("GAW Betrag (€)", min_value=0.0, step=25.0, key="gaw_value")

        df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]

    # -------------------------------
    # Hardware
    # -------------------------------
    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            st.number_input(df_hw.loc[i, "Produkt"], min_value=0, step=1, key=f"hw_{i}")
        df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

    # -------------------------------
    # 🔢 Berechnungen
    # -------------------------------
    # MRR
    list_mrr = (df_sw["Menge"] * df_sw["List_MRR"]).sum()
    min_mrr = (df_sw["Menge"] * df_sw["Min_MRR"]).sum()

    # OTF Software + Hardware
    list_otf_sw = (df_sw["Menge"] * df_sw["List_OTF"]).sum()
    min_otf_sw = (df_sw["Menge"] * df_sw["Min_OTF"]).sum()

    list_otf_hw = (df_hw["Menge"] * df_hw["List_OTF"]).sum()
    min_otf_hw = (df_hw["Menge"] * df_hw["Min_OTF"]).sum()

    list_otf_total = list_otf_sw + list_otf_hw
    min_otf_total = min_otf_sw + min_otf_hw

    gaw_total = st.session_state["gaw_qty"] * st.session_state["gaw_value"]

    # -------------------------------
    # Anzeige
    # -------------------------------
    st.markdown("### 🧾 LIST PREISE")
    col1, col2 = st.columns(2)
    col1.markdown(f"**Software MRR LIST:** {list_mrr:,.2f} €")
    col2.markdown(f"**OTF LIST gesamt:** {list_otf_total:,.2f} €")

    st.markdown("### 🔻 MIN PREISE")
    col3, col4 = st.columns(2)
    col3.markdown(f"**Software MRR MIN:** {min_mrr:,.2f} €")
    col4.markdown(f"**OTF MIN gesamt:** {min_otf_total:,.2f} €")

    st.markdown(f"### 💰 GAW Gesamt: {gaw_total:,.2f} €")

    # -------------------------------
    # Tabelle
    # -------------------------------
    with st.expander("Preisdetails anzeigen"):
        df_show = pd.concat([df_sw, df_hw])[[
            "Produkt", "Min_OTF", "List_OTF", "Min_MRR", "List_MRR"
        ]]
        st.dataframe(
            df_show.style.format({
                "Min_OTF": "{:,.0f} €",
                "List_OTF": "{:,.0f} €",
                "Min_MRR": "{:,.0f} €",
                "List_MRR": "{:,.0f} €",
            }),
            hide_index=True,
            use_container_width=True
        )

# -------------------------------
# Footer
# -------------------------------
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)

