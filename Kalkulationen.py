import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import math
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# =====================================================
# 🔐 Passwörter
# =====================================================
USER_PASSWORD = "welovekb"
ADMIN_PASSWORD = "sebaforceo"

# =====================================================
# 🧠 Supabase
# =====================================================
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def log_login(role, success):
    supabase.table("login_events").insert({
        "role": role,
        "success": success,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

# =====================================================
# 🧠 Session State Initialisierung
# =====================================================
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("is_admin", False)
st.session_state.setdefault("USER_PASSWORD", USER_PASSWORD)
st.session_state.setdefault("show_map", False)

# =====================================================
# 🔐 Login
# =====================================================
def login(password):
    user_pw = st.session_state.get("USER_PASSWORD", USER_PASSWORD)
    if password == user_pw:
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        log_login("User", True)
        st.rerun()
    elif password == ADMIN_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = True
        log_login("Admin", True)
        st.rerun()
    else:
        log_login("Unknown", False)
        st.error("❌ Falsches Passwort")

if not st.session_state.logged_in:
    st.title("🔐 Login erforderlich")
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        login(pw)
    st.stop()

# =====================================================
# 👑 Admin Backend
# =====================================================
if st.session_state.is_admin:
    st.header("👑 Admin Dashboard")

    data = supabase.table("login_events").select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(data.data)
    if not df.empty:
        df["Datum"] = pd.to_datetime(df["created_at"]).dt.date
        st.subheader("📄 Login-Historie")
        st.dataframe(df, use_container_width=True)
        st.subheader("📊 Logins pro Tag")
        logins_per_day = df[df["success"]==True].groupby("Datum").size().reset_index(name="Logins")
        st.dataframe(logins_per_day, use_container_width=True)
        st.bar_chart(logins_per_day.set_index("Datum"))
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("CSV Export", csv, "login_history.csv", "text/csv")
    else:
        st.info("Noch keine Login-Daten vorhanden.")

    st.subheader("🔑 User Passwort ändern")
    new_password = st.text_input("Neues User-Passwort", type="password")
    if st.button("Update User Passwort"):
        if new_password:
            st.session_state['USER_PASSWORD'] = new_password
            st.success("✅ Passwort erfolgreich geändert!")
        else:
            st.warning("Bitte ein gültiges Passwort eingeben.")
    st.stop()

# =====================================================
# 🔧 App Setup
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

# 🗂 Seitenauswahl (Sidebar) – erweitert um Contract Numbers
page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Radien", "Telesales", "Contract Numbers"]
)

# ==========================
# Hilfsfunktionen für persistente Inputs
# ==========================
def persistent_number_input(label, key, value=0.0, **kwargs):
    st.session_state.setdefault(key, value)
    st.session_state[key] = st.number_input(label, value=st.session_state[key], key=f"ui_{key}", **kwargs)
    return st.session_state[key]

def persistent_text_input(label, key, value="", **kwargs):
    st.session_state.setdefault(key, value)
    st.session_state[key] = st.text_input(label, value=st.session_state[key], key=f"ui_{key}", **kwargs)
    return st.session_state[key]

def persistent_selectbox(label, key, options, index=0, **kwargs):
    st.session_state.setdefault(key, options[index])
    st.session_state[key] = st.selectbox(label, options, index=options.index(st.session_state[key]), **kwargs)
    return st.session_state[key]

# =====================================================
# 🏁 Platform
# =====================================================
if page == "Platform":
    st.header("🏁 Platform Kalkulation")
    col1, col2 = st.columns([2, 1.5])

    with col1:
        st.subheader("Eingaben")
        revenue = persistent_number_input("Revenue on platform (€)", "revenue", 0.0, step=250.0)
        commission_pct = persistent_number_input("Commission (%)", "commission_pct", 14.0, step=1.0)
        avg_order_value = persistent_number_input("Average order value (€)", "avg_order_value", 25.0, step=5.0)
        service_fee = persistent_number_input("Service Fee (€)", "service_fee", 0.69, step=0.1)

        total_cost = revenue*(commission_pct/100) + \
                     (0.7*revenue/avg_order_value if avg_order_value else 0)*service_fee

        st.markdown("### 💶 Cost on Platform")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Vertragsdetails")
        OTF = persistent_number_input("One Time Fee (OTF) (€)", "OTF", 0.0, step=100.0)
        MRR = persistent_number_input("Monthly Recurring Revenue (MRR) (€)", "MRR", 0.0, step=10.0)
        contract_length = persistent_number_input("Contract length (Monate)", "contract_length", 24, step=12)

    transaction = 0.7*revenue/5*0.35
    cost_monthly = MRR + transaction
    saving_monthly = total_cost - cost_monthly
    saving_over_contract = saving_monthly*contract_length

    st.subheader("📊 Kennzahlen")
    st.info(
        f"- Cost monthly: {cost_monthly:,.2f} €\n"
        f"- Saving monthly: {saving_monthly:,.2f} €\n"
        f"- Saving over contract length: {saving_over_contract:,.2f} €"
    )

# =====================================================
# 💳 Cardpayment
# =====================================================
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Actual")
        rev_a = persistent_number_input("Revenue (€)", "rev_a", 0.0, step=250.0)
        sum_a = persistent_number_input("Sum of payments", "sum_a", 0.0, step=20.0)
        mrr_a = persistent_number_input("Monthly Fee (€)", "mrr_a", 0.0, step=5.0)
        comm_a = persistent_number_input("Commission (%)", "comm_a", 1.39, step=0.01)
        auth_a = persistent_number_input("Authentification Fee (€)", "auth_a", 0.0)

    with col2:
        st.subheader("Offer")
        rev_o = persistent_number_input("Revenue (€)", "rev_o", rev_a, step=250.0)
        sum_o = persistent_number_input("Sum of payments", "sum_o", sum_a, step=20.0)
        mrr_o = persistent_number_input("Monthly Fee (€)", "mrr_o", 0.0, step=5.0)
        comm_o = persistent_number_input("Commission (%)", "comm_o", 1.19, step=0.01)
        auth_o = persistent_number_input("Authentification Fee (€)", "auth_o", 0.06)

    total_actual = rev_a*(comm_a/100) + sum_a*auth_a + mrr_a
    total_offer  = rev_o*(comm_o/100) + sum_o*auth_o + mrr_o
    saving = total_offer - total_actual

    st.markdown("---")
    col3, col4, col5 = st.columns(3)
    col3.markdown(f"<div style='color:red; font-size:28px;'>💳 {total_actual:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Total Actual")
    col4.markdown(f"<div style='color:blue; font-size:28px;'>💳 {total_offer:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Total Offer")
    col5.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving:,.2f} €</div>", unsafe_allow_html=True)
    col5.caption("Ersparnis (Offer - Actual)")

