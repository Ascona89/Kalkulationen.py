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

    with col1:
        st.subheader("Eingaben")
        revenue = st.number_input(
            "Revenue on platform (€)",
            min_value=0.0,
            value=0.0,
            step=250.0,
            help="Gesamter Umsatz, den der Wettbewerber auf der Plattform erzielt"
        )
        commission_pct = st.number_input(
            "Commission (%)",
            min_value=0.0,
            value=14.0,
            step=1.0,
            help="Provision des Wettbewerbers in Prozent vom Umsatz"
        ) / 100
        avg_order_value = st.number_input(
            "Average order value (€)",
            min_value=0.0,
            value=25.0,
            step=5.0,
            help="Durchschnittlicher Bestellwert, wird für die Berechnung von Transaktionsgebühren verwendet"
        )
        service_fee = st.number_input(
            "Service Fee (€)",
            min_value=0.0,
            value=0.69,
            step=0.1,
            help="Feste Transaktionsgebühr pro Bestellung"
        )

        st.markdown("---")
        st.subheader("Vertragsdetails")
        OTF = st.number_input(
            "One Time Fee (OTF) (€)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            help="Einmalige Kosten für den Vertrag"
        )
        MRR = st.number_input(
            "Monthly Recurring Revenue (MRR) (€)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Monatlich wiederkehrende Einnahmen des Wettbewerbers"
        )
        contract_length = st.selectbox(
            "Contract length (Monate)",
            [12, 24],
            help="Laufzeit des Vertrags in Monaten"
        )

    # Berechnungen
    total_cost = revenue * commission_pct + (0.7 * revenue / avg_order_value if avg_order_value else 0) * service_fee
    transaction = 0.7 * revenue / 5 * 0.35
    cost_oyy_monthly = MRR + transaction
    saving_monthly = total_cost - cost_oyy_monthly
    saving_over_contract = saving_monthly * contract_length

    with col2:
        st.markdown("### 💶 Total Cost")
        st.metric(label="", value=f"{total_cost:,.2f} €")
        st.caption("Gesamtkosten des Wettbewerbers pro Monat inkl. Provision und Transaktionsgebühren")

    st.subheader("📊 Kennzahlen")
    st.info(f"- Cost OYY monthly: {cost_oyy_monthly:,.2f} €\n"
            f"- Saving monthly: {saving_monthly:,.2f} €\n"
            f"- Saving over contract length: {saving_over_contract:,.2f} €")
    st.caption("Monatliche Kosten vs. Einsparungen über Vertragslaufzeit")

# ------------------------ 2. CARDPAYMENT ------------------------
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Competitor")
        rev_c = st.number_input("Revenue (€)", key="rev_c", min_value=0.0, value=0.0, step=250.0, help="Umsatz des Wettbewerbers")
        sum_pay_c = st.number_input("Sum of payments", key="sum_c", min_value=0.0, value=0.0, help="Summe der Zahlungen beim Wettbewerber")
        otf_c = st.number_input("One Time Fee (€)", key="otf_c", min_value=0.0, value=0.0, help="Einmalige Gebühr")
        mrr_c = st.number_input("Monthly Fee (€)", key="mrr_c", min_value=0.0, value=0.0, help="Monatliche Gebühr")
        commission_c = st.number_input("Commission (%)", key="comm_c", min_value=0.0, value=1.39, step=1.0, help="Prozentuale Kommission")/100
        auth_c = st.number_input("Authentification Fee (€)", key="auth_c", min_value=0.0, value=0.0, help="Gebühr pro Zahlung")
        avg_order_value = st.number_input("Average order value (€)", key="avg_c", min_value=0.0, value=0.0, step=5.0, help="Durchschnittlicher Bestellwert")

    with col2:
        st.subheader("Offer")
        rev_o = st.number_input("Revenue (€)", key="rev_o", min_value=0.0, value=rev_c, step=250.0, help="Umsatz des Angebots")
        sum_pay_o = st.number_input("Sum of payments", key="sum_o", min_value=0.0, value=sum_pay_c, help="Summe der Zahlungen im Angebot")
        otf_o = st.number_input("One Time Fee (€)", key="otf_o", min_value=0.0, value=0.0)
        mrr_o = st.number_input("Monthly Fee (€)", key="mrr_o", min_value=0.0, value=0.0)
        commission_o = st.number_input("Commission (%)", key="comm_o", min_value=0.0, value=1.19, step=1.0, help="Prozentuale Kommission für Angebot")/100
        auth_o = st.number_input("Authentification Fee (€)", key="auth_o", min_value=0.0, value=0.06, help="Gebühr pro Zahlung im Angebot")
        avg_order_value_o = st.number_input("Average order value (€)", key="avg_o", min_value=0.0, value=0.0, step=5.0)

    total_c = rev_c * commission_c + (0.7 * rev_c / avg_order_value if avg_order_value else 0) * auth_c
    total_o = rev_o * commission_o + (0.7 * rev_o / avg_order_value_o if avg_order_value_o else 0) * auth_o
    saving = total_o - total_c

    st.markdown("---")
    st.subheader("Ergebnisse")
    col3, col4, col5 = st.columns(3)
    col3.metric("💳 Total Competitor", f"{total_c:,.2f} €")
    col3.caption("Gesamtkosten des Wettbewerbers inklusive Kommission und Authentifizierungsgebühren")
    col4.metric("💳 Total Offer", f"{total_o:,.2f} €")
    col4.caption("Gesamtkosten des Angebots inklusive Kommission und Authentifizierungsgebühren")
    col5.metric("💰 Saving (Offer - Competitor)", f"{saving:,.2f} €")
    col5.caption("Differenz zwischen Angebot und Competitor – zeigt die Ersparnis")

