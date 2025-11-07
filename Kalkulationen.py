import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 🔧 Seitenkonfiguration
# ------------------------------------------------------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

# ------------------------------------------------------------
# 🧠 Session State Initialisierung
# ------------------------------------------------------------
def init_session_state(keys_defaults):
    for key, default in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

# ------------------------------------------------------------
# 📋 Seitenmenü
# ------------------------------------------------------------
page = st.sidebar.radio("Wähle eine Kalkulation:", ["Competitor", "Cardpayment", "Pricing"])

# ------------------------------------------------------------
# 🏁 COMPETITOR
# ------------------------------------------------------------
if page == "Competitor":
    st.header("🏁 Competitor Kalkulation")

    col1, col2 = st.columns([2, 1.5])
    init_session_state({
        "revenue": 0.0, "commission_pct": 14.0, "avg_order_value": 25.0,
        "service_fee": 0.69, "OTF": 0.0, "MRR": 0.0, "contract_length": 24
    })

    with col1:
        st.subheader("Eingaben")
        st.number_input("Revenue on platform (€)", step=250.0, key="revenue",
                        help="Gesamter Umsatz auf der Plattform")
        st.number_input("Commission (%)", step=1.0, key="commission_pct",
                        help="Provision in Prozent")
        st.number_input("Average order value (€)", step=5.0, key="avg_order_value",
                        help="Durchschnittlicher Bestellwert")
        st.number_input("Service Fee (€)", step=0.1, key="service_fee",
                        help="Transaktionsgebühr pro Onlinezahlung")

        st.markdown("---")
        st.subheader("Vertragsdetails")
        st.number_input("One Time Fee (OTF) (€)", step=100.0, key="OTF")
        st.number_input("Monthly Recurring Revenue (MRR) (€)", step=10.0, key="MRR")
        st.number_input("Contract length (Monate)", step=12, key="contract_length")

    total_cost = st.session_state.revenue * (st.session_state.commission_pct / 100) + (
        (0.7 * st.session_state.revenue / st.session_state.avg_order_value if st.session_state.avg_order_value else 0)
        * st.session_state.service_fee
    )
    transaction = 0.7 * st.session_state.revenue / 5 * 0.35
    cost_oyy_monthly = st.session_state.MRR + transaction
    saving_monthly = total_cost - cost_oyy_monthly
    saving_over_contract = saving_monthly * st.session_state.contract_length

    with col2:
        st.markdown("### 💶 Total Cost")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>",
                    unsafe_allow_html=True)

    st.subheader("📊 Kennzahlen")
    st.info(f"- Cost OYY monthly: {cost_oyy_monthly:,.2f} €\n"
            f"- Saving monthly: {saving_monthly:,.2f} €\n"
            f"- Saving over contract length: {saving_over_contract:,.2f} €")

