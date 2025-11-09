import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")

# ---------------- LOGIN SYSTEM ----------------
# Passwortgeschützter Zugriff
LOGIN_CODE = "welovekb"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Geschützter Zugang")
    st.write("Bitte gib den Zugangscode ein, um die Kalkulations-App zu starten.")
    password = st.text_input("Zugangscode", type="password")

    if st.button("Login"):
        if password == LOGIN_CODE:
            st.session_state["authenticated"] = True
            st.success("✅ Zugriff gewährt!")
            st.rerun()
        else:
            st.error("❌ Falscher Code. Bitte erneut versuchen.")
    st.stop()  # stoppt die App, bis Login erfolgreich

# ---------------- MAIN APP ----------------
st.title("📊 Kalkulations-App")

# Helper: Defaultwerte setzen
def init_session_state(defaults: dict):
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# Seitenmenü
page = st.sidebar.radio("Wähle eine Kalkulation:", ["Platform", "Cardpayment", "Pricing"])

# ---------------- PLATFORM ----------------
if page == "Platform":
    st.header("🏁 Platform Kalkulation")

    init_session_state({
        "revenue": 0.0, "commission_pct": 14.0, "avg_order_value": 25.0,
        "service_fee": 0.69, "OTF": 0.0, "MRR": 0.0, "contract_length": 24
    })

    col_left, col_right = st.columns([2, 1.4])

    with col_left:
        st.subheader("Eingaben")
        st.number_input("Revenue on platform (€)", key="revenue", step=250.0)
        st.number_input("Commission (%)", key="commission_pct", step=1.0)
        st.number_input("Average order value (€)", key="avg_order_value", step=5.0)
        st.number_input("Service Fee (€)", key="service_fee", step=0.1)

        total_cost = st.session_state.revenue * (st.session_state.commission_pct / 100) + (
            (0.7 * st.session_state.revenue / st.session_state.avg_order_value if st.session_state.avg_order_value else 0)
            * st.session_state.service_fee
        )
        st.markdown("### 💶 Cost on Platform")
        st.markdown(f"<div style='color:red; font-size:28px; font-weight:bold'>{total_cost:,.2f} €</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Vertragsdetails")
        st.number_input("One Time Fee (OTF) (€)", key="OTF", step=100.0)
        st.number_input("Monthly Recurring Revenue (MRR) (€)", key="MRR", step=10.0)
        st.number_input("Contract length (Monate)", key="contract_length", step=12)

    with col_right:
        transaction = 0.7 * st.session_state.revenue / 5 * 0.35
        cost_oyy_monthly = st.session_state.MRR + transaction
        saving_monthly = total_cost - cost_oyy_monthly
        saving_over_contract = saving_monthly * st.session_state.contract_length

        st.subheader("📊 Kennzahlen")
        st.metric("Cost OYY monthly", f"{cost_oyy_monthly:,.2f} €")
        st.metric("Saving monthly", f"{saving_monthly:,.2f} €")
        st.metric("Saving over contract length", f"{saving_over_contract:,.2f} €")

# ---------------- CARDPAYMENT ----------------
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")

    init_session_state({
        "rev_a": 0.0, "sum_a": 0, "mrr_a": 0.0,
        "comm_a": 1.39, "auth_a": 0.0,
        "rev_o": 0.0, "sum_o": 0, "mrr_o": 0.0,
        "comm_o": 1.19, "auth_o": 0.06
    })

    col_a, col_o = st.columns(2)
    with col_a:
        st.subheader("Actual")
        st.number_input("Revenue (€)", key="rev_a", step=250.0)
        st.number_input("Sum of payments", key="sum_a", step=20, format="%d")
        st.number_input("Monthly Fee (€)", key="mrr_a", step=5.0)
        st.number_input("Commission (%)", key="comm_a", step=0.01)
        st.number_input("Authentification Fee (€)", key="auth_a")

    with col_o:
        st.subheader("Offer")
        st.session_state.rev_o = st.session_state.rev_a
        st.session_state.sum_o = st.session_state.sum_a
        st.number_input("Revenue (€)", key="rev_o", step=250.0)
        st.number_input("Sum of payments", key="sum_o", step=20)
        st.number_input("Monthly Fee (€)", key="mrr_o", step=5.0)
        st.number_input("Commission (%)", key="comm_o", step=0.01)
        st.number_input("Authentification Fee (€)", key="auth_o")

    total_actual = st.session_state.rev_a * (st.session_state.comm_a / 100) + \
                   st.session_state.sum_a * st.session_state.auth_a + st.session_state.mrr_a
    total_offer = st.session_state.rev_o * (st.session_state.comm_o / 100) + \
                  st.session_state.sum_o * st.session_state.auth_o + st.session_state.mrr_o
    saving = total_offer - total_actual

    st.markdown("---")
    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("Total Actual", f"{total_actual:,.2f} €")
    rcol2.metric("Total Offer", f"{total_offer:,.2f} €")
    rcol3.metric("Ersparnis", f"{saving:,.2f} €")

