import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# ============================================================
#               🔐 FILE DEFINITIONS (Backend)
# ============================================================
LOG_FILE = "access_log.json"
PW_FILE = "passwords.json"

# ============================================================
#               🔐 PASSWORD HANDLING
# ============================================================
def load_passwords():
    if not os.path.exists(PW_FILE):
        with open(PW_FILE, "w") as f:
            json.dump({"user_password": "welovekb"}, f)
    with open(PW_FILE, "r") as f:
        return json.load(f)

def save_passwords(data):
    with open(PW_FILE, "w") as f:
        json.dump(data, f, indent=2)

password_store = load_passwords()

PASSWORD_ADMIN = "sebaforceo"
PASSWORD_USER = password_store["user_password"]

# ============================================================
#               📊 ACCESS LOGGING
# ============================================================
def load_logs():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_access(username, role):
    logs = load_logs()
    logs.append({
        "username": username,
        "role": role,
        "timestamp": datetime.now().isoformat()
    })
    save_logs(logs)

def get_daily_metrics():
    logs = load_logs()
    metrics = {}
    for log in logs:
        date = log["timestamp"][:10]
        metrics[date] = metrics.get(date, 0) + 1
    return [{"date": k, "count": v} for k, v in sorted(metrics.items())]

# ============================================================
#               🧠 SESSION STATE LOGIN
# ============================================================
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "role": None, "username": None}

# ============================================================
#               🔐 LOGIN PAGE
# ============================================================
if not st.session_state.auth["logged_in"]:
    st.set_page_config(page_title="Kalkulations-App")
    st.title("🔐 Login erforderlich")

    pw = st.text_input("Passwort eingeben:", type="password")

    if st.button("Login"):
        if pw == PASSWORD_USER:
            st.session_state.auth = {"logged_in": True, "role": "user", "username": "user"}
            log_access("user", "user")
            st.success("Login erfolgreich!")
            st.rerun()

        elif pw == PASSWORD_ADMIN:
            st.session_state.auth = {"logged_in": True, "role": "admin", "username": "admin"}
            log_access("admin", "admin")
            st.success("Admin Login erfolgreich!")
            st.rerun()

        else:
            st.error("❌ Falsches Passwort")

    st.stop()

# ============================================================
#               🔐 LOGOUT FUNCTION
# ============================================================
def logout():
    st.session_state.auth = {"logged_in": False, "role": None, "username": None}
    st.rerun()

# ============================================================
#               📌 SIDEBAR
# ============================================================
if st.session_state.auth["role"] == "admin":
    page = st.sidebar.radio("Navigation", [
        "Backend", "Passwort ändern", "Platform", "Cardpayment", "Pricing", "Logout"
    ])
else:
    page = st.sidebar.radio("Navigation", [
        "Platform", "Cardpayment", "Pricing", "Logout"
    ])

if page == "Logout":
    logout()

# ============================================================
#               🛠️ ADMIN BACKEND
# ============================================================
if page == "Backend":
    st.header("🛠️ Backend – Zugriffsanalyse")

    logs = load_logs()
    df = pd.DataFrame(logs)

    st.subheader("📈 Gesamtzugriffe")
    st.metric("Total", len(df))

    st.subheader("🕒 Letzte 20 Zugriffe")
    if not df.empty:
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.info("Noch keine Log-Einträge.")

    daily = get_daily_metrics()
    if daily:
        chart_df = pd.DataFrame(daily)
        st.subheader("📊 Zugriffe pro Tag")
        st.bar_chart(chart_df.set_index("date"))
    else:
        st.info("Noch keine Zugriffsdaten verfügbar.")

    st.stop()

# ============================================================
#               🔐 PASSWORT ÄNDERN (Admin)
# ============================================================
if page == "Passwort ändern":
    st.header("🔐 Passwort für normalen User ändern")

    new_pw = st.text_input("Neues Passwort:", type="password")
    confirm_pw = st.text_input("Passwort bestätigen:", type="password")

    if st.button("Speichern"):
        if new_pw.strip() == "":
            st.error("Passwort darf nicht leer sein.")
        elif new_pw != confirm_pw:
            st.error("Passwörter stimmen nicht überein.")
        else:
            password_store["user_password"] = new_pw
            save_passwords(password_store)
            st.success("Passwort erfolgreich geändert!")

    st.stop()

