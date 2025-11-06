import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio("Wähle eine Kalkulation:", ["Competitor", "Cardpayment", "Pricing"])

# ------------------------ 1. COMPETITOR ------------------------
if page == "Competitor":
    st.header("🏁 Competitor Kalkulation")
    col1, col2 = st.columns([2, 1.5])

    with col1:
        st.subheader("Eingaben")
        revenue = st.number_input("Revenue on platform (€)", min_value=0.0, value=0.0, step=100.0)
        commission_pct = st.number_input("Commission (%)", min_value=0.0, value=14.0, step=0.5)/100
        avg_order_value = st.number_input("Average order value (€)", min_value=0.0, value=35.0, step=1.0)
        service_fee = st.number_input("Service Fee (€)", min_value=0.0, value=0.69, step=0.1)

        st.markdown("---")
        st.subheader("Vertragsdetails")
        OTF = st.number_input("One Time Fee (OTF) (€)", min_value=0.0, value=0.0, step=100.0)
        MRR = st.number_input("Monthly Recurring Revenue (MRR) (€)", min_value=0.0, value=0.0, step=10.0)
        contract_length = st.selectbox("Contract length (Monate)", [12, 24])

    total_cost = revenue * commission_pct + (0.7 * revenue / avg_order_value if avg_order_value else 0) * service_fee
    transaction = 0.7 * revenue / 5 * 0.35
    cost_oyy_monthly = MRR + transaction
    saving_monthly = total_cost - cost_oyy_monthly
    saving_over_contract = saving_monthly * contract_length

    with col2:
        st.markdown("### 💶 Total Cost")
        st.metric(label="", value=f"{total_cost:,.2f} €", delta_color="normal")

    st.subheader("📊 Kennzahlen")
    st.info(f"- Cost OYY monthly: {cost_oyy_monthly:,.2f} €\n- Saving monthly: {saving_monthly:,.2f} €\n- Saving over contract length: {saving_over_contract:,.2f} €")

# ------------------------ 2. CARDPAYMENT ------------------------
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Competitor")
        rev_c = st.number_input("Revenue (€)", key="rev_c", min_value=0.0, value=0.0)
        sum_pay_c = st.number_input("Sum of payments", key="sum_c", min_value=0.0, value=0.0)
        otf_c = st.number_input("One Time Fee (€)", key="otf_c", min_value=0.0, value=0.0)
        mrr_c = st.number_input("Monthly Fee (€)", key="mrr_c", min_value=0.0, value=0.0)
        commission_c = st.number_input("Commission (%)", key="comm_c", min_value=0.0, value=1.39)/100
        auth_c = st.number_input("Authentification Fee (€)", key="auth_c", min_value=0.0, value=0.0)
        avg_order_value = st.number_input("Average order value (€)", key="avg_c", min_value=0.0, value=0.0)

    with col2:
        st.subheader("Offer")
        rev_o = st.number_input("Revenue (€)", key="rev_o", min_value=0.0, value=0.0)
        sum_pay_o = st.number_input("Sum of payments", key="sum_o", min_value=0.0, value=0.0)
        otf_o = st.number_input("One Time Fee (€)", key="otf_o", min_value=0.0, value=0.0)
        mrr_o = st.number_input("Monthly Fee (€)", key="mrr_o", min_value=0.0, value=0.0)
        commission_o = st.number_input("Commission (%)", key="comm_o", min_value=0.0, value=1.19)/100
        auth_o = st.number_input("Authentification Fee (€)", key="auth_o", min_value=0.0, value=0.06)
        avg_order_value_o = st.number_input("Average order value (€)", key="avg_o", min_value=0.0, value=0.0)

    total_c = rev_c * commission_c + (0.7 * rev_c / avg_order_value if avg_order_value else 0) * auth_c
    total_o = rev_o * commission_o + (0.7 * rev_o / avg_order_value_o if avg_order_value_o else 0) * auth_o
    saving = total_o - total_c

    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.metric("💳 Total Competitor", f"{total_c:,.2f} €", delta_color="inverse")
    col4.metric("💳 Total Offer", f"{total_o:,.2f} €", delta_color="normal")
    col5.metric("💰 Saving (Offer - Competitor)", f"{saving:,.2f} €", delta_color="off")

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
            if df_sw["Produkt"][i] != "GAW":
                df_sw.at[i, "Menge"] = st.number_input(df_sw["Produkt"][i], min_value=0, value=0, step=1, key=f"sw_{i}")
            else:
                gaw_qty = st.number_input("GAW Menge", min_value=0, value=0, key="gaw_qty")
                gaw_value = st.number_input("GAW Betrag (€)", min_value=0.0, value=0.0, step=10.0, key="gaw_value")
                df_sw.at[i, "Menge"] = gaw_qty

    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            df_hw.at[i, "Menge"] = st.number_input(df_hw["Produkt"][i], min_value=0, value=0, step=1, key=f"hw_{i}")

    # Berechnung MRR ohne GAW
    df_sw["MRR_min_sum"] = df_sw.apply(lambda row: row["Menge"] * row["Min_MRR"] if row["Produkt"] != "GAW" else 0, axis=1)
    df_sw["MRR_list_sum"] = df_sw.apply(lambda row: row["Menge"] * row["List_MRR"] if row["Produkt"] != "GAW" else 0, axis=1)
    df_hw["MRR_min_sum"] = df_hw["Menge"] * df_hw["Min_MRR"]
    df_hw["MRR_list_sum"] = df_hw["Menge"] * df_hw["List_MRR"]

    # Berechnung OTF inkl. GAW
    df_sw["OTF_min_sum"] = df_sw.apply(lambda row: row["Menge"] * row["Min_OTF"] if row["Produkt"] != "GAW" else 0, axis=1)
    df_sw["OTF_list_sum"] = df_sw.apply(lambda row: row["Menge"] * row["List_OTF"] if row["Produkt"] != "GAW" else 0, axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"] * df_hw["Min_OTF"]
    df_hw["OTF_list_sum"] = df_hw["Menge"] * df_hw["List_OTF"]

    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + (gaw_qty * gaw_value)
    total_list_otf = df_sw["OTF_list_sum"].sum() + df_hw["OTF_list_sum"].sum() + (gaw_qty * gaw_value)
    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum() + df_hw["MRR_list_sum"].sum()

    st.markdown("---")
    st.subheader("📊 Gesamtergebnisse")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("OTF Min", f"{total_min_otf:,.2f} €")
    col2.metric("OTF List", f"{total_list_otf:,.2f} €")
    col3.metric("MRR Min", f"{total_min_mrr:,.2f} €")
    col4.metric("MRR List", f"{total_list_mrr:,.2f} €")

    with st.expander("Preisdetails anzeigen"):
        st.dataframe(pd.concat([df_sw, df_hw])[["Produkt", "Menge", "Min_OTF", "List_OTF", "Min_MRR", "List_MRR"]])