# ---------------- PRICING ----------------
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    software = [
        {"Produkt":"Shop","Min_OTF":365,"List_OTF":999,"Min_MRR":50,"List_MRR":119},
        {"Produkt":"App","Min_OTF":15,"List_OTF":49,"Min_MRR":15,"List_MRR":49},
        {"Produkt":"POS","Min_OTF":365,"List_OTF":999,"Min_MRR":49,"List_MRR":89},
        {"Produkt":"Pay","Min_OTF":35,"List_OTF":49,"Min_MRR":5,"List_MRR":25},
        {"Produkt":"GAW","Min_OTF":50,"List_OTF":100,"Min_MRR":100,"List_MRR":100}
    ]
    hardware = [
        {"Produkt":"Ordermanager","Min_OTF":135,"List_OTF":299,"Min_MRR":0,"List_MRR":0},
        {"Produkt":"POS inkl 1 Printer","Min_OTF":350,"List_OTF":1699,"Min_MRR":0,"List_MRR":0},
        {"Produkt":"Cash Drawer","Min_OTF":50,"List_OTF":149,"Min_MRR":0,"List_MRR":0},
        {"Produkt":"Extra Printer","Min_OTF":99,"List_OTF":199,"Min_MRR":0,"List_MRR":0},
        {"Produkt":"Additional Display","Min_OTF":100,"List_OTF":100,"Min_MRR":0,"List_MRR":0},
        {"Produkt":"PAX","Min_OTF":225,"List_OTF":299,"Min_MRR":0,"List_MRR":0}
    ]

    for i in range(len(software)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(hardware)):
        st.session_state.setdefault(f"hw_{i}", 0)
    st.session_state.setdefault("gaw_qty", 1)
    st.session_state.setdefault("gaw_value", 50.0)

    sw_col, hw_col = st.columns(2)

    with sw_col:
        st.subheader("🧩 Software")
        for i, prod in enumerate(software):
            if prod["Produkt"] != "GAW":
                st.number_input(f"{prod['Produkt']} Menge", key=f"sw_{i}", min_value=0, step=1)
        st.number_input("GAW Menge", key="gaw_qty", min_value=0, step=1)
        st.number_input("GAW Betrag (€)", key="gaw_value", min_value=0.0, step=25.0)

        shop_selected = st.session_state.get("sw_0", 0) > 0
        pos_selected = st.session_state.get("sw_2", 0) > 0
        st.session_state.setdefault("hw_0", 0)
        st.session_state.setdefault("hw_1", 0)
        if shop_selected:
            if st.session_state["hw_0"] < 1:
                st.session_state["hw_0"] = 1
        if pos_selected:
            st.session_state["hw_0"] = 0
            if st.session_state["hw_1"] < 1:
                st.session_state["hw_1"] = 1

    with hw_col:
        st.subheader("🖥️ Hardware")
        for i, prod in enumerate(hardware):
            st.number_input(f"{prod['Produkt']}", key=f"hw_{i}", min_value=0, step=1)

    df_sw = pd.DataFrame(software)
    df_hw = pd.DataFrame(hardware)
    df_sw["Menge"] = [st.session_state.get(f"sw_{i}", 0) for i in range(len(df_sw))]
    gaw_index = df_sw.index[df_sw["Produkt"]=="GAW"].tolist()
    if gaw_index:
        df_sw.at[gaw_index[0], "Menge"] = st.session_state["gaw_qty"]
    df_hw["Menge"] = [st.session_state.get(f"hw_{i}", 0) for i in range(len(df_hw))]

    df_sw["OTF_min_sum"] = df_sw.apply(lambda r: r["Menge"]*r["Min_OTF"] if r["Produkt"]!="GAW" else 0, axis=1)
    df_sw["OTF_list_sum"] = df_sw.apply(lambda r: r["Menge"]*r["List_OTF"] if r["Produkt"]!="GAW" else 0, axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"]*df_hw["Min_OTF"]
    df_hw["OTF_list_sum"] = df_hw["Menge"]*df_hw["List_OTF"]

    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + st.session_state["gaw_qty"] * st.session_state["gaw_value"]
    total_list_otf = df_sw["OTF_list_sum"].sum() + df_hw["OTF_list_sum"].sum() + st.session_state["gaw_qty"] * st.session_state["gaw_value"]

    df_sw["MRR_min_sum"] = df_sw.apply(lambda r: r["Menge"]*r["Min_MRR"] if r["Produkt"]!="GAW" else 0, axis=1)
    df_sw["MRR_list_sum"] = df_sw.apply(lambda r: r["Menge"]*r["List_MRR"] if r["Produkt"]!="GAW" else 0, axis=1)
    df_hw["MRR_min_sum"] = df_hw["Menge"]*df_hw["Min_MRR"]
    df_hw["MRR_list_sum"] = df_hw["Menge"]*df_hw["List_MRR"]

    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum() + df_hw["MRR_list_sum"].sum()

    st.markdown("---")
    st.subheader("📊 Gesamtergebnisse")
    st.markdown(
        f"<div style='display:flex; gap:30px; font-size:18px; flex-wrap:wrap'>"
        f"<div style='color:#e74c3c; font-weight:600;'>OTF Min: {total_min_otf:,.2f} €</div>"
        f"<div style='color:#28a745; font-weight:600;'>OTF List: {total_list_otf:,.2f} €</div>"
        f"<div style='color:#e74c3c; font-weight:600;'>MRR Min: {total_min_mrr:,.2f} €</div>"
        f"<div style='color:#28a745; font-weight:600;'>MRR List: {total_list_mrr:,.2f} €</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    with st.expander("Preisdetails anzeigen"):
        df_show_sw = df_sw[["Produkt","Menge","Min_OTF","List_OTF","Min_MRR","List_MRR"]].copy()
        df_show_hw = df_hw[["Produkt","Menge","Min_OTF","List_OTF","Min_MRR","List_MRR"]].copy()
        df_show = pd.concat([df_show_sw, df_show_hw], ignore_index=True)
        for c in ["Min_OTF","List_OTF","Min_MRR","List_MRR"]:
            df_show[c] = df_show[c].map(lambda x: f"{x:,.0f} €")
        st.dataframe(df_show, use_container_width=True, hide_index=True)

# ---------------- FOOTER ----------------
st.markdown("""
<hr style="margin:20px 0;">
<p style='text-align:center; font-size:0.9rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