# ============================================================
#               📊 PLATFORM PAGE
# ============================================================
if page == "Platform":
    st.header("🏁 Platform Kalkulation")

    def init_state(keys):
        for key, val in keys.items():
            if key not in st.session_state:
                st.session_state[key] = val

    init_state({
        "revenue": 0.0, "commission_pct": 14.0, "avg_order_value": 25.0,
        "service_fee": 0.69, "OTF": 0.0, "MRR": 0.0, "contract_length": 24
    })

    col1, col2 = st.columns([2, 1.5])

    with col1:
        st.subheader("Eingaben")
        st.number_input("Revenue (€)", step=100.0, key="revenue")
        st.number_input("Commission (%)", step=1.0, key="commission_pct")
        st.number_input("Average order value (€)", step=5.0, key="avg_order_value")
        st.number_input("Service Fee (€)", step=0.1, key="service_fee")

        total_cost = (
            st.session_state.revenue * (st.session_state.commission_pct / 100)
            + (0.7 * st.session_state.revenue / st.session_state.avg_order_value) * st.session_state.service_fee
        )

        st.markdown("### 💶 Cost on Platform")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>",
                    unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Vertragsdetails")
        st.number_input("One Time Fee OTF (€)", step=100.0, key="OTF")
        st.number_input("MRR (€)", step=10.0, key="MRR")
        st.number_input("Contract length (Monate)", step=12, key="contract_length")

    transaction = 0.7 * st.session_state.revenue / 5 * 0.35
    cost_monthly = st.session_state.MRR + transaction
    saving_monthly = total_cost - cost_monthly
    saving_contract = saving_monthly * st.session_state.contract_length

    st.subheader("📊 Kennzahlen")
    st.info(
        f"- Cost monthly: {cost_monthly:,.2f} €\n"
        f"- Saving monthly: {saving_monthly:,.2f} €\n"
        f"- Saving over contract: {saving_contract:,.2f} €"
    )

# ============================================================
#               💳 CARDPAYMENT PAGE
# ============================================================
if page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")

    def init(keys):
        for k, v in keys.items():
            if k not in st.session_state:
                st.session_state[k] = v

    init({
        "rev_a": 0.0, "sum_a": 0.0, "mrr_a": 0.0,
        "comm_a": 1.39, "auth_a": 0.0,
        "rev_o": 0.0, "sum_o": 0.0, "mrr_o": 0.0,
        "comm_o": 1.19, "auth_o": 0.06
    })

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Actual")
        st.number_input("Revenue (€)", key="rev_a")
        st.number_input("Sum of payments", key="sum_a")
        st.number_input("MRR (€)", key="mrr_a")
        st.number_input("Commission (%)", key="comm_a")
        st.number_input("Authentification Fee (€)", key="auth_a")

    with col2:
        st.subheader("Offer")
        st.session_state.rev_o = st.session_state.rev_a
        st.session_state.sum_o = st.session_state.sum_a

        st.number_input("Revenue (€)", key="rev_o")
        st.number_input("Sum of payments", key="sum_o")
        st.number_input("MRR (€)", key="mrr_o")
        st.number_input("Commission (%)", key="comm_o")
        st.number_input("Authentification Fee (€)", key="auth_o")

    total_actual = (
        st.session_state.rev_a * (st.session_state.comm_a / 100)
        + st.session_state.sum_a * st.session_state.auth_a
        + st.session_state.mrr_a
    )

    total_offer = (
        st.session_state.rev_o * (st.session_state.comm_o / 100)
        + st.session_state.sum_o * st.session_state.auth_o
        + st.session_state.mrr_o
    )

    saving = total_offer - total_actual

    st.markdown("---")
    st.subheader("Ergebnisse")

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div style='color:red;font-size:28px;'>{total_actual:,.2f} €</div>", unsafe_allow_html=True)
    c1.caption("Total Actual")

    c2.markdown(f"<div style='color:blue;font-size:28px;'>{total_offer:,.2f} €</div>", unsafe_allow_html=True)
    c2.caption("Total Offer")

    c3.markdown(f"<div style='color:green;font-size:28px;'>{saving:,.2f} €</div>", unsafe_allow_html=True)
    c3.caption("Ersparnis (Offer - Actual)")

