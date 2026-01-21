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
# 🧠 Session State Initialisierung
# =====================================================
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("is_admin", False)
st.session_state.setdefault("USER_PASSWORD", USER_PASSWORD)

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
# 🔧 App Setup
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio("Wähle eine Kalkulation:", ["Platform", "Cardpayment", "Pricing", "Radien"])

# =====================================================
# 🏁 Platform
# =====================================================
if page == "Platform":
    st.header("🏁 Platform Kalkulation")
    # ... hier kommt unveränderter Platform-Code ...

# =====================================================
# 💳 Cardpayment
# =====================================================
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    # ... hier kommt unveränderter Cardpayment-Code ...

# =====================================================
# 💰 Pricing
# =====================================================
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    # --- Software ---
    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 0, 0],
        "List_OTF": [999, 49, 999, 49, 0, 0],
        "Min_MRR": [50, 15, 49, 5, 15, 0],
        "List_MRR": [119, 49, 89, 25, 15, 0]
    })

    # --- Hardware Kauf ---
    df_hw_kauf = pd.DataFrame({
        "Produkt":["Ordermanager","POS inkl 1 Printer","Cash Drawer","PAX"],
        "Min_OTF":[9.0,23.33,3.33,15.0],
        "List_OTF":[19.93,113.27,9.93,19.93],
        "Min_MRR":[0]*4,
        "List_MRR":[0]*4
    })

    # --- Hardware Leasing (MRR = List_OTF) ---
    df_hw_lease = df_hw_kauf.copy()
    df_hw_lease["Min_MRR"] = df_hw_lease["Min_OTF"]
    df_hw_lease["List_MRR"] = df_hw_lease["List_OTF"]

    # --- Session State Mengen ---
    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}",0)
    for i in range(len(df_hw_kauf)):
        st.session_state.setdefault(f"hwk_{i}",0)
        st.session_state.setdefault(f"hwl_{i}",0)

    # --- Eingaben in drei Spalten ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Software")
        for i, p in enumerate(df_sw["Produkt"]):
            st.number_input(p, min_value=0, step=1, key=f"sw_{i}")
    with col2:
        st.subheader("Hardware Kauf")
        for i, p in enumerate(df_hw_kauf["Produkt"]):
            st.number_input(p, min_value=0, step=1, key=f"hwk_{i}")
    with col3:
        st.subheader("Hardware Leasing")
        for i, p in enumerate(df_hw_lease["Produkt"]):
            st.number_input(p, min_value=0, step=1, key=f"hwl_{i}")

    # --- Berechnung der Mengen ---
    df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    df_hw_kauf["Menge"] = [st.session_state[f"hwk_{i}"] for i in range(len(df_hw_kauf))]
    df_hw_lease["Menge"] = [st.session_state[f"hwl_{i}"] for i in range(len(df_hw_lease))]

    # --- Berechnung Preise ---
    mrr_sw = (df_sw["Menge"] * df_sw["List_MRR"]).sum()
    otf_hwk = (df_hw_kauf["Menge"] * df_hw_kauf["List_OTF"]).sum()
    mrr_hwl = mrr_sw + (df_hw_lease["Menge"] * df_hw_lease["List_MRR"]).sum()

    # --- LIST Preise und Rabattrechner unverändert ---
    st.markdown("### 🧾 LIST PREISE")
    st.markdown(f"**MRR Software (List):** {mrr_sw:,.2f} €")
    st.markdown(f"**OTF Hardware Kauf (List):** {otf_hwk:,.2f} €")
    st.markdown(f"**MRR Hardware Leasing:** {mrr_hwl:,.2f} €")
    st.markdown("---")

# =====================================================
# 🌐 Radien
# =====================================================
elif page == "Radien":
    st.header("📍 Radien Kalkulation")
    st.subheader("Frei wählbare Radien (in km)")
    radien_input = st.text_area("Trage Radien ein, getrennt durch Komma", "1,2,3")
    try:
        radien = [float(r.strip()) for r in radien_input.split(",") if r.strip()]
        st.success(f"Eingegebene Radien: {radien}")
    except:
        st.error("Bitte gültige Zahlen eingeben, getrennt durch Komma.")

# =====================================================
# Footer
# =====================================================
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
