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
        commission = st.number_input("Commission (%)", min_value=0.0, value=14.0, step=0.5) / 100  # in Dezimal
        avg_order_value = st.number_input("Average order value (€)", min_value=0.0, value=35.0, step=1.0)
        service_fee = st.number_input("Service Fee (€)", min_value=0.0, value=0.69, step=0.1)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Unterer übersichtlicher Block: 3 Eingaben
        st.subheader("Weitere Eingaben")
        OTF = st.number_input("One Time Fee (OTF) (€)", min_value=0.0, value=0.0, step=100.0)
        MRR = st.number_input("Monthly Recurring Revenue (MRR) (€)", min_value=0.0, value=0.0, step=10.0)
        contract_length = st.selectbox("Contract length (Monate)", [12, 24])

        # Berechnungen
        total_cost = revenue * commission + (0.7 * revenue / avg_order_value) * service_fee
        transaction = 0.7 * revenue / 5 * 0.35
        cost_oyy_monthly = MRR + transaction
        saving_monthly = total_cost - cost_oyy_monthly
        saving_over_contract = saving_monthly * contract_length

        # Ergebnisse unter den Eingaben
        st.markdown("### 📊 Ergebnisse")
        st.write(f"**Cost OYY monthly:** {cost_oyy_monthly:,.2f} €")
        st.write(f"**Saving monthly:** {saving_monthly:,.2f} €")
        st.write(f"**Saving over contract length:** {saving_over_contract:,.2f} €")

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
        commission_c = st.number_input("Commission (%)", key="comm_c", min_value=0.0, value=14.0) / 100
        auth_c = st.number_input("Authentification Fee (€)", key="auth_c", min_value=0.0, value=0.0)
        avg_order_value = st.number_input("Average order value (€)", key="avg_c", min_value=0.0, value=35.0)

    with col2:
        st.subheader("Offer")
        rev_o = st.number_input("Revenue (€)", key="rev_o", value=rev_c, disabled=True)
        sum_pay_o = st.number_input("Sum of payments", key="sum_o", value=sum_pay_c, disabled=True)
        otf_o = st.number_input("One Time Fee (€)", key="otf_o", min_value=0.0, value=0.0)
        mrr_o = st.number_input("Monthly Fee (€)", key="mrr_o", min_value=0.0, value=0.0)
        commission_o = st.number_input("Commission (%)", key="comm_o", min_value=0.0, value=1.19) / 100
        auth_o = st.number_input("Authentification Fee (€)", key="auth_o", min_value=0.0, value=0.06)

    # Berechnungen
    # Total Competitor und Offer basierend auf Competitor-Formel
    total_c = rev_c * commission_c + (0.7 * rev_c / avg_order_value) * auth_c
    total_o = rev_o * commission_o + (0.7 * rev_o / avg_order_value) * auth_o
    saving = total_o - total_c

    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.metric("💳 Total Competitor", f"{total_c:,.2f} €")
    col4.metric("💳 Total Offer", f"{total_o:,.2f} €")
    col5.metric("💰 Saving (Offer - Competitor)", f"{saving:,.2f} €")
