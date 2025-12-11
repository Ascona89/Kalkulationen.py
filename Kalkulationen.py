# app.py
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# --------------------------
# Backend-Logfile (intern)
# --------------------------
LOG_FILE = "access_log.json"

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
    logs.append({"username": username, "role": role, "timestamp": datetime.now().isoformat()})
    save_logs(logs)

def get_daily_metrics():
    logs = load_logs()
    metrics = {}
    for log in logs:
        date = log["timestamp"][:10]
        metrics[date] = metrics.get(date, 0) + 1
    metrics_list = [{"date": k, "count": v} for k, v in sorted(metrics.items())]
    return metrics_list

# --------------------------
# Session State initialisieren
# --------------------------
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

# --------------------------
# Login
# --------------------------
PASSWORD_USER = "welovekb"
PASSWORD_ADMIN = "sebaforceo"

if not st.session_state.auth["logged_in"]:
    st.set_page_config(page_title="Kalkulations-App", layout="wide")
    st.title("🔐 Login erforderlich")
    password_input = st.text_input("Passwort eingeben:", type="password")
    if st.button("Login"):
        pw = password_input.strip()
        if pw == PASSWORD_USER:
            st.session_state.auth.update({"logged_in": True, "username": "user", "role": "user"})
            log_access("user", "user")
            st.success("Login erfolgreich! 🚀")
            st.experimental_rerun()
        elif pw == PASSWORD_ADMIN:
            st.session_state.auth.update({"logged_in": True, "username": "admin", "role": "admin"})
            log_access("admin", "admin")
            st.success("Admin Login erfolgreich! 🚀")
            st.experimental_rerun()
        else:
            st.error("❌ Falsches Passwort")
    st.stop()

# --------------------------
# Logout
# --------------------------
def logout():
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.experimental_rerun()

# --------------------------
# Sidebar
# --------------------------
if st.session_state.auth["role"] == "admin":
    page = st.sidebar.radio("Menü:", ["Backend", "Platform", "Cardpayment", "Pricing", "Logout"])
else:
    page = st.sidebar.radio("Menü:", ["Platform", "Cardpayment", "Pricing", "Logout"])

if page == "Logout":
    logout()

# --------------------------
# Backend (Admin)
# --------------------------
if page == "Backend":
    st.set_page_config(page_title="Kalkulations-App (Admin)", layout="wide")
    st.header("🛠️ Backend – Zugriffsanalyse")
    logs = load_logs()
    df = pd.DataFrame(logs)
    st.subheader("📈 Gesamtzugriffe")
    st.metric("Anzahl Zugriffe", len(df))
    
    st.subheader("🕒 Letzte 20 Zugriffe")
    if not df.empty:
        st.dataframe(df.tail(20), use_container_width=True)
    
    st.subheader("📊 Zugriffe pro Tag")
    metrics = get_daily_metrics()
    if metrics:
        mdf = pd.DataFrame(metrics)
        mdf['date'] = pd.to_datetime(mdf['date']).dt.date
        st.bar_chart(pd.Series(mdf['count'].values, index=mdf['date'].astype(str)))
    else:
        st.info("Noch keine Zugriffe vorhanden.")
    st.stop()

# --------------------------
# Platform Page
# --------------------------
def platform_page():
    st.header("🏁 Platform Kalkulation")
    col1, col2 = st.columns([2, 1.5])
    for key, default in [("revenue",0.0),("commission_pct",14.0),("avg_order_value",25.0),
                         ("service_fee",0.69),("OTF",0.0),("MRR",0.0),("contract_length",24)]:
        if key not in st.session_state: st.session_state[key] = default
    with col1:
        st.subheader("Eingaben")
        st.number_input("Revenue on platform (€)", step=250.0, key="revenue")
        st.number_input("Commission (%)", step=1.0, key="commission_pct")
        st.number_input("Average order value (€)", step=5.0, key="avg_order_value")
        st.number_input("Service Fee (€)", step=0.1, key="service_fee")
        total_cost = st.session_state.revenue*(st.session_state.commission_pct/100)+\
                     (0.7*st.session_state.revenue/st.session_state.avg_order_value if st.session_state.avg_order_value else 0)*st.session_state.service_fee
        st.markdown("### 💶 Cost on Platform")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Vertragsdetails")
        st.number_input("One Time Fee (OTF) (€)", step=100.0, key="OTF")
        st.number_input("Monthly Recurring Revenue (MRR) (€)", step=10.0, key="MRR")
        st.number_input("Contract length (Monate)", step=12, key="contract_length")
    transaction = 0.7*st.session_state.revenue/5*0.35
    cost_monthly = st.session_state.MRR + transaction
    saving_monthly = total_cost - cost_monthly
    saving_over_contract = saving_monthly * st.session_state.contract_length
    st.subheader("📊 Kennzahlen")
    st.info(f"- Cost monthly: {cost_monthly:,.2f} €\n"
            f"- Saving monthly: {saving_monthly:,.2f} €\n"
            f"- Saving over contract length: {saving_over_contract:,.2f} €")