# ------------------------------------------------------------
# 💳 CARDPAYMENT
# ------------------------------------------------------------
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    col1, col2 = st.columns(2)

    init_session_state({
        "rev_c": 0.0, "sum_c": 0.0, "mrr_c": 0.0,
        "comm_c": 1.39, "auth_c": 0.0,
        "rev_o": 0.0, "sum_o": 0.0, "mrr_o": 0.0,
        "comm_o": 1.19, "auth_o": 0.06
    })

    with col1:
        st.subheader("Competitor")
        st.number_input("Revenue (€)", step=250.0, key="rev_c",
                        help="Gesamter Umsatz")
        st.number_input("Sum of payments", step=20, key="sum_c",
                        help="Anzahl Transaktionen")
        st.number_input("Monthly Fee (€)", step=5.0, key="mrr_c",
                        help="Monatliche Grundgebühr")
        st.number_input("Commission (%)", step=0.01, key="comm_c",
                        help="Provisionssatz des Mitbewerbers")
        st.number_input("Authentification Fee (€)", key="auth_c",
                        help="Gebühr pro Zahlung")

    with col2:
        st.subheader("Offer")

        # Werte automatisch übernehmen
        st.session_state.rev_o = st.session_state.rev_c
        st.session_state.sum_o = st.session_state.sum_c

        st.number_input("Revenue (€)", step=250.0, key="rev_o",
                        help="Umsatz – automatisch übernommen vom Competitor")
        st.number_input("Sum of payments", step=20, key="sum_o",
                        help="Transaktionen – automatisch übernommen vom Competitor")
        st.number_input("Monthly Fee (€)", step=5.0, key="mrr_o",
                        help="Monatliche Gebühr im Angebot")
        st.number_input("Commission (%)", step=0.01, key="comm_o",
                        help="Provisionssatz des Angebots")
        st.number_input("Authentification Fee (€)", key="auth_o",
                        help="Gebühr pro Zahlung im Angebot")

    # Kalkulation
    total_c = st.session_state.rev_c * (st.session_state.comm_c / 100) + \
              st.session_state.sum_c * st.session_state.auth_c + st.session_state.mrr_c
    total_o = st.session_state.rev_o * (st.session_state.comm_o / 100) + \
              st.session_state.sum_o * st.session_state.auth_o + st.session_state.mrr_o
    saving = total_o - total_c

    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.markdown(f"<div style='color:red; font-size:28px;'>💳 {total_c:,.2f} €</div>",
                  unsafe_allow_html=True)
    col3.caption("Total Competitor")
    col4.markdown(f"<div style='color:blue; font-size:28px;'>💳 {total_o:,.2f} €</div>",
                  unsafe_allow_html=True)
    col4.caption("Total Offer")
    col5.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving:,.2f} €</div>",
                  unsafe_allow_html=True)
    col5.caption("Ersparnis (Offer - Competitor)")

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

    # Session State initialisieren
    for i in range(len(df_sw)):
        if f"sw_{i}" not in st.session_state: st.session_state[f"sw_{i}"] = 0
    for i in range(len(df_hw)):
        if f"hw_{i}" not in st.session_state: st.session_state[f"hw_{i}"] = 0
    if "gaw_value" not in st.session_state: st.session_state["gaw_value"] = 50.0
    if "gaw_qty" not in st.session_state: st.session_state["gaw_qty"] = 1

    col_sw, col_hw = st.columns(2)

    # --- Software ---
    with col_sw:
        st.subheader("🧩 Software")
        for i in range(len(df_sw)):
            if df_sw["Produkt"][i] != "GAW":
                st.session_state[f"sw_{i}"] = st.number_input(
                    df_sw["Produkt"][i], min_value=0, step=1, key=f"sw_{i}"
                )

        # Dynamische Logik:
        # Shop → Ordermanager =1, POS → Ordermanager =0, POS inkl 1 Printer=1
        shop_selected = st.session_state["sw_0"] > 0
        pos_selected = st.session_state["sw_2"] > 0

        if shop_selected:
            st.session_state["hw_0"] = max(st.session_state["hw_0"], 1)  # Ordermanager
        if pos_selected:
            st.session_state["hw_0"] = 0  # Ordermanager
            st.session_state["hw_1"] = max(st.session_state["hw_1"], 1)  # POS inkl 1 Printer

        # GAW
        st.session_state["gaw_qty"] = st.number_input("GAW Menge", step=1, key="gaw_qty")
        st.session_state["gaw_value"] = st.number_input(
            "GAW Betrag (€)", min_value=0.0, value=50.0, step=25.0, key="gaw_value"
        )

        df_sw.loc[df_sw["Produkt"] == "GAW", "Menge"] = st.session_state["gaw_qty"]

    # --- Hardware ---
    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            st.session_state[f"hw_{i}"] = st.number_input(
                df_hw["Produkt"][i], min_value=0, step=1, key=f"hw_{i}"
            )

    # --- Kalkulation ---
    df_sw["OTF_min_sum"] = df_sw.apply(lambda r: r["Menge"] * r["Min_OTF"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_sw["OTF_list_sum"] = df_sw.apply(lambda r: r["Menge"] * r["List_OTF"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"] * df_hw["Min_OTF"]
    df_hw["OTF_list_sum"] = df_hw["Menge"] * df_hw["List_OTF"]

    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + st.session_state["gaw_qty"] * st.session_state["gaw_value"]
    total_list_otf = df_sw["OTF_list_sum"].sum() + df_hw["OTF_list_sum"].sum() + st.session_state["gaw_qty"] * st.session_state["gaw_value"]

    df_sw["MRR_min_sum"] = df_sw.apply(lambda r: r["Menge"] * r["Min_MRR"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_sw["MRR_list_sum"] = df_sw.apply(lambda r: r["Menge"] * r["List_MRR"] if r["Produkt"] != "GAW" else 0, axis=1)
    df_hw["MRR_min_sum"] = df_hw["Menge"] * df_hw["Min_MRR"]
    df_hw["MRR_list_sum"] = df_hw["Menge"] * df_hw["List_MRR"]

    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum() + df_hw["MRR_list_sum"].sum()

    # --- Ausgabe ---
    st.markdown("---")
    st.subheader("📊 Gesamtergebnisse")
    st.markdown(f"""
    <div style='display:flex; gap:40px; font-size:20px;'>
        <div style='color:#e74c3c;'>OTF Min: {total_min_otf:,.2f} €</div>
        <div style='color:#28a745;'>OTF List: {total_list_otf:,.2f} €</div>
        <div style='color:#e74c3c;'>MRR Min: {total_min_mrr:,.2f} €</div>
        <div style='color:#28a745;'>MRR List: {total_list_mrr:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Preisdetails anzeigen"):
        df_show = pd.concat([df_sw, df_hw])[["Produkt", "Min_OTF", "List_OTF", "Min_MRR", "List_MRR"]]
        st.dataframe(df_show, hide_index=True, use_container_width=True)

# ------------------------------------------------------------
# 😉 Footer
# ------------------------------------------------------------
st.markdown("""
<hr style="margin:20px 0;">
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
