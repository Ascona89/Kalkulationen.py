import streamlit as st
import pandas as pd

# ---------------- page config ----------------
st.set_page_config(page_title="Kalkulations-App", layout="wide")

# ---------------- simple login ----------------
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

# ---------------- main app (after login) ----------------
if st.session_state["login_status"]:
    st.title("📊 Kalkulations-App")

    # helper to init session state defaults
    def init_session_state(defaults: dict):
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

    # sidebar menu
    page = st.sidebar.radio("Wähle eine Kalkulation:", ["Platform", "Cardpayment", "Pricing"])

    # ---------------- PLATFORM (früher Competitor) ----------------
    if page == "Platform":
        st.header("🏁 Platform Kalkulation")

        init_session_state({
            "revenue": 0.0, "commission_pct": 14.0, "avg_order_value": 25.0,
            "service_fee": 0.69, "OTF": 0.0, "MRR": 0.0, "contract_length": 24
        })

        col_left, col_right = st.columns([2, 1.4])

        with col_left:
            st.subheader("Eingaben")
            st.number_input("Revenue on platform (€)", key="revenue", step=250.0,
                            help="Gesamter Umsatz auf der Plattform (Schritte 250)")
            st.number_input("Commission (%)", key="commission_pct", step=1.0,
                            help="Provision in Prozent (Schritte 1%)")
            st.number_input("Average order value (€)", key="avg_order_value", step=5.0,
                            help="Durchschnittlicher Bestellwert (Schritte 5€), Standard 25€")
            st.number_input("Service Fee (€)", key="service_fee", step=0.1,
                            help="Feste Service-/Transaktionsgebühr pro Bestellung (Schritte 0.1€)")

            # Ergebnis direkt unter Service Fee
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
            st.number_input("Contract length (Monate)", key="contract_length", step=12,
                            help="Standard 24, Schritte 12")

        # right column: KPIs
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
            st.number_input("Revenue (€)", key="rev_a", step=250.0,
                            help="Umsatz (Schritte 250)")
            st.number_input("Sum of payments", key="sum_a", step=20, format="%d",
                            help="Anzahl Transaktionen (Schritte 20)")
            st.number_input("Monthly Fee (€)", key="mrr_a", step=5.0,
                            help="Monatliche Gebühr (Schritte 5)")
            st.number_input("Commission (%)", key="comm_a", step=0.01,
                            help="Provision in Prozent (Schritte 0.01%)")
            st.number_input("Authentification Fee (€)", key="auth_a",
                            help="Authentifizierungsgebühr pro Zahlung")

        with col_o:
            st.subheader("Offer")
            # Übernahme der Werte ohne value= (schreibt in session_state)
            st.session_state.rev_o = st.session_state.rev_a
            st.session_state.sum_o = st.session_state.sum_a

            st.number_input("Revenue (€)", key="rev_o", step=250.0,
                            help="Umsatz (vom Actual übernommen, änderbar)")
            st.number_input("Sum of payments", key="sum_o", step=20,
                            help="Transaktionen (vom Actual übernommen, änderbar)")
            st.number_input("Monthly Fee (€)", key="mrr_o", step=5.0,
                            help="Monatliche Gebühr")
            st.number_input("Commission (%)", key="comm_o", step=0.01,
                            help="Provision in Prozent")
            st.number_input("Authentification Fee (€)", key="auth_o",
                            help="Authentifizierungsgebühr pro Zahlung")

        # Berechnung
        total_actual = st.session_state.rev_a * (st.session_state.comm_a / 100) + \
                       st.session_state.sum_a * st.session_state.auth_a + st.session_state.mrr_a
        total_offer = st.session_state.rev_o * (st.session_state.comm_o / 100) + \
                      st.session_state.sum_o * st.session_state.auth_o + st.session_state.mrr_o
        saving = total_offer - total_actual

        st.markdown("---")
        rcol1, rcol2, rcol3 = st.columns([1,1,1])
        rcol1.metric("Total Actual", f"{total_actual:,.2f} €")
        rcol2.metric("Total Offer", f"{total_offer:,.2f} €")
        rcol3.metric("Ersparnis", f"{saving:,.2f} €")

    # ---------------- PRICING ----------------
    elif page == "Pricing":
        st.header("💰 Pricing Kalkulation")

        # Software / Hardware data (first column removed as requested earlier)
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

        # init session state for quantities and gaw value
        for i in range(len(software)):
            key = f"sw_{i}"
            if key not in st.session_state:
                st.session_state[key] = 0
        for i in range(len(hardware)):
            key = f"hw_{i}"
            if key not in st.session_state:
                st.session_state[key] = 0
        if "gaw_qty" not in st.session_state:
            st.session_state["gaw_qty"] = 1
        if "gaw_value" not in st.session_state:
            st.session_state["gaw_value"] = 50.0

        sw_col, hw_col = st.columns(2)

        # SOFTWARE inputs
        with sw_col:
            st.subheader("🧩 Software")
            for i, prod in enumerate(software):
                if prod["Produkt"] != "GAW":
                    st.number_input(f"{prod['Produkt']} Menge", key=f"sw_{i}", min_value=0, step=1)
            # GAW inputs
            st.number_input("GAW Menge", key="gaw_qty", min_value=0, step=1)
            st.number_input("GAW Betrag (€)", key="gaw_value", min_value=0.0, step=25.0, value=st.session_state["gaw_value"])

            # dynamic logic: Shop -> ordermanager; POS -> ordermanager off & POS inkl printer on
            shop_selected = st.session_state.get("sw_0", 0) > 0
            pos_selected = st.session_state.get("sw_2", 0) > 0
            # ensure hardware session keys exist
            if "hw_0" not in st.session_state:
                st.session_state["hw_0"] = 0
            if "hw_1" not in st.session_state:
                st.session_state["hw_1"] = 0
            if shop_selected:
                if st.session_state["hw_0"] < 1:
                    st.session_state["hw_0"] = 1
            if pos_selected:
                st.session_state["hw_0"] = 0
                if st.session_state["hw_1"] < 1:
                    st.session_state["hw_1"] = 1

        # HARDWARE inputs
        with hw_col:
            st.subheader("🖥️ Hardware")
            for i, prod in enumerate(hardware):
                st.number_input(f"{prod['Produkt']}", key=f"hw_{i}", min_value=0, step=1)

        # assemble dataframes for calculations
        df_sw = pd.DataFrame(software)
        df_hw = pd.DataFrame(hardware)
        # quantities from session state
        df_sw["Menge"] = [st.session_state.get(f"sw_{i}", 0) for i in range(len(df_sw))]
        # overwrite GAW Menge with gaw_qty session
        gaw_index = df_sw.index[df_sw["Produkt"]=="GAW"].tolist()
        if gaw_index:
            df_sw.at[gaw_index[0], "Menge"] = st.session_state["gaw_qty"]
        df_hw["Menge"] = [st.session_state.get(f"hw_{i}", 0) for i in range(len(df_hw))]

        # calculations: OTF and MRR sums
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

        # display results inline, compact, colored (Min = red, List = green)
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

        # detail table hidden below
        with st.expander("Preisdetails anzeigen"):
            # format numbers with euro sign
            df_show_sw = df_sw[["Produkt","Menge","Min_OTF","List_OTF","Min_MRR","List_MRR"]].copy()
            df_show_hw = df_hw[["Produkt","Menge","Min_OTF","List_OTF","Min_MRR","List_MRR"]].copy()
            df_show = pd.concat([df_show_sw, df_show_hw], ignore_index=True)
            # format numeric columns as integers with euro sign for OTFS
            df_show["Min_OTF"] = df_show["Min_OTF"].map(lambda x: f"{x:,.0f} €")
            df_show["List_OTF"] = df_show["List_OTF"].map(lambda x: f"{x:,.0f} €")
            df_show["Min_MRR"] = df_show["Min_MRR"].map(lambda x: f"{x:,.0f} €")
            df_show["List_MRR"] = df_show["List_MRR"].map(lambda x: f"{x:,.0f} €")
            st.dataframe(df_show.style.set_properties(**{"font-family":"monospace"}), use_container_width=True, hide_index=True)

    # ---------------- footer ----------------
    st.markdown("""
    <hr style="margin:20px 0;">
    <p style='text-align:center; font-size:0.9rem; color:gray;'>
    😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
    </p>
    """, unsafe_allow_html=True)
