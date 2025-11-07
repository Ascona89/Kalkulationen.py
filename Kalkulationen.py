import streamlit as st
import pandas as pd

# -----------------------------------
# 🔒 Login mit Code
# -----------------------------------
if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

if not st.session_state["login_status"]:
    st.title("🔒 Zugriff geschützt")
    code = st.text_input("Bitte Code eingeben", type="password")
    if st.button("Login"):
        if code == "seba":
            st.session_state["login_status"] = True
            st.success("Zugriff gewährt!")
            st.experimental_rerun()
        else:
            st.error("Falscher Code!")
else:
    # -----------------------------------
    # 🔧 Seitenkonfiguration
    # -----------------------------------
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
            st.number_input("Revenue on platform (€)", step=250.0, key="revenue",
                            help="Gesamter Umsatz auf der Plattform")
            st.number_input("Commission (%)", step=1.0, key="commission_pct",
                            help="Provision in Prozent")
            st.number_input("Average order value (€)", step=5.0, key="avg_order_value",
                            help="Durchschnittlicher Bestellwert")
            st.number_input("Service Fee (€)", step=0.1, key="service_fee",
                            help="Transaktionsgebühr pro Onlinezahlung")

            # Ergebnis direkt unter Service Fee
            total_cost = st.session_state.revenue * (st.session_state.commission_pct / 100) + \
                         (0.7 * st.session_state.revenue / st.session_state.avg_order_value if st.session_state.avg_order_value else 0) * st.session_state.service_fee
            st.markdown("### 💶 Cost on Platform")
            st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>",
                        unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Vertragsdetails")
            st.number_input("One Time Fee (OTF) (€)", step=100.0, key="OTF")
            st.number_input("Monthly Recurring Revenue (MRR) (€)", step=10.0, key="MRR")
            st.number_input("Contract length (Monate)", step=12, key="contract_length")

        # Kennzahlen
        transaction = 0.7 * st.session_state.revenue / 5 * 0.35
        cost_oyy_monthly = st.session_state.MRR + transaction
        saving_monthly = total_cost - cost_oyy_monthly
        saving_over_contract = saving_monthly * st.session_state.contract_length

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
            # Werte automatisch übernehmen
            st.session_state.rev_o = st.session_state.rev_a
            st.session_state.sum_o = st.session_state.sum_a

            st.number_input("Revenue (€)", step=250.0, key="rev_o")
            st.number_input("Sum of payments", step=20, key="sum_o")
            st.number_input("Monthly Fee (€)", step=5.0, key="mrr_o")
            st.number_input("Commission (%)", step=0.01, key="comm_o")
            st.number_input("Authentification Fee (€)", key="auth_o")

        # Kalkulation
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
        # … (hier kommt der bisherige Pricing-Code, identisch wie vorher)
        st.info("Pricing Kalkulation wie gehabt")  # Platzhalter, kann kompletten vorherigen Code hier einfügen

    # ------------------------------------------------------------
    # 😉 Footer
    # ------------------------------------------------------------
    st.markdown("""
    <hr style="margin:20px 0;">
    <p style='text-align:center; font-size:0.8rem; color:gray;'>
    😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
    </p>
    """, unsafe_allow_html=True)