# ============================================================
#               💰 PRICING PAGE
# ============================================================
if page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    software_data = {
        "Produkt": ["Shop", "App", "POS", "Pay", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 50],
        "List_OTF": [999, 49, 999, 49, 100],
        "Min_MRR": [50, 15, 49, 5, 100],
        "List_MRR": [119, 49, 89, 25, 100],
    }

    hardware_data = {
        "Produkt": ["Ordermanager", "POS inkl 1 Printer", "Cash Drawer", "Extra Printer", "Additional Display", "PAX"],
        "Min_OTF": [135, 350, 50, 99, 100, 225],
        "List_OTF": [299, 1699, 149, 199, 100, 299],
        "Min_MRR": [0, 0, 0, 0, 0, 0],
        "List_MRR": [0, 0, 0, 0, 0, 0],
    }

    df_sw = pd.DataFrame(software_data)
    df_hw = pd.DataFrame(hardware_data)

    # Init Menge in Session State
    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(df_hw)):
        st.session_state.setdefault(f"hw_{i}", 0)

    st.session_state.setdefault("gaw_value", 50.0)
    st.session_state.setdefault("gaw_qty", 1)

    col_sw, col_hw = st.columns(2)

    # SW
    with col_sw:
        st.subheader("🧩 Software")
        for i in range(len(df_sw)):
            if df_sw["Produkt"][i] != "GAW":
                st.number_input(df_sw["Produkt"][i], min_value=0, step=1, key=f"sw_{i}")

        shop_selected = st.session_state["sw_0"] > 0
        pos_selected = st.session_state["sw_2"] > 0

        if shop_selected:
            if st.session_state["hw_0"] < 1:
                st.session_state["hw_0"] = 1

        if pos_selected:
            st.session_state["hw_0"] = 0
            if st.session_state["hw_1"] < 1:
                st.session_state["hw_1"] = 1

        st.number_input("GAW Menge", step=1, key="gaw_qty")
        st.number_input("GAW Betrag (€)", step=10.0, key="gaw_value")

        df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]

    # HW
    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            st.number_input(df_hw["Produkt"][i], min_value=0, step=1, key=f"hw_{i}")
        df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

    # Kalkulation OTF/MRR
    df_sw["OTF_min_sum"] = df_sw.apply(lambda r: r["Menge"] * r["Min_OTF"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_sw["OTF_list_sum"] = df_sw.apply(lambda r: r["Menge"] * r["List_OTF"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"] * df_hw["Min_OTF"]
    df_hw["OTF_list_sum"] = df_hw["Menge"] * df_hw["List_OTF"]

    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + st.session_state["gaw_qty"] * st.session_state["gaw_value"]
    total_list_otf = df_sw["OTF_list_sum"].sum() + df_hw["OTF_list_sum"].sum() + st.session_state["gaw_qty"] * st.session_state["gaw_value"]

    df_sw["MRR_min_sum"] = df_sw["Menge"] * df_sw["Min_MRR"]
    df_sw["MRR_list_sum"] = df_sw["Menge"] * df_sw["List_MRR"]
    df_hw["MRR_min_sum"] = df_hw["Menge"] * df_hw["Min_MRR"]
    df_hw["MRR_list_sum"] = df_hw["Menge"] * df_hw["List_MRR"]

    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum() + df_hw["MRR_list_sum"].sum()

    # OUTPUT
    st.markdown("---")
    st.subheader("📊 OTF List (oben)")
    st.markdown(f"<div style='font-size:26px; color:green;'>List OTF: {total_list_otf:,.2f} €</div>", unsafe_allow_html=True)

    st.subheader("📊 Preisdetails")
    df_show = pd.concat([df_sw, df_hw])[["Produkt", "Min_OTF", "List_OTF", "Min_MRR", "List_MRR"]]
    st.dataframe(df_show, use_container_width=True)

    st.subheader("📉 OTF Min (unten)")
    st.markdown(f"<div style='font-size:26px; color:red;'>Min OTF: {total_min_otf:,.2f} €</div>", unsafe_allow_html=True)