# =====================================================
# 💰 Pricing
# =====================================================
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")

    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "GAW"],
        "Min_OTF": [365, 15, 365, 35, 0, 0],
        "List_OTF": [999, 49, 999, 49, 0, 0],
        "Min_MRR": [50, 15, 49, 5, 15, 0],
        "List_MRR": [119, 49, 89, 25, 15, 0]
    })

    df_hw = pd.DataFrame({
        "Produkt":["Ordermanager","POS inkl 1 Printer","Cash Drawer","Extra Printer","Additional Display","PAX"],
        "Min_OTF":[135,350,50,99,100,225],
        "List_OTF":[299,1699,149,199,100,299],
        "Min_MRR":[0]*6,
        "List_MRR":[0]*6
    })

    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(df_hw)):
        st.session_state.setdefault(f"hw_{i}", 0)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Software")
        for i, p in enumerate(df_sw["Produkt"]):
            st.session_state[f"sw_{i}"] = st.number_input(p, min_value=0, step=1, key=f"sw_ui_{i}")
    with col2:
        st.subheader("Hardware")
        for i, p in enumerate(df_hw["Produkt"]):
            st.session_state[f"hw_{i}"] = st.number_input(p, min_value=0, step=1, key=f"hw_ui_{i}")

    df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

    list_otf = (df_sw["Menge"]*df_sw["List_OTF"]).sum() + (df_hw["Menge"]*df_hw["List_OTF"]).sum()
    min_otf = (df_sw["Menge"]*df_sw["Min_OTF"]).sum() + (df_hw["Menge"]*df_hw["Min_OTF"]).sum()
    list_mrr = (df_sw["Menge"]*df_sw["List_MRR"]).sum()
    min_mrr = (df_sw["Menge"]*df_sw["Min_MRR"]).sum()

    st.markdown("### 🧾 LIST PREISE")
    st.markdown(f"**OTF LIST gesamt:** {list_otf:,.2f} €")
    st.markdown(f"**MRR LIST gesamt:** {list_mrr:,.2f} €")
    st.markdown("---")

    st.subheader("💸 Rabattfunktion")
    col_otf, col_otf_reason = st.columns([1,3])
    with col_otf:
        st.session_state['discount_otf'] = st.selectbox("OTF Rabatt (%)", [0,5,10,15,20,25,30,35,40,45,50], 
                                                       index=[0,5,10,15,20,25,30,35,40,45,50].index(st.session_state.get('discount_otf',0)))
    with col_otf_reason:
        st.session_state['reason_otf'] = st.text_input("Grund OTF Rabatt", value=st.session_state.get('reason_otf',''))
        if st.session_state['discount_otf'] > 0 and len(st.session_state['reason_otf']) < 10:
            st.warning("Bitte Begründung eintragen (mindestens 10 Zeichen).")

    col_mrr, col_mrr_reason = st.columns([1,3])
    with col_mrr:
        st.session_state['discount_mrr'] = st.selectbox("MRR Rabatt (%)", [0,5,10,15,20,25,30,35,40,45,50], 
                                                       index=[0,5,10,15,20,25,30,35,40,45,50].index(st.session_state.get('discount_mrr',0)))
    with col_mrr_reason:
        st.session_state['reason_mrr'] = st.text_input("Grund MRR Rabatt", value=st.session_state.get('reason_mrr',''))
        if st.session_state['discount_mrr'] > 0 and len(st.session_state['reason_mrr']) < 10:
            st.warning("Bitte Begründung eintragen (mindestens 10 Zeichen).")

    otf_discounted = list_otf * (1 - st.session_state['discount_otf']/100) if st.session_state['discount_otf'] > 0 and len(st.session_state['reason_otf']) >= 10 else list_otf
    mrr_discounted = list_mrr * (1 - st.session_state['discount_mrr']/100) if st.session_state['discount_mrr'] > 0 and len(st.session_state['reason_mrr']) >= 10 else list_mrr

    st.info(f"OTF nach Rabatt: {otf_discounted:,.2f} €")
    st.info(f"MRR nach Rabatt: {mrr_discounted:,.2f} €")

    st.markdown("---")
    st.markdown("### 🔻 MIN PREISE")
    st.markdown(f"**OTF MIN gesamt:** {min_otf:,.2f} €")
    st.markdown(f"**MRR MIN gesamt:** {min_mrr:,.2f} €")

