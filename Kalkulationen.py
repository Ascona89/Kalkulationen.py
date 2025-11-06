import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("Kalkulations-App für interne Nutzung")

# Menü zur Auswahl der Kalkulation
menu = ["Competitor", "Cardpayment", "Pricing"]
choice = st.sidebar.selectbox("Wähle die Kalkulation:", menu)

# ----------------- Competitor -----------------
if choice == "Competitor":
    st.header("Competitor Kalkulation")
    col_input, col_result = st.columns([1,1])

    with col_input:
        st.subheader("Eingaben")
        revenue = st.number_input("Revenue on Platform (€)", value=1000.0)
        commission_percent = st.number_input("Commission (%)", value=14.0)
        avg_order_value = st.number_input("Average Order Value (€)", value=35.0)
        service_fee = st.number_input("Service Fee (€)", value=0.69)
        otf = st.number_input("OTF (€)")
        mrr = st.number_input("MRR (€)")
        contract_length = st.selectbox("Contract Length (Monate)", options=[12, 24])

    with col_result:
        st.subheader("Ergebnisse")
        total_orders = revenue / avg_order_value
        online_payment_orders = total_orders * 0.7
        commission_per_month = revenue * (commission_percent/100)
        transaction_fee = online_payment_orders * service_fee
        total_cost = commission_per_month + transaction_fee
        transaction = (revenue * 0.7) / 5 * 0.35
        cost_oyy_monthly = mrr + transaction
        saving_monthly = total_cost - cost_oyy_monthly
        saving_total = saving_monthly * contract_length

        st.write(f"Total Orders: {total_orders:.2f}")
        st.write(f"Online Payment Orders: {online_payment_orders:.2f}")
        st.write(f"Commission per Month: €{commission_per_month:.2f}")
        st.write(f"Transaction Fee: €{transaction_fee:.2f}")
        st.write(f"Total Cost: €{total_cost:.2f}")
        st.write(f"Transaction: €{transaction:.2f}")
        st.write(f"Cost OYY Monthly: €{cost_oyy_monthly:.2f}")
        st.write(f"Saving Monthly: €{saving_monthly:.2f}")
        st.write(f"Saving over Contract Length: €{saving_total:.2f}")

# ----------------- Cardpayment -----------------
elif choice == "Cardpayment":
    st.header("Cardpayment Kalkulation")
    col_input, col_result = st.columns([1,1])

    with col_input:
        st.subheader("Eingaben")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Competitor**")
            otf_comp = st.number_input("One Time Fee (€)", key="otf_comp")
            monthly_fee_comp = st.number_input("Monthly Fee (€)", key="monthly_comp")
            commission_comp = st.number_input("Commission (%)", key="commission_comp")
            auth_fee_comp = st.number_input("Authentification Fee (€)", key="auth_comp")

        with col2:
            st.write("**Offer**")
            otf_offer = st.number_input("One Time Fee (€)", key="otf_offer")
            monthly_fee_offer = st.number_input("Monthly Fee (€)", key="monthly_offer")
            commission_offer = st.number_input("Commission (%)", key="commission_offer")
            auth_fee_offer = st.number_input("Authentification Fee (€)", key="auth_offer")

        revenue = st.number_input("Revenue (€)", value=1000.0)
        sum_payments = st.number_input("Sum of Payments (€)", value=500.0)

    with col_result:
        st.subheader("Ergebnisse")
        commission_result_comp = revenue * (commission_comp/100)
        auth_result_comp = sum_payments * auth_fee_comp
        total_comp = monthly_fee_comp + commission_result_comp + auth_result_comp

        commission_result_offer = revenue * (commission_offer/100)
        auth_result_offer = sum_payments * auth_fee_offer
        total_offer = monthly_fee_offer + commission_result_offer + auth_result_offer

        st.write("**Competitor**")
        st.write(f"Commission: €{commission_result_comp:.2f}")
        st.write(f"Authentification Fee: €{auth_result_comp:.2f}")
        st.write(f"Total: €{total_comp:.2f}")

        st.write("**Offer**")
        st.write(f"Commission: €{commission_result_offer:.2f}")
        st.write(f"Authentification Fee: €{auth_result_offer:.2f}")
        st.write(f"Total: €{total_offer:.2f}")

# ----------------- Pricing -----------------
elif choice == "Pricing":
    st.header("Pricing Kalkulation")
    col_input, col_result = st.columns([1,1])

    # Items definieren
    items = [
        {"name": "Shop", "SUF_min": 365, "SUF_list": 999, "MRR_min": 50, "MRR_list": 119},
        {"name": "App", "SUF_min": 15, "SUF_list": 49, "MRR_min": 15, "MRR_list": 49},
        {"name": "POS", "SUF_min": 365, "SUF_list": 999, "MRR_min": 49, "MRR_list": 89},
        {"name": "Pay", "SUF_min": 35, "SUF_list": 49, "MRR_min": 5, "MRR_list": 25},
        {"name": "Kiosk", "SUF_min": 0, "SUF_list": 0, "MRR_min": 0, "MRR_list": 0},
        {"name": "GAW", "SUF_min": 50, "SUF_list": 100, "MRR_min": 100, "MRR_list": 100},
        {"name": "Ordermanager", "SUF_min": 135, "SUF_list": 299, "MRR_min": 0, "MRR_list": 0},
        {"name": "POS inkl. 1 printer", "SUF_min": 350, "SUF_list": 1699, "MRR_min": 0, "MRR_list": 0},
        {"name": "Cash Drawer", "SUF_min": 50, "SUF_list": 149, "MRR_min": 0, "MRR_list": 0},
        {"name": "extra Printer", "SUF_min": 99, "SUF_list": 199, "MRR_min": 0, "MRR_list": 0},
        {"name": "additional Display", "SUF_min": 100, "SUF_list": 100, "MRR_min": 0, "MRR_list": 0},
        {"name": "PAX", "SUF_min": 225, "SUF_list": 299, "MRR_min": 0, "MRR_list": 0},
        {"name": "Kiosk2", "SUF_min": 0, "SUF_list": 0, "MRR_min": 0, "MRR_list": 0},
    ]

    with col_input:
        st.subheader("Mengen Eingaben")
        qty_items = {}
        for item in items:
            qty_items[item["name"]] = st.number_input(
                f"{item['name']} Menge", min_value=0, value=1, key=f"qty_{item['name']}"
            )

    with col_result:
        st.subheader("Ergebnisse")
        df = pd.DataFrame(items)
        df["Menge"] = [qty_items[item["name"]] for item in items]
        df["SUF_Min_Total"] = df["SUF_min"] * df["Menge"]
        df["SUF_List_Total"] = df["SUF_list"] * df["Menge"]
        df["MRR_Min_Total"] = df["MRR_min"] * df["Menge"]
        df["MRR_List_Total"] = df["MRR_list"] * df["Menge"]

        st.dataframe(
            df[["name", "Menge", "SUF_Min_Total", "SUF_List_Total", "MRR_Min_Total", "MRR_List_Total"]],
            use_container_width=True
        )
