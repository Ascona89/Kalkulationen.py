import streamlit as st
import pandas as pd

# ------------------------ Seite Setup ------------------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio("Wähle eine Kalkulation:", ["Competitor", "Cardpayment", "Pricing"])

# ------------------------ 1. COMPETITOR ------------------------
if page == "Competitor":
    st.header("🏁 Competitor Kalkulation")
    col1, col2 = st.columns([2, 1.5])

    # --- session_state Initialisierung ---
    for key, default in [("revenue",0.0), ("commission_pct",14.0), ("avg_order_value",25.0),
                         ("service_fee",0.69), ("OTF",0.0), ("MRR",0.0), ("contract_length",12)]:
        if key not in st.session_state:
            st.session_state[key] = default

    with col1:
        st.subheader("Eingaben")
        revenue = st.number_input("Revenue on platform (€)", step=250.0, key="revenue",
                                  help="Gesamter Umsatz, den der Wettbewerber auf der Plattform erzielt")
        commission_pct = st.number_input("Commission (%)", step=1.0, key="commission_pct",
                                         help="Provision des Wettbewerbers in Prozent") / 100
        avg_order_value = st.number_input("Average order value (€)", step=5.0, key="avg_order_value",
                                          help="Durchschnittlicher Bestellwert für Transaktionsgebühren")
        service_fee = st.number_input("Service Fee (€)", step=0.1, key="service_fee",
                                      help="Feste Transaktionsgebühr pro Bestellung")

        st.markdown("---")
        st.subheader("Vertragsdetails")
        OTF = st.number_input("One Time Fee (OTF) (€)", step=100.0, key="OTF")
        MRR = st.number_input("Monthly Recurring Revenue (MRR) (€)", step=10.0, key="MRR")
        contract_length = st.selectbox("Contract length (Monate)", [12, 24],
                                       index=[12,24].index(st.session_state.contract_length), key="contract_length")

    # --- Berechnungen ---
    total_cost = revenue * commission_pct + (0.7 * revenue / avg_order_value if avg_order_value else 0) * service_fee
    transaction = 0.7 * revenue / 5 * 0.35
    cost_oyy_monthly = MRR + transaction
    saving_monthly = total_cost - cost_oyy_monthly
    saving_over_contract = saving_monthly * contract_length

    with col2:
        st.markdown("### 💶 Total Cost")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>", unsafe_allow_html=True)
        st.caption("Gesamtkosten inkl. Provision und Transaktionsgebühren")

    st.subheader("📊 Kennzahlen")
    st.info(f"- Cost OYY monthly: {cost_oyy_monthly:,.2f} €\n"
            f"- Saving monthly: {saving_monthly:,.2f} €\n"
            f"- Saving over contract length: {saving_over_contract:,.2f} €")

# ------------------------ 2. CARDPAYMENT ------------------------
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    col1, col2 = st.columns(2)

    # --- session_state Initialisierung ---
    for key, default in [("rev_c",0.0), ("sum_c",0.0), ("otf_c",0.0), ("mrr_c",0.0),
                         ("comm_c",1.39), ("auth_c",0.0), ("rev_o",0.0), ("sum_o",0.0),
                         ("otf_o",0.0), ("mrr_o",0.0), ("comm_o",1.19), ("auth_o",0.06)]:
        if key not in st.session_state:
            st.session_state[key] = default

    with col1:
        st.subheader("Competitor")
        rev_c = st.number_input("Revenue (€)", step=250.0, key="rev_c")
        sum_pay_c = st.number_input("Sum of payments", key="sum_c")
        otf_c = st.number_input("One Time Fee (€)", key="otf_c")
        mrr_c = st.number_input("Monthly Fee (€)", key="mrr_c")
        commission_c = st.number_input("Commission (%)", step=1.0, key="comm_c") / 100
        auth_c = st.number_input("Authentification Fee (€)", key="auth_c")
        avg_order_value_c = st.number_input("Average order value (€)", value=0.0, key="avg_c")

    with col2:
        st.subheader("Offer")
        # Werte von Competitor übernehmen
        rev_o = st.number_input("Revenue (€)", value=rev_c, step=250.0, key="rev_o")
        sum_pay_o = st.number_input("Sum of payments", value=sum_pay_c, key="sum_o")
        otf_o = st.number_input("One Time Fee (€)", key="otf_o")
        mrr_o = st.number_input("Monthly Fee (€)", key="mrr_o")
        commission_o = st.number_input("Commission (%)", step=1.0, key="comm_o") / 100
        auth_o = st.number_input("Authentification Fee (€)", key="auth_o")
        avg_order_value_o = st.number_input("Average order value (€)", value=0.0, key="avg_o")

    # --- Berechnungen ---
    total_c = rev_c * commission_c + (0.7 * rev_c / avg_order_value_c if avg_order_value_c else 0) * auth_c + mrr_c
    total_o = rev_o * commission_o + (0.7 * rev_o / avg_order_value_o if avg_order_value_o else 0) * auth_o + mrr_o
    saving = total_o - total_c

    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.markdown(f"<div style='color:red; font-size:28px;'>💳 {total_c:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Total Competitor")
    col4.markdown(f"<div style='color:blue; font-size:28px;'>💳 {total_o:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Total Offer")
    col5.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving:,.2f} €</div>", unsafe_allow_html=True)
    col5.caption("Ersparnis (Offer - Competitor)")