# =====================================================
# 🗺️ Radien
# =====================================================
elif page == "Radien":
    st.header("🗺️ Radien um eine Adresse")

    adresse = persistent_text_input("Adresse eingeben", "adresse")
    radien_input = persistent_text_input("Radien eingeben (km, durch Komma getrennt)", "radien_input", "5,10")

    if st.button("Karte anzeigen"):
        st.session_state['show_map'] = True

    if st.session_state.get('show_map', False):
        if adresse.strip() and radien_input.strip():
            try:
                radien = [float(r.strip()) for r in radien_input.split(",") if r.strip()]
            except ValueError:
                st.warning("Bitte nur Zahlen für Radien eingeben, getrennt durch Komma.")
                radien = []

            if radien:
                geolocator = Nominatim(user_agent="streamlit-free-radius-map", timeout=10)
                try:
                    location = geolocator.geocode(adresse)
                    if location:
                        lat, lon = location.latitude, location.longitude

                        m = folium.Map(location=[lat, lon], zoom_start=12)
                        folium.Marker(
                            [lat, lon],
                            popup=adresse,
                            tooltip="Zentrum",
                            icon=folium.Icon(color="red", icon="info-sign")
                        ).add_to(m)

                        bounds = []
                        for r in radien:
                            folium.Circle(
                                location=[lat, lon],
                                radius=r*1000,
                                color="blue",
                                weight=2,
                                fill=True,
                                fill_opacity=0.15
                            ).add_to(m)

                            bounds.append([lat + r/111, lon + r/111])
                            bounds.append([lat - r/111, lon - r/111])

                        m.fit_bounds(bounds)
                        st_folium(m, width=1000, height=600)
                    else:
                        st.warning("Adresse nicht gefunden.")
                except Exception as e:
                    st.error(f"Fehler bei Geocoding: {e}")
            else:
                st.warning("Bitte gültige Radien eingeben.")
        else:
            st.warning("Bitte Adresse eingeben und mindestens einen Radius angeben.")

