import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------------------------------------
# 🔐 PASSWÖRTER
# ------------------------------------------------------------
USER_PASSWORD = "welovekb"
ADMIN_PASSWORD = "sebaforceo"

# ------------------------------------------------------------
# 🧠 SESSION STATE INITIALISIERUNG
# ------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "login_history" not in st.session_state:
    st.session_state.login_history = []

def log_attempt(role, success):
    st.session_state.login_history.append({
        "Rolle": role,
        "Zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Erfolg": success
    })

def login(password_input):
    global USER_PASSWORD, ADMIN_PASSWORD
    if password_input == USER_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        log_attempt("User", "Erfolg")
        st.success("Login erfolgreich! 🚀")
        st.rerun()
    elif password_input == ADMIN_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = True
        log_attempt("Admin", "Erfolg")
        st.success("Admin Login erfolgreich! 🚀")
        st.rerun()
    else:
        log_attempt("Unbekannt", "Fehlgeschlagen")
        st.error("❌ Falsches Passwort")

# ------------------------------------------------------------
# 🔐 LOGIN-BEREICH
# ------------------------------------------------------------
if not st.session_state.logged_in:
    st.title("🔐 Login erforderlich")
    password_input = st.text_input("Passwort", type="password")
    if st.button("Login"):
        login(password_input)
    st.stop()

# ------------------------------------------------------------
# 🔧 ADMIN DASHBOARD
# ------------------------------------------------------------
if st.session_state.is_admin:
    st.header("👑 Admin Dashboard")

    # --- Login-Historie ---
    st.subheader("Login-Historie")
    if st.session_state.login_history:
        df_history = pd.DataFrame(st.session_state.login_history)
        st.dataframe(df_history, use_container_width=True)
        csv = df_history.to_csv(index=False).encode("utf-8")
        st.download_button("Download Login-Historie als CSV", csv, "login_history.csv", "text/csv")
        
        # --- Übersicht Logins pro Tag ---
        df_history['Datum'] = pd.to_datetime(df_history['Zeit']).dt.date
        logins_per_day = df_history.groupby('Datum').size().reset_index(name='Anzahl Logins')
        st.subheader("📊 Logins pro Tag")
        st.dataframe(logins_per_day, use_container_width=True)
    else:
        st.info("Noch keine Login-Versuche vorhanden.")

    # --- Nutzerpasswort ändern ---
    st.subheader("Nutzer-Passwort ändern")
    new_user_pw = st.text_input("Neues Nutzer-Passwort", type="password")
    if st.button("Passwort ändern"):
        if new_user_pw:
            USER_PASSWORD = new_user_pw
            st.success("Nutzerpasswort erfolgreich geändert!")

    st.stop()

# ------------------------------------------------------------
# 🔧 SEITENKONFIGURATION
# ------------------------------------------------------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

def init_session_state(keys_defaults):
    for key, default in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

# ------------------------------------------------------------
# 📋 SEITENMENÜ
# ------------------------------------------------------------
page = st.sidebar.radio("Wähle eine Kalkulation:", ["Platform", "Cardpayment", "Pricing"])

# ------------------------------------------------------------
# 🏁 PLATFORM
# ------------------------------------------------------------
if page == "Platform":
    st.header("🏁 Platform Kalkulation")
    col1, col2 = st.columns([2, 1.5])
    init_session_state({
        "revenue": 0.0, "commission_pct": 14.0, "avg_order_value": 25.0,
        "service_fee": 0.69, "OTF": 0.0, "MRR": 0.0, "contract_length": 24
    })

    with col1:
        st.subheader("Eingaben")
        st.number_input("Revenue on platform (€)", step=250.0, key="revenue")
        st.number_input("Commission (%)", step=1.0, key="commission_pct")
        st.number_input("Average order value (€)", step=5.0, key="avg_order_value")
        st.number_input("Service Fee (€)", step=0.1, key="service_fee")

        total_cost = st.session_state.revenue * (st.session_state.commission_pct / 100) + \
                     (0.7 * st.session_state.revenue / st.session_state.avg_order_value if st.session_state.avg_order_value else 0) * st.session_state.service_fee
        st.markdown("### 💶 Cost on Platform")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Vertragsdetails")
        st.number_input("One Time Fee (OTF) (€)", step=100.0, key="OTF")
        st.number_input("Monthly Recurring Revenue (MRR) (€)", step=10.0, key="MRR")
        st.number_input("Contract length (Monate)", step=12, key="contract_length")

    transaction = 0.7 * st.session_state.revenue / 5 * 0.35
    cost_monthly = st.session_state.MRR + transaction
    saving_monthly = total_cost - cost_monthly
    saving_over_contract = saving_monthly * st.session_state.contract_length

    st.subheader("📊 Kennzahlen")
    st.info(f"- Cost monthly: {cost_monthly:,.2f} €\n"
            f"- Saving monthly: {saving_monthly:,.2f} €\n"
            f"- Saving over contract length: {saving_over_contract:,.2f} €")