# ------------------------ 3. PRICING ------------------------
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")
    st.write("Bitte Mengen eingeben. GAW und ADS werden nur für OTF berücksichtigt.")

    software_data = {
        "Produkt": ["Shop", "App", "POS", "Pay", "GAW", "ADS"],
        "Min_OTF": [365, 15, 365, 35, 50, 0],
        "List_OTF": [999, 49, 999, 49, 100, 0],
        "Min_MRR": [50, 15, 49, 5, 100, 0],
        "List_MRR": [119, 49, 89, 25, 100, 0],
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

    col_sw, col_hw = st.columns(2)
    with col_sw:
        st.subheader("🧩 Software")
        for i in range(len(df_sw)):
            if df_sw["Produkt"][i] not in ["GAW", "ADS"]:
                df_sw.at[i, "Menge"] = st.number_input(
                    df_sw["Produkt"][i], min_value=0, value=0, step=1, key=f"sw_{i}",
                    help=f"Anzahl der Lizenzen/Einheiten für {df_sw['Produkt'][i]}"
                )
        # GAW
        gaw_qty = st.number_input(
            "GAW Menge", min_value=1, value=1, step=1, key="gaw_qty",
            help="Mindestmenge 1 Einheit"
        )
        gaw_value = st.number_input(
            "GAW Betrag (€)", min_value=50.0, value=50.0, step=25.0, key="gaw_value",
            help="Betrag pro GAW-Einheit für OTF (min. 50€, Schritte 25€)"
        )
        df_sw.loc[df_sw["Produkt"]=="GAW", "Menge"] = gaw_qty

        # ADS
        ads_qty = st.number_input(
            "ADS Menge", min_value=1, value=1, step=1, key="ads_qty",
            help="Anzahl der ADS-Einheiten für OTF"
        )
        ads_value = st.number_input(
            "ADS Betrag (€)", min_value=50.0, value=50.0, step=25.0, key="ads_value",
            help="Betrag pro ADS-Einheit für OTF (min. 50€, Schritte 25€)"
        )
        df_sw.loc[df_sw["Produkt"]=="ADS", "Menge"] = ads_qty

    with col_hw:
        st.subheader("🖥️ Hardware")
        for i in range(len(df_hw)):
            df_hw.at[i, "Menge"] = st.number_input(
                df_hw["Produkt"][i],
                min_value=0,
                value=0,
                step=1,
                key=f"hw_{i}",
                help="Zusätzliche Drucker, 1 ist bei POS inklusive" if "Printer" in df_hw["Produkt"][i] else f"Anzahl der Einheiten für {df_hw['Produkt'][i]}"
            )

    # Berechnungen
    df_sw["OTF_min_sum"] = df_sw.apply(lambda row: (row["Menge"] * row["Min_OTF"]) if row["Produkt"] not in ["GAW","ADS"] else 0, axis=1)
    df_sw["OTF_list_sum"] = df_sw.apply(lambda row: (row["Menge"] * row["List_OTF"]) if row["Produkt"] not in ["GAW","ADS"] else 0, axis=1)
    df_hw["OTF_min_sum"] = df_hw["Menge"] * df_hw["Min_OTF"]
    df_hw["OTF_list_sum"] = df_hw["Menge"] * df_hw["List_OTF"]

    total_min_otf = df_sw["OTF_min_sum"].sum() + df_hw["OTF_min_sum"].sum() + gaw_qty * gaw_value + ads_qty * ads_value
    total_list_otf = df_sw["OTF_list_sum"].sum() + df_hw["OTF_list_sum"].sum() + gaw_qty * gaw_value + ads_qty * ads_value

    df_sw["MRR_min_sum"] = df_sw.apply(lambda row: row["Menge"] * row["Min_MRR"] if row["Produkt"] not in ["GAW","ADS"] else 0, axis=1)
    df_sw["MRR_list_sum"] = df_sw.apply(lambda row: row["Menge"] * row["List_MRR"] if row["Produkt"] not in ["GAW","ADS"] else 0, axis=1)
    df_hw["MRR_min_sum"] = df_hw["Menge"] * df_hw["Min_MRR"]
    df_hw["MRR_list_sum"] = df_hw["Menge"] * df_hw["List_MRR"]

    total_min_mrr = df_sw["MRR_min_sum"].sum() + df_hw["MRR_min_sum"].sum()
    total_list_mrr = df_sw["MRR_list_sum"].sum() + df_hw["MRR_list_sum"].sum()

    # Ergebnisse anzeigen
    st.markdown("---")
    st.subheader("📊 Gesamtergebnisse")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("OTF Min", f"{total_min_otf:,.2f} €")
    col1.caption("Summe der Mindest-OTF inkl. GAW und ADS")
    col2.metric("OTF List", f"{total_list_otf:,.2f} €")
    col2.caption("Summe der Listen-OTF inkl. GAW und ADS")
    col3.metric("MRR Min", f"{total_min_mrr:,.2f} €")
    col3.caption("Summe der Mindest-MRR aller Software- und Hardwareeinheiten")
    col4.metric("MRR List", f"{total_list_mrr:,.2f} €")
    col4.caption("Summe der Listen-MRR aller Software- und Hardwareeinheiten")

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