# =====================================================
# =================== TELESSALES ======================
# =====================================================
elif page == "Telesales":
    st.header("📞 Telesales – PLZ im Radius")

    # CSV mit PLZ-Daten lokal oder vom GitHub Repo
    CSV_URL = "https://raw.githubusercontent.com/Ascona89/Kalkulationen.py/main/plz_geocoord.csv"

    @st.cache_data
    def load_plz_data():
        df = pd.read_csv(CSV_URL, dtype=str)
        for col in ["plz", "lat", "lon"]:
            if col not in df.columns:
                st.error(f"Spalte '{col}' fehlt in der CSV!")
                st.stop()
        df["lat"] = df["lat"].astype(float)
        df["lon"] = df["lon"].astype(float)
        return df

    df_plz = load_plz_data()

    st.session_state.setdefault("show_result", False)
    st.session_state.setdefault("df_result", None)
    st.session_state.setdefault("center", None)

    col1, col2 = st.columns(2)
    with col1:
        center_input = st.text_input("📍 Stadt oder PLZ", placeholder="z.B. Berlin oder 10115")
    with col2:
        radius_km = st.number_input("📏 Radius (km)", min_value=1, max_value=300, value=10, step=1)

    if st.button("PLZ im Radius anzeigen"):
        geolocator = Nominatim(user_agent="telesales_radius_app", timeout=10)
        loc = geolocator.geocode(center_input)
        if loc:
            lat0, lon0 = loc.latitude, loc.longitude
            st.session_state.center = (lat0, lon0)
            # Haversine Distance
            df_plz["distance"] = df_plz.apply(
                lambda row: 6371*math.acos(
                    math.cos(math.radians(lat0))*math.cos(math.radians(row["lat"]))*
                    math.cos(math.radians(row["lon"])-math.radians(lon0))+
                    math.sin(math.radians(lat0))*math.sin(math.radians(row["lat"]))
                ), axis=1)
            df_result = df_plz[df_plz["distance"]<=radius_km].copy()
            st.session_state.df_result = df_result
            st.session_state.show_result = True
        else:
            st.warning("Adresse nicht gefunden.")

    if st.session_state.show_result and st.session_state.df_result is not None:
        st.subheader("Ergebnisse")
        st.dataframe(st.session_state.df_result[["plz","ort","distance"]].sort_values("distance"), use_container_width=True)
        # Karte
        df_map = st.session_state.df_result
        m = folium.Map(location=st.session_state.center, zoom_start=10)
        folium.Marker(
            location=st.session_state.center,
            popup=center_input,
            icon=folium.Icon(color="red")
        ).add_to(m)
        for _, row in df_map.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=5,
                popup=f"{row['plz']} {row['ort']} ({row['distance']:.1f} km)",
                color="blue",
                fill=True,
                fill_opacity=0.7
            ).add_to(m)
        st_folium(m, width=1000, height=600)