# --------------------------
# Cardpayment Page
# --------------------------
def cardpayment_page():
    st.header("💳 Cardpayment Vergleich")
    col1, col2 = st.columns(2)
    defaults = {"rev_a":0.0,"sum_a":0.0,"mrr_a":0.0,"comm_a":1.39,"auth_a":0.0,
                "rev_o":0.0,"sum_o":0.0,"mrr_o":0.0,"comm_o":1.19,"auth_o":0.06}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
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
        st.number_input("Sum of payments", step=20.0, key="sum_o")
        st.number_input("Monthly Fee (€)", step=5.0, key="mrr_o")
        st.number_input("Commission (%)", step=0.01, key="comm_o")
        st.number_input("Authentification Fee (€)", key="auth_o")
    total_actual = st.session_state.rev_a*(st.session_state.comm_a/100)+st.session_state.sum_a*st.session_state.auth_a+st.session_state.mrr_a
    total_o = st.session_state.rev_o*(st.session_state.comm_o/100)+st.session_state.sum_o*st.session_state.auth_o+st.session_state.mrr_o
    saving = total_o-total_actual
    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.markdown(f"<div style='color:red; font-size:28px;'>💳 {total_actual:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Total Actual")
    col4.markdown(f"<div style='color:blue; font-size:28px;'>💳 {total_o:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Total Offer")
    col5.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving:,.2f} €</div>", unsafe_allow_html=True)
    col5.caption("Ersparnis (Offer - Actual)")

# --------------------------
# Pricing Page
# --------------------------
def pricing_page():
    st.header("💰 Pricing Kalkulation")
    software_data = {"Produkt":["Shop","App","POS","Pay","GAW"],
                     "Min_OTF":[365,15,365,35,50],"List_OTF":[999,49,999,49,100],
                     "Min_MRR":[50,15,49,5,100],"List_MRR":[119,49,89,25,100]}
    hardware_data = {"Produkt":["Ordermanager","POS inkl 1 Printer","Cash Drawer","Extra Printer","Additional Display","PAX"],
                     "Min_OTF":[135,350,50,99,100,225],"List_OTF":[299,1699,149,199,100,299],
                     "Min_MRR":[0,0,0,0,0,0],"List_MRR":[0,0,0,0,0,0]}
    df_sw = pd.DataFrame(software_data)
    df_hw = pd.DataFrame(hardware_data)
    for i in range(len(df_sw)):
        if f"sw_{i}" not in st.session_state: st.session_state[f"sw_{i}"]=0
    for i in range(len(df_hw)):
        if f"hw_{i}" not in st.session_state: st.session_state[f"hw_{i}"]=0
    if "gaw_value" not in st.session_state: st.session_state["gaw_value"]=50.0
    if "gaw_qty" not in st.session_state: st.session_state["gaw_qty"]=1
    col_sw,col_hw=st.columns(2)
    with col_sw:
        st.subheader("🧩 Software")
        for i in range(len(df_sw)):
            if df_sw["Produkt"][i]!="GAW":
                st.number_input(df_sw["Produkt"][i], min_value=0, step=1, key=f"sw_{i}")
        st.number_input("GAW Menge", step=1, key="gaw_qty")
        st.number_input("GAW Betrag (€)", min_value=0.0, value=50.0, step=25.0, key="gaw_value")
        df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            st.number_input(df_hw["Produkt"][i], min_value=0, step=1, key=f"hw_{i}")
        df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]
    df_sw["OTF_min_sum"] = df_sw.apply(lambda r:r["Menge"]*r["Min_OTF"] if r["Produkt"]!="GAW" else 0,axis=1)
    df_sw["OTF_list_sum"] = df_sw.apply(lambda r:r["Menge"]*r["List_OTF"] if r["Produkt"]!="GAW" else 0,axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"]*df_hw["Min_OTF"]
    df_hw["OTF_list_sum"] = df_hw["Menge"]*df_hw["List_OTF"]
    df_sw["MRR_min_sum"] = df_sw.apply(lambda r:r["Menge"]*r["Min_MRR"] if r["Produkt"]!="GAW" else 0,axis=1)
    df_sw["MRR_list_sum"] = df_sw.apply(lambda r:r["Menge"]*r["List_MRR"] if r["Produkt"]!="GAW" else 0,axis=1)
    df_hw["MRR_min_sum"] = df_hw["Menge"]*df_hw["Min_MRR"]
    df_hw["MRR_list_sum"] = df_hw["Menge"]*df_hw["List_MRR"]
    total_min_otf = df_sw["OTF_min_sum"].sum()+df_hw["OTF_min_sum"].sum()+st.session_state["gaw_qty"]*st.session_state["gaw_value"]
    total_list_otf = df_sw["OTF_list_sum"].sum()+df_hw["OTF_list_sum"].sum()+st.session_state["gaw_qty"]*st.session_state["gaw_value"]
    total_min_mrr = df_sw["MRR_min_sum"].sum()+df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum()+df_hw["MRR_list_sum"].sum()
    st.markdown(f"<div style='font-size:20px; color:#28a745;'>OTF List: {total_list_otf:,.2f} € | MRR List: {total_list_mrr:,.2f} €</div>", unsafe_allow_html=True)
    with st.expander("Preisdetails anzeigen"):
        df_show=pd.concat([df_sw,df_hw])[["Produkt","Min_OTF","List_OTF","Min_MRR","List_MRR"]]
        st.dataframe(df_show.style.format({"Min_OTF":"{:,.0f} €","List_OTF":"{:,.0f} €","Min_MRR":"{:,.0f} €","List_MRR":"{:,.0f} €"}), hide_index=True,use_container_width=True)
    st.markdown(f"<div style='font-size:20px; color:#e74c3c;'>OTF Min: {total_min_otf:,.2f} € | MRR Min: {total_min_mrr:,.2f} €</div>", unsafe_allow_html=True)

# --------------------------
# Page routing
# --------------------------
if page == "Platform":
    platform_page()
elif page == "Cardpayment":
    cardpayment_page()
elif page == "Pricing":
    pricing_page()
