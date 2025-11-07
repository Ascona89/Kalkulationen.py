import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 🔒 LOGINBEREICH
# ------------------------------------------------------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")

if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

if not st.session_state["login_status"]:
    st.title("🔒 Zugriff geschützt")
    code_input = st.text_input("Bitte Code eingeben", type="password")
    if st.button("Login"):
        if code_input == "seba":
            st.session_state["login_status"] = True
            st.success("Zugriff gewährt!")
        else:
            st.error("Falscher Code!")

# ------------------------------------------------------------
# ✅ HAUPTAPP (nur sichtbar nach Login)
# ------------------------------------------------------------
if st.session_state["login_status"]:
    st.title("📊 Kalkulations-App")

    def init_session_state(keys_defaults):
        for key, default in keys_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

    page = st.sidebar.radio("Wähle eine Kalkulation:", ["Platform", "Cardpayment", "Pricing"])

    # ------------------------------------------------------------
    # 🏁 PLATFORM (ehemals Competitor)
    # ------------------------------------------------------------
    if page == "Platform":
        st.header("💶 Cost on Platform")

        init_session_state({
            "revenue": 0.0, "commission_pct": 14.0, "avg_order_value": 25.0,
            "service_fee": 0.69, "OTF": 0.0, "MRR": 0.0, "contract_length": 24
        })

        col1, col2 = st.columns([2, 1.5])
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
            st.markdown(f"<div style='color:red; font-size:28px; font-weight:bold;'>{total_cost:,.2f} €</div>",
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

        with col2:
            st.subheader("📊 Kennzahlen")
            st.metric("Cost OYY monthly", f"{cost_oyy_monthly:,.2f} €")
            st.metric("Saving monthly", f"{saving_monthly:,.2f} €")
            st.metric("Saving over contract length", f"{saving_over_contract:,.2f} €")

    # ------------------------------------------------------------
    # 💳 CARDPAYMENT
    # ------------------------------------------------------------
    elif page == "Cardpayment":
        st.header("💳 Cardpayment Vergleich")

        init_session_state({
            "rev_a": 0.0, "sum_a": 0.0, "mrr_a": 0.0,
            "comm_a": 1.39, "auth_a": 0.0,
            "rev_o": 0.0, "sum_o": 0.0, "mrr_o": 0.0,
            "comm_o": 1.19, "auth_o": 0.06
        })

        col1, col2 = st.columns(2)
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
        total_offer = st.session_state.rev_o * (st.session_state.comm_o / 100) + \
                      st.session_state.sum_o * st.session_state.auth_o + st.session_state.mrr_o
        saving = total_offer - total_actual

        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        col3.metric("Total Actual", f"{total_actual:,.2f} €")
        col4.metric("Total Offer", f"{total_offer:,.2f} €")
        col5.metric("Ersparnis", f"{saving:,.2f} €")

    # ------------------------------------------------------------
    # 💰 PRICING
    # ------------------------------------------------------------
    elif page == "Pricing":
        st.header("💰 Pricing Kalkulation")

        # Tabelle mit Software/Hardware (vereinfachte Darstellung)
        data = {
            "Produkt": ["Shop", "App", "POS", "Pay", "Ordermanager", "POS inkl. 1 Printer",
                        "Cash Drawer", "Extra Printer", "Additional Display", "PAX", "GAW"],
            "Menge": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "Min_OTF": [365, 15, 365, 35, 135, 350, 50, 99, 100, 225, 50],
            "List_OTF": [999, 49, 999, 49, 299, 1699, 149, 199, 100, 299, 100],
            "Min_MRR": [50, 15, 49, 5, 0, 0, 0, 0, 0, 0, 0],
            "List_MRR": [119, 49, 89, 25, 0, 0, 0, 0, 0, 0, 0]
        }

        df = pd.DataFrame(data)

        st.markdown("### Software / Hardware Auswahl")
        for i, row in df.iterrows():
            df.at[i, "Menge"] = st.number_input(f"{row['Produkt']} Menge", min_value=0, max_value=10, value=row["Menge"], step=1, key=f"prod_{i}")

        # Berechnung
        df["OTF_min_sum"] = df["Menge"] * df["Min_OTF"]
        df["OTF_list_sum"] = df["Menge"] * df["List_OTF"]
        df["MRR_min_sum"] = df["Menge"] * df["Min_MRR"]
        df["MRR_list_sum"] = df["Menge"] * df["List_MRR"]

        total_otf_min = df["OTF_min_sum"].sum()
        total_otf_list = df["OTF_list_sum"].sum()
        total_mrr_min = df["MRR_min_sum"].sum()
        total_mrr_list = df["MRR_list_sum"].sum()

        # Ergebnisse
        st.markdown("### Ergebnisse")
        st.markdown(
            f"<div style='font-size:18px;'>"
            f"<span style='color:red;'>MIN OTF: {total_otf_min:,.2f} €</span> | "
            f"<span style='color:green;'>LIST OTF: {total_otf_list:,.2f} €</span> | "
            f"<span style='color:red;'>MIN MRR: {total_mrr_min:,.2f} €</span> | "
            f"<span style='color:green;'>LIST MRR: {total_mrr_list:,.2f} €</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        with st.expander("📦 Detailtabelle anzeigen"):
            st.dataframe(df[["Produkt", "Menge", "Min_OTF", "List_OTF", "Min_MRR", "List_MRR"]])

    # ------------------------------------------------------------
    # 😉 FOOTER
    # ------------------------------------------------------------
    st.markdown("""
    <hr style="margin:20px 0;">
    <p style='text-align:center; font-size:0.8rem; color:gray;'>
    😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
    </p>
    """, unsafe_allow_html=True)
