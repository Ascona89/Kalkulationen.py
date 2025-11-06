import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kalkulations-App", layout="wide")

# Seitenmenü
st.sidebar.title("Menü")
page = st.sidebar.radio("Wähle eine Kalkulation:", ["Competitor", "Cardpayment", "Pricing"])

# ---------- 1. COMPETITOR ----------
if page == "Competitor":
    st.title("🏁 Competitor Kalkulation")

    col1, col2 = st.columns([2, 1.5])

    with col1:
        st.subheader("Eingaben")
        revenue = st.number_input("Revenue on platform (€)", min_value=0.0, value=0.0, step=100.0)
        commission = st.number_input("Commission (%)", min_value=0.0, value=14.0, step=0.5)
        avg_order_value = st.number_input("Average order value (€)", min_value=0.0, value=35.0, step=1.0)
        service_fee = st.number_input("Service Fee (€)", min_value=0.0, value=0.69, step=0.1)

        st.markdown("<br><br>", unsafe_allow_html=True)

        col_otf, col_kennzahlen = st.columns([1, 1])
        OTF = col_otf.number_input("One Time Fee (OTF) (€)", min_value=0.0, value=0.0, step=100.0)
        MRR = st.number_input("Monthly Recurring Revenue (MRR) (€)", min_value=0.0, value=0.0, step=10.0)
        contract_length = st.selectbox("Contract length (Monate)", [12, 24])

        # Berechnungen
        total_orders = revenue / avg_order_value if avg_order_value else 0
        online_payment = total_orders * 0.7
        commission_month = (commission / 100) * revenue
        transaction_fee = online_payment * service_fee
        total_cost = commission_month + transaction_fee
        transaction = 0.7 * revenue / 5 * 0.35
        cost_oyy_monthly = MRR + transaction
        saving_monthly = total_cost - cost_oyy_monthly
        saving_over_contract = saving_monthly * contract_length

        # Kennzahlen rechts neben OTF
        col_kennzahlen.markdown("### 📊 Kennzahlen")
        col_kennzahlen.write(f"**Cost OYY monthly:** {cost_oyy_monthly:,.2f} €")
        col_kennzahlen.write(f"**Saving monthly:** {saving_monthly:,.2f} €")
        col_kennzahlen.write(f"**Saving over contract length:** {saving_over_contract:,.2f} €")

    with col2:
        st.markdown("### 💶 Total Cost")
        st.metric(label="", value=f"{total_cost:,.2f} €")

# ---------- 2. CARDPAYMENT ----------
elif page == "Cardpayment":
    st.title("💳 Cardpayment Vergleich")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Competitor")
        rev_c = st.number_input("Revenue (€)", key="rev_c", min_value=0.0, value=0.0)
        sum_pay_c = st.number_input("Sum of payments", key="sum_c", min_value=0.0, value=0.0)
        otf_c = st.number_input("One Time Fee (€)", key="otf_c", min_value=0.0, value=0.0)
        mrr_c = st.number_input("Monthly Fee (€)", key="mrr_c", min_value=0.0, value=0.0)
        comm_c = st.number_input("Commission (%)", key="comm_c", min_value=0.0, value=0.0)
        auth_c = st.number_input("Authentification Fee (€)", key="auth_c", min_value=0.0, value=0.0)

    with col2:
        st.subheader("Offer")
        rev_o = st.number_input("Revenue (€)", key="rev_o", value=rev_c, disabled=True)
        sum_pay_o = st.number_input("Sum of payments", key="sum_o", value=sum_pay_c, disabled=True)
        otf_o = st.number_input("One Time Fee (€)", key="otf_o", min_value=0.0, value=0.0)
        mrr_o = st.number_input("Monthly Fee (€)", key="mrr_o", min_value=0.0, value=0.0)
        comm_o = st.number_input("Commission (%)", key="comm_o", min_value=0.0, value=1.19, step=0.01)
        auth_o = st.number_input("Authentification Fee (€)", key="auth_o", min_value=0.0, value=0.06, step=0.01)

    # Berechnungen
    total_c = mrr_c + (rev_c * comm_c / 100) + (sum_pay_c * auth_c)
    total_o = mrr_o + (rev_o * comm_o / 100) + (sum_pay_o * auth_o)
    saving = total_o - total_c

    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.metric("💳 Total Competitor", f"{total_c:,.2f} €")
    col4.metric("💳 Total Offer", f"{total_o:,.2f} €")
    col5.metric("💰 Saving (Offer - Competitor)", f"{saving:,.2f} €")