# ------------------------ 3. PRICING ------------------------
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")
    st.write("Bitte Mengen eingeben. GAW wird nur für OTF berücksichtigt.")

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

    # --- session_state Initialisierung für alle Mengen ---
    for i in range(len(df_sw)):
        key = f"sw_{i}"
        if key not in st.session_state:
            st.session_state[key] = 0
    for i in range(len(df_hw)):
        key = f"hw_{i}"
        if key not in st.session_state:
            st.session_state[key] = 0
    if "gaw_value" not in st.session_state:
        st.session_state.gaw_value = 50.0
    if "gaw_qty" not in st.session_state:
        st.session_state.gaw_qty = 1

    col_sw, col_hw = st.columns(2)
    with col_sw:
        st.subheader("🧩 Software")
        for i in range(len(df_sw)):
            if df_sw["Produkt"][i] != "GAW":
                df_sw.at[i, "Menge"] = st.number_input(df_sw["Produkt"][i], min_value=0, step=1, key=f"sw_{i}")
        gaw_qty = st.number_input("GAW Menge", step=1, key="gaw_qty")
        gaw_value = st.number_input("GAW Betrag (€)", min_value=0.0, step=25.0, key="gaw_value")
        df_sw.loc[df_sw["Produkt"]=="GAW", "Menge"] = gaw_qty

    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            df_hw.at[i, "Menge"] = st.number_input(df_hw["Produkt"][i], min_value=0, step=1, key=f"hw_{i}")

    # --- Berechnungen ---
    df_sw["OTF_min_sum"] = df_sw.apply(lambda row: row["Menge"]*row["Min_OTF"] if row["Produkt"]!="GAW" else 0, axis=1)
    df_sw["OTF_list_sum"] = df_sw.apply(lambda row: row["Menge"]*row["List_OTF"] if row["Produkt"]!="GAW" else 0, axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"]*df_hw["Min_OTF"]
    df_hw["OTF_list_sum"] = df_hw["Menge"]*df_hw["List_OTF"]

    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + gaw_qty*gaw_value
    total_list_otf = df_sw["OTF_list_sum"].sum() + df_hw["OTF_list_sum"].sum() + gaw_qty*gaw_value

    df_sw["MRR_min_sum"] = df_sw.apply(lambda row: row["Menge"]*row["Min_MRR"] if row["Produkt"]!="GAW" else 0, axis=1)
    df_sw["MRR_list_sum"] = df_sw.apply(lambda row: row["Menge"]*row["List_MRR"] if row["Produkt"]!="GAW" else 0, axis=1)
    df_hw["MRR_min_sum"] = df_hw["Menge"]*df_hw["Min_MRR"]
    df_hw["MRR_list_sum"] = df_hw["Menge"]*df_hw["List_MRR"]

    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum() + df_hw["MRR_list_sum"].sum()

    # --- Ergebnisse anzeigen ---
    st.markdown("---")
    st.subheader("📊 Gesamtergebnisse")
    st.markdown(f"""
    <div style='display:flex; gap:40px; font-size:20px;'>
        <div style='color:#000000;'>OTF Min: {total_min_otf:,.2f} €</div>
        <div style='color:#28a745;'>OTF List: {total_list_otf:,.2f} €</div>
        <div style='color:#000000;'>MRR Min: {total_min_mrr:,.2f} €</div>
        <div style='color:#28a745;'>MRR List: {total_list_mrr:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Preisdetails anzeigen"):
        st.dataframe(pd.concat([df_sw, df_hw])[["Produkt", "Min_OTF", "Min_MRR", "List_MRR"]])

# ------------------------ Footer-Signatur ------------------------
st.markdown(
    """
    <hr style="margin:20px 0;">
    <p style='text-align: center; font-size: 0.8rem; color: gray;'>
        😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast. Grüsse SAS
    </p>
    """,
    unsafe_allow_html=True
)