# =====================================================
# =================== Contract Numbers ======================
# =====================================================
elif page == "Contract Numbers":
    st.header("📑 Contract Numbers")

    # Produkte
    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "GAW"],
        "List_OTF": [999, 49, 999, 49, 0, 0],
        "List_MRR": [119, 49, 89, 25, 15, 0],
        "Typ": ["Software"]*6
    })

    df_hw = pd.DataFrame({
        "Produkt":["Ordermanager","POS inkl 1 Printer","Cash Drawer","Extra Printer","Additional Display","PAX"],
        "List_OTF":[299,1699,149,199,100,299],
        "List_MRR":[0]*6,
        "Typ": ["Hardware"]*6
    })

    df_products = pd.concat([df_sw, df_hw], ignore_index=True)

    # Eingaben Gesamtwerte
    col1, col2 = st.columns(2)
    with col1:
        total_mrr = st.number_input("💶 Gesamt MRR (€)", min_value=0.0, step=50.0)
    with col2:
        total_otf = st.number_input("💶 Gesamt OTF (€)", min_value=0.0, step=100.0)

    st.markdown("---")
    st.subheader("📦 Verkäufe pro Produkt")

    # Menge für jedes Produkt
    for i in df_products.index:
        st.session_state.setdefault(f"cn_qty_{i}", 0)

    # Berechnung der OTF- und MRR-Anteile
    df_products["Menge"] = 0
    for i, row in df_products.iterrows():
        col_qty, col_otf, col_mrr_mon, col_mrr_week = st.columns([2,1,1,1])
        with col_qty:
            qty = st.number_input(row["Produkt"], min_value=0, step=1, key=f"cn_qty_{i}")
            df_products.at[i, "Menge"] = qty

    # OTF-Verteilung nach Software / Hardware
    df_sw_sel = df_products[(df_products["Typ"]=="Software") & (df_products["Menge"]>0)]
    df_hw_sel = df_products[(df_products["Typ"]=="Hardware") & (df_products["Menge"]>0)]

    sw_total_list_otf = (df_sw_sel["List_OTF"] * df_sw_sel["Menge"]).sum()
    hw_total_list_otf = (df_hw_sel["List_OTF"] * df_hw_sel["Menge"]).sum()
    total_list_otf = sw_total_list_otf + hw_total_list_otf

    sw_otf_total = total_otf * (sw_total_list_otf / total_list_otf) if total_list_otf>0 else 0
    hw_otf_total = total_otf * (hw_total_list_otf / total_list_otf) if total_list_otf>0 else 0

    df_products["OTF_Anteil"] = 0.0
    if sw_total_list_otf > 0:
        df_products.loc[df_sw_sel.index, "OTF_Anteil"] = (
            df_products.loc[df_sw_sel.index, "List_OTF"] * df_products.loc[df_sw_sel.index, "Menge"]
            / sw_total_list_otf * sw_otf_total
        )
    if hw_total_list_otf > 0:
        df_products.loc[df_hw_sel.index, "OTF_Anteil"] = (
            df_products.loc[df_hw_sel.index, "List_OTF"] * df_products.loc[df_hw_sel.index, "Menge"]
            / hw_total_list_otf * hw_otf_total
        )

    # MRR-Verteilung nur Software
    df_products["MRR_Monat"] = 0.0
    df_products["MRR_Woche"] = 0.0
    sw_total_list_mrr = (df_sw_sel["List_MRR"] * df_sw_sel["Menge"]).sum()
    if sw_total_list_mrr > 0 and total_mrr > 0:
        df_products.loc[df_sw_sel.index, "MRR_Monat"] = (
            df_products.loc[df_sw_sel.index, "List_MRR"] * df_products.loc[df_sw_sel.index, "Menge"]
            / sw_total_list_mrr * total_mrr
        )
        df_products.loc[df_sw_sel.index, "MRR_Woche"] = df_products.loc[df_sw_sel.index, "MRR_Monat"] / 4

    # Ergebnisse direkt neben jedem Number Input anzeigen
    for i, row in df_products.iterrows():
        col_qty, col_otf, col_mrr_mon, col_mrr_week = st.columns([2,1,1,1])
        with col_otf:
            st.write(f"OTF: {row['OTF_Anteil']:.2f} €")
        with col_mrr_mon:
            st.write(f"MRR/Monat: {row['MRR_Monat']:.2f} €")
        with col_mrr_week:
            st.write(f"MRR/Woche: {row['MRR_Woche']:.2f} €")

    # Zusammenfassende Kontrolle
    st.markdown("---")
    st.subheader("✅ Kontrollübersicht")
    col1, col2, col3 = st.columns(3)
    otf_software = df_products[df_products["Typ"]=="Software"]["OTF_Anteil"].sum()
    otf_hardware = df_products[df_products["Typ"]=="Hardware"]["OTF_Anteil"].sum()
    total_mrr_calc = df_products["MRR_Monat"].sum()
    total_otf_calc = df_products["OTF_Anteil"].sum()
    with col1:
        st.metric("💻 Software OTF", f"{otf_software:,.2f} €")
        st.metric("🖨️ Hardware OTF", f"{otf_hardware:,.2f} €")
    with col2:
        st.metric("🧾 OTF berechnet", f"{total_otf_calc:,.2f} €")
        st.metric("🧾 OTF Eingabe", f"{total_otf:,.2f} €")
    with col3:
        st.metric("💰 MRR / Monat", f"{total_mrr_calc:,.2f} €")
        st.metric("📆 MRR / Woche", f"{total_mrr_calc/4:,.2f} €")