# ---------- 3. PRICING ----------
elif page == "Pricing":
    st.title("💰 Pricing Kalkulation")
    st.write("Bitte Mengen eingeben. Standardwert ist 0.")

    # Software-Daten
    software_data = {
        "Produkt": ["Shop", "App", "POS", "Pay", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 50],
        "List_OTF": [999, 49, 999, 49, 100],
        "Min_MRR": [50, 15, 49, 5, 100],
        "List_MRR": [119, 49, 89, 25, 100],
    }

    # Hardware-Daten
    hardware_data = {
        "Produkt": ["Ordermanager", "POS inkl. Printer", "Cash Drawer", "Extra Printer", "Additional Display", "PAX"],
        "Min_OTF": [135, 350, 50, 99, 100, 225],
        "List_OTF": [299, 1699, 149, 199, 100, 299],
        "Min_MRR": [0, 0, 0, 0, 0, 0],
        "List_MRR": [0, 0, 0, 0, 0, 0],
    }

    df_sw = pd.DataFrame(software_data)
    df_hw = pd.DataFrame(hardware_data)

    col_sw, col_hw = st.columns(2)

    with col_sw:
        st.subheader("🧩 Software")
        for i in range(len(df_sw)):
            if df_sw["Produkt"][i] == "GAW":
                gaw_qty = st.number_input("GAW Menge", min_value=0, value=0, key="gaw_qty")
                gaw_value = st.number_input("GAW Betrag (€)", min_value=0.0, value=0.0, step=10.0, key="gaw_value")
                df_sw.at[i, "Menge"] = gaw_qty
            else:
                df_sw.at[i, "Menge"] = st.number_input(df_sw["Produkt"][i], min_value=0, value=0, step=1, key=f"sw_{i}")

    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            df_hw.at[i, "Menge"] = st.number_input(df_hw["Produkt"][i], min_value=0, value=0, step=1, key=f"hw_{i}")

    # Berechnungen
    for df in [df_sw, df_hw]:
        df["OTF_min_sum"] = df["Menge"] * df["Min_OTF"]
        df["OTF_list_sum"] = df["Menge"] * df["List_OTF"]
        df["MRR_min_sum"] = df["Menge"] * df["Min_MRR"]
        df["MRR_list_sum"] = df["Menge"] * df["List_MRR"]

    # GAW Berechnung zu OTF addieren
    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + (gaw_qty * gaw_value)
    total_list_otf = df_sw["OTF_list_sum"].sum() + df_hw["OTF_list_sum"].sum() + (gaw_qty * gaw_value)
    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum() + df_hw["MRR_list_sum"].sum()

    st.markdown("---")
    st.subheader("📊 Gesamtergebnisse")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min OTF", f"{total_min_otf:,.2f} €")
    col2.metric("List OTF", f"{total_list_otf:,.2f} €")
    col3.metric("Min MRR", f"{total_min_mrr:,.2f} €")
    col4.metric("List MRR", f"{total_list_mrr:,.2f} €")

    # Tabelle weiter unten
    with st.expander("Preisdetails anzeigen"):
        st.dataframe(pd.concat([df_sw, df_hw])[["Produkt", "Menge", "Min_OTF", "List_OTF", "Min_MRR", "List_MRR"]])