# ------------------------------------------------------------
# 💳 CARDPAYMENT
# ------------------------------------------------------------
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    col1, col2 = st.columns(2)

    init_session_state({
        "rev_a": 0.0, "sum_a": 0.0, "mrr_a": 0.0,
        "comm_a": 1.39, "auth_a": 0.0,
        "rev_o": 0.0, "sum_o": 0.0, "mrr_o": 0.0,
        "comm_o": 1.19, "auth_o": 0.06
    })

    with col1:
        st.subheader("Actual")
        st.number_input("Revenue (€)", step=250.0, key="rev_a")
        st.number_input("Sum of payments", step=20, key="sum_a")
        st.number_input("Monthly Fee (€)", step=5.0, key="mrr_a")
        st.number_input("Commission (%)", step=0.01, key="comm_a")
        st.number_input("Authentification Fee (€)", key="auth_a")

    with col2:
        st.subheader("Offer")
        st.session_state.rev_o = st.session_state.rev_a
        st.session_state.sum_o = st.session_state.sum_a
        st.number_input("Revenue (€)", step=250.0, key="rev_o")
        st.number_input("Sum of payments", step=20, key="sum_o")
        st.number_input("Monthly Fee (€)", step=5.0, key="mrr_o")
        st.number_input("Commission (%)", step=0.01, key="comm_o")
        st.number_input("Authentification Fee (€)", key="auth_o")

    total_actual = st.session_state.rev_a * (st.session_state.comm_a / 100) + \
                   st.session_state.sum_a * st.session_state.auth_a + st.session_state.mrr_a
    total_o = st.session_state.rev_o * (st.session_state.comm_o / 100) + \
              st.session_state.sum_o * st.session_state.auth_o + st.session_state.mrr_o
    saving = total_o - total_actual

    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.markdown(f"<div style='color:red; font-size:28px;'>💳 {total_actual:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Total Actual")
    col4.markdown(f"<div style='color:blue; font-size:28px;'>💳 {total_o:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Total Offer")
    col5.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving:,.2f} €</div>", unsafe_allow_html=True)
    col5.caption("Ersparnis (Offer - Actual)")

# ------------------------------------------------------------
# 💰 PRICING
# ------------------------------------------------------------
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    software_data = {
        "Produkt": ["Shop", "App", "POS", "Pay", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 50],
        "List_OTF": [999, 49, 999, 49, 100],
        "Min_MRR": [50, 15, 49, 5, 100],
        "List_MRR": [119, 49, 89, 25, 100],
    }
    hardware_data = {
        "Produkt": ["Ordermanager", "POS inkl 1 Printer", "Cash Drawer",
                    "Extra Printer", "Additional Display", "PAX"],
        "Min_OTF": [135, 350, 50, 99, 100, 225],
        "List_OTF": [299, 1699, 149, 199, 100, 299],
        "Min_MRR": [0, 0, 0, 0, 0, 0],
        "List_MRR": [0, 0, 0, 0, 0, 0],
    }

    df_sw = pd.DataFrame(software_data)
    df_hw = pd.DataFrame(hardware_data)

    for i in range(len(df_sw)):
        if f"sw_{i}" not in st.session_state: st.session_state[f"sw_{i}"] = 0
    for i in range(len(df_hw)):
        if f"hw_{i}" not in st.session_state: st.session_state[f"hw_{i}"] = 0
    if "gaw_value" not in st.session_state: st.session_state["gaw_value"] = 50.0
    if "gaw_qty" not in st.session_state: st.session_state["gaw_qty"] = 1

    col_sw, col_hw = st.columns(2)

    # --- Software ---
    with col_sw:
        for i in range(len(df_sw)):
            if df_sw["Produkt"][i] != "GAW":
                st.number_input(df_sw["Produkt"][i], min_value=0, step=1, key=f"sw_{i}")
        st.number_input("GAW Menge", step=1, key="gaw_qty")
        st.number_input("GAW Betrag (€)", min_value=0.0, value=50.0, step=25.0, key="gaw_value")
        df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]

    # --- Hardware ---
    with col_hw:
        for i in range(len(df_hw)):
            st.number_input(df_hw["Produkt"][i], min_value=0, step=1, key=f"hw_{i}")
        df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

    # --- Live List Price Berechnung ---
    total_list_mrr = df_sw["Menge"].dot(df_sw["List_MRR"])
    total_list_otf = df_hw["Menge"].dot(df_hw["List_OTF"]) + st.session_state["gaw_qty"]*st.session_state["gaw_value"]

    # Anzeige der List Prices mit header-Schriftgröße
    col_sw.header(f"🧩 Software (MRR List: {total_list_mrr:,.2f} €)")
    col_hw.header(f"🖥️ Hardware (OTF List: {total_list_otf:,.2f} €)")

    # --- Kalkulation ---
    df_sw["OTF_min_sum"] = df_sw.apply(lambda r: r["Menge"] * r["Min_OTF"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_sw["MRR_min_sum"] = df_sw.apply(lambda r: r["Menge"] * r["Min_MRR"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"] * df_hw["Min_OTF"]
    df_hw["MRR_min_sum"] = df_hw["Menge"] * df_hw["Min_MRR"]

    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + st.session_state["gaw_qty"]*st.session_state["gaw_value"]
    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()

    # --- Tabelle anzeigen ---
    with st.expander("Preisdetails anzeigen"):
        df_show = pd.concat([df_sw, df_hw])[["Produkt", "Min_OTF", "List_OTF", "Min_MRR", "List_MRR"]]
        st.dataframe(df_show.style.format({
            "Min_OTF": "{:,.0f} €",
            "List_OTF": "{:,.0f} €",
            "Min_MRR": "{:,.0f} €",
            "List_MRR": "{:,.0f} €",
        }), hide_index=True, use_container_width=True)

    # --- MIN-Werte unterhalb der Tabelle ---
    st.markdown("---")
    st.markdown(f"<div style='font-size:28px; color:#e74c3c;'>OTF Min: {total_min_otf:,.2f} €</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:28px; color:#e74c3c;'>MRR Min: {total_min_mrr:,.2f} €</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# 😉 Footer
# ------------------------------------------------------------
st.markdown("""
<hr style="margin:20px 0;">
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
