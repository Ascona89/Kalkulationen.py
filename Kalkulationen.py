import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import math
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

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

# 🗂 Seitenauswahl
page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Radien", "Contractnumbers"]
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
def show_platform():
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
def show_cardpayment():
    st.header("💳 Cardpayment Vergleich")

    # --- Gemeinsame Inputs für Revenue und Sum of Payments ---
    col_rev, col_sum = st.columns(2)
    with col_rev:
        revenue = persistent_number_input("Revenue (€)", "revenue", 0.0, step=250.0)
    with col_sum:
        sum_payments = persistent_number_input("Sum of payments", "sum_payments", 0.0, step=20.0)

    # --- Actual und Offer Inputs ---
    col1, col2 = st.columns(2)

    # --- Actual ---
    with col1:
        st.subheader("Actual")
        mrr_a = persistent_number_input("Monthly Fee (€)", "mrr_a", 0.0, step=5.0)
        comm_a = persistent_number_input("Commission (%)", "comm_a", 1.39, step=0.01)
        auth_a = persistent_number_input("Authentification Fee (€)", "auth_a", 0.0)

    # --- Offer ---
    with col2:
        st.subheader("Offer")
        mrr_o = persistent_number_input("Monthly Fee (€)", "mrr_o", 0.0, step=5.0)
        comm_o = persistent_number_input("Commission (%)", "comm_o", 1.19, step=0.01)
        auth_o = persistent_number_input("Authentification Fee (€)", "auth_o", 0.06)

    # --- Berechnungen ---
    total_actual = revenue * (comm_a/100) + sum_payments * auth_a + mrr_a
    total_offer  = revenue * (comm_o/100) + sum_payments * auth_o + mrr_o
    saving = total_offer - total_actual
    saving_per_year = saving * 12

    # --- Anzeige ---
    st.markdown("---")
    col3, col4, col5, col6 = st.columns(4)
    col3.markdown(f"<div style='color:red; font-size:28px;'>💳 {total_actual:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Total Actual")
    col4.markdown(f"<div style='color:blue; font-size:28px;'>💳 {total_offer:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Total Offer")
    col5.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving:,.2f} €</div>", unsafe_allow_html=True)
    col5.caption("Ersparnis (Offer - Actual)")
    col6.markdown(f"<div style='color:orange; font-size:28px;'>💸 {saving_per_year:,.2f} €</div>", unsafe_allow_html=True)
    col6.caption("Ersparnis pro Jahr")

# =====================================================
# 💰 Pricing
# =====================================================
def show_pricing():
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

    # ======================
    # Session-State Initialisierung
    # ======================
    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(df_hw)):
        st.session_state.setdefault(f"hw_{i}", 0)

    # ======================
    # Eingabefelder horizontal nebeneinander
    # ======================
    st.subheader("💻 Software")
    sw_cols = st.columns(len(df_sw))
    for i, p in enumerate(df_sw["Produkt"]):
        with sw_cols[i]:
            st.session_state[f"sw_{i}"] = st.number_input(
                p,
                min_value=0,
                step=1,
                value=st.session_state[f"sw_{i}"],
                key=f"sw_ui_{i}"
            )

    st.subheader("🖨️ Hardware")
    hw_cols = st.columns(len(df_hw))
    for i, p in enumerate(df_hw["Produkt"]):
        with hw_cols[i]:
            st.session_state[f"hw_{i}"] = st.number_input(
                p,
                min_value=0,
                step=1,
                value=st.session_state[f"hw_{i}"],
                key=f"hw_ui_{i}"
            )

    # ======================
    # Mengen übernehmen
    # ======================
    df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

    # ======================
    # LIST Preise
    # ======================
    list_otf = (df_sw["Menge"]*df_sw["List_OTF"]).sum() + (df_hw["Menge"]*df_hw["List_OTF"]).sum()
    min_otf = (df_sw["Menge"]*df_sw["Min_OTF"]).sum() + (df_hw["Menge"]*df_hw["Min_OTF"]).sum()
    list_mrr = (df_sw["Menge"]*df_sw["List_MRR"]).sum()
    min_mrr = (df_sw["Menge"]*df_sw["Min_MRR"]).sum()

    st.markdown("### 🧾 LIST PREISE")
    st.markdown(f"**OTF LIST gesamt:** {list_otf:,.2f} €")
    st.markdown(f"**MRR LIST gesamt:** {list_mrr:,.2f} €")
    st.markdown("---")

    # ======================
    # Rabattfunktion
    # ======================
    col_otf, col_otf_reason = st.columns([1,3])
    with col_otf:
        st.session_state['discount_otf'] = st.selectbox(
            "OTF Rabatt (%)",
            [0,5,10,15,20,25,30,35,40,45,50],
            index=[0,5,10,15,20,25,30,35,40,45,50].index(st.session_state.get('discount_otf',0))
        )
    with col_otf_reason:
        st.session_state['reason_otf'] = st.text_input("Grund OTF Rabatt", value=st.session_state.get('reason_otf',''))
        if st.session_state['discount_otf'] > 0 and len(st.session_state['reason_otf']) < 10:
            st.warning("Bitte Begründung eintragen (mindestens 10 Zeichen).")

    col_mrr, col_mrr_reason = st.columns([1,3])
    with col_mrr:
        st.session_state['discount_mrr'] = st.selectbox(
            "MRR Rabatt (%)",
            [0,5,10,15,20,25,30,35,40,45,50],
            index=[0,5,10,15,20,25,30,35,40,45,50].index(st.session_state.get('discount_mrr',0))
        )
    with col_mrr_reason:
        st.session_state['reason_mrr'] = st.text_input("Grund MRR Rabatt", value=st.session_state.get('reason_mrr',''))
        if st.session_state['discount_mrr'] > 0 and len(st.session_state['reason_mrr']) < 10:
            st.warning("Bitte Begründung eintragen (mindestens 10 Zeichen).")

    otf_discounted = list_otf * (1 - st.session_state['discount_otf']/100) \
        if st.session_state['discount_otf'] > 0 and len(st.session_state['reason_otf']) >= 10 else list_otf
    mrr_discounted = list_mrr * (1 - st.session_state['discount_mrr']/100) \
        if st.session_state['discount_mrr'] > 0 and len(st.session_state['reason_mrr']) >= 10 else list_mrr

    st.info(f"OTF nach Rabatt: {otf_discounted:,.2f} €")
    st.info(f"MRR nach Rabatt: {mrr_discounted:,.2f} €")

    st.markdown("---")
    st.markdown("### 🔻 MIN PREISE")
    st.markdown(f"**OTF MIN gesamt:** {min_otf:,.2f} €")
    st.markdown(f"**MRR MIN gesamt:** {min_mrr:,.2f} €")


# =====================================================
# 🗺️ Radien
# =====================================================
def show_radien():
    import requests
    import math
    import folium
    import pandas as pd
    import streamlit as st
    from streamlit_folium import st_folium

    st.header("🗺️ Radien um eine Adresse, Stadt oder PLZ – mehrere Radien möglich")

    CSV_URL = "https://raw.githubusercontent.com/Ascona89/Kalkulationen.py/main/plz_geocoord.csv"

    # ======================
    # PLZ CSV laden
    # ======================
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

    # ======================
    # Inputs
    # ======================
    user_input = st.text_input(
        "📍 Adresse, Stadt oder PLZ eingeben (z.B. Berlin, Alexanderplatz 1 oder 10115)"
    )

    radien_input = st.text_input(
        "📏 Radien eingeben (km, durch Komma getrennt, z.B. 5,10)",
        value="5,10"
    )

    if not user_input.strip():
        return

    # ======================
    # Koordinaten ermitteln
    # ======================
    lat_c, lon_c, location_name = None, None, ""

    # 1️⃣ PLZ direkt aus CSV
    if user_input.strip().isdigit() and len(user_input.strip()) == 5:
        plz_match = df_plz[df_plz["plz"] == user_input.strip()]
        if plz_match.empty:
            st.error("❌ PLZ nicht in Datenbank gefunden.")
            return
        lat_c = plz_match.iloc[0]["lat"]
        lon_c = plz_match.iloc[0]["lon"]
        location_name = f"PLZ: {user_input.strip()}"

    # 2️⃣ Photon Geocoding (cloud-tauglich)
    else:
        headers = {
            "User-Agent": "kalkulations-app/1.0 (contact: support@example.com)"
        }

        try:
            response = requests.get(
                "https://photon.komoot.io/api/",
                params={
                    "q": user_input,
                    "limit": 1,
                    "lang": "de"
                },
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                st.error(f"🌍 Geocoding fehlgeschlagen (Status {response.status_code})")
                return

            data = response.json()

            if "features" not in data or len(data["features"]) == 0:
                st.error("❌ Adresse/Stadt/PLZ konnte nicht gefunden werden.")
                return

            coords = data["features"][0]["geometry"]["coordinates"]
            lon_c, lat_c = coords[0], coords[1]
            location_name = user_input.strip()

        except requests.exceptions.RequestException:
            st.error("🌍 Geocoding-Service aktuell nicht erreichbar.")
            return

    # ======================
    # Radien parsen
    # ======================
    try:
        radien = [float(r.strip()) for r in radien_input.split(",") if r.strip()]
    except ValueError:
        st.error("Bitte nur Zahlen für Radien eingeben, getrennt durch Komma.")
        return

    if len(radien) == 0:
        st.error("Mindestens ein Radius erforderlich.")
        return

    # ======================
    # Haversine
    # ======================
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    df_plz["distance_km"] = df_plz.apply(
        lambda r: haversine(lat_c, lon_c, r["lat"], r["lon"]),
        axis=1
    )

    df_result = df_plz[df_plz["distance_km"] <= max(radien)].sort_values("distance_km")

    # ======================
    # Ergebnisse
    # ======================
    st.success(f"✅ {len(df_result)} PLZ im Umkreis (bis {max(radien)} km)")
    st.dataframe(
        df_result[["plz", "lat", "lon", "distance_km"]],
        use_container_width=True
    )

    # ======================
    # Karte
    # ======================
    m = folium.Map(location=[lat_c, lon_c], zoom_start=11)
    folium.Marker(
        [lat_c, lon_c],
        tooltip=location_name,
        icon=folium.Icon(color="red")
    ).add_to(m)

    for r in radien:
        folium.Circle(
            [lat_c, lon_c],
            radius=r * 1000,
            color="blue",
            fill=True,
            fill_opacity=0.1
        ).add_to(m)

    st_folium(m, width=700, height=500)


# =====================================================
# Contract Numbers
# =====================================================
def show_contractnumbers():
    st.header("📑 Contract Numbers")

    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "TSE"],
        "List_OTF": [999, 49, 999, 49, 0, 0],
        "List_MRR": [119, 49, 89, 25, 15, 12],
        "Typ": ["Software"]*6
    })

    df_hw = pd.DataFrame({
        "Produkt": ["Ordermanager","POS inkl 1 Printer","Cash Drawer","Extra Printer","Additional Display","PAX"],
        "List_OTF": [299,1699,149,199,100,299],
        "List_MRR": [0]*6,
        "Typ": ["Hardware"]*6
    })

    # ======================
    # Sync mit Pricing als Initialwert
    # ======================
    for i in range(len(df_sw)):
        if f"qty_sw_{i}" not in st.session_state:
            st.session_state[f"qty_sw_{i}"] = st.session_state.get(f"sw_{i}", 0)

    for i in range(len(df_hw)):
        if f"qty_hw_{i}" not in st.session_state:
            st.session_state[f"qty_hw_{i}"] = st.session_state.get(f"hw_{i}", 0)

    # ======================
    # Gesamt OTF / MRR Eingabe
    # ======================
    col1, col2 = st.columns(2)
    with col1:
        total_mrr = st.number_input("💶 Gesamt MRR (€)", min_value=0.0, step=50.0, key="total_mrr")
    with col2:
        total_otf = st.number_input("💶 Gesamt OTF (€)", min_value=0.0, step=100.0, key="total_otf")

    st.markdown("---")
    st.subheader("📦 Verkäufe pro Produkt")

    # ======================
    # Software Eingabefelder horizontal
    # ======================
    st.markdown("### 💻 Software")
    sw_cols = st.columns(len(df_sw))
    for idx, row in df_sw.iterrows():
        with sw_cols[idx]:
            st.session_state[f"qty_sw_{idx}"] = st.number_input(
                row["Produkt"],
                min_value=0,
                step=1,
                value=st.session_state[f"qty_sw_{idx}"],
                key=f"qty_sw_input_{idx}"
            )

    # ======================
    # Hardware Eingabefelder horizontal
    # ======================
    st.markdown("### 🖨️ Hardware")
    hw_cols = st.columns(len(df_hw))
    for idx, row in df_hw.iterrows():
        with hw_cols[idx]:
            st.session_state[f"qty_hw_{idx}"] = st.number_input(
                row["Produkt"],
                min_value=0,
                step=1,
                value=st.session_state[f"qty_hw_{idx}"],
                key=f"qty_hw_input_{idx}"
            )

    # ======================
    # Mengen setzen
    # ======================
    df_sw["Menge"] = [st.session_state[f"qty_sw_{i}"] for i in range(len(df_sw))]
    df_hw["Menge"] = [st.session_state[f"qty_hw_{i}"] for i in range(len(df_hw))]

    # ======================
    # OTF Berechnung
    # ======================
    # Basiswerte für Software und Hardware
    sw_base = df_sw["Menge"] * df_sw["List_OTF"]
    hw_base = df_hw["Menge"] * df_hw["List_OTF"]
    total_base = sw_base.sum() + hw_base.sum()

    if total_base > 0:
        scale_factor = total_otf / total_base
    else:
        scale_factor = 0

    df_sw["OTF"] = (sw_base * scale_factor).round(0).astype(int)
    df_hw["OTF"] = (hw_base * scale_factor).round(0).astype(int)

    # ======================
    # MRR Berechnung
    # ======================
    fixed_mrr = {"Connect": 13.72}
    per_unit_mrr = {"TSE": 12.0}

    fixed_active = {prod: val for prod, val in fixed_mrr.items() if df_sw.loc[df_sw["Produkt"]==prod,"Menge"].iloc[0]>0}
    fixed_total = sum(fixed_active.values())

    per_unit_total = sum(df_sw.loc[df_sw["Produkt"]==prod,"Menge"].iloc[0]*val for prod,val in per_unit_mrr.items())
    total_mrr_rest = max(total_mrr - fixed_total - per_unit_total,0)

    variable_sw = df_sw[~df_sw["Produkt"].isin(list(fixed_mrr.keys()) + list(per_unit_mrr.keys()))]
    variable_values = variable_sw["Menge"] * variable_sw["List_MRR"]

    if variable_values.sum() > 0:
        prop = variable_values / variable_values.sum()
        mrr_rest_values = prop * total_mrr_rest
    else:
        mrr_rest_values = [0]*len(variable_sw)

    df_sw.loc[variable_sw.index,"MRR_Monat"] = mrr_rest_values
    df_sw.loc[variable_sw.index,"MRR_Woche"] = [v/4 for v in mrr_rest_values]

    for prod,val in fixed_active.items():
        df_sw.loc[df_sw["Produkt"]==prod,"MRR_Monat"] = val
        df_sw.loc[df_sw["Produkt"]==prod,"MRR_Woche"] = val/4

    for prod,val in per_unit_mrr.items():
        qty = df_sw.loc[df_sw["Produkt"]==prod,"Menge"].iloc[0]
        df_sw.loc[df_sw["Produkt"]==prod,"MRR_Monat"] = qty*val
        df_sw.loc[df_sw["Produkt"]==prod,"MRR_Woche"] = (qty*val)/4

    df_hw["MRR_Monat"] = 0
    df_hw["MRR_Woche"] = 0

    # ======================
    # Ergebnisse
    # ======================
    st.markdown("---")
    st.subheader("✅ Ergebnisse")
    df_result = pd.concat([df_sw, df_hw], ignore_index=True)

    for idx, row in df_result.iterrows():
        cols = st.columns([2,1,1,1])
        cols[0].markdown(f"**{row['Produkt']}**")
        cols[1].markdown(f"OTF: {row['OTF']} €")
        cols[2].markdown(f"MRR/Monat: {row['MRR_Monat']:.2f} €")
        cols[3].markdown(f"MRR/Woche: {row['MRR_Woche']:.2f} €")

    # ======================
    # Kontrollübersicht
    # ======================
    st.subheader("📊 Kontrollübersicht")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💻 Software OTF", f"{df_sw['OTF'].sum()} €")
        st.metric("🖨️ Hardware OTF", f"{df_hw['OTF'].sum()} €")
    with col2:
        st.metric("🧾 OTF berechnet", f"{df_result['OTF'].sum()} €")
        st.metric("🧾 OTF Eingabe", f"{total_otf} €")
    with col3:
        st.metric("💰 MRR / Monat", f"{df_result['MRR_Monat'].sum():.2f} €")
        st.metric("📆 MRR / Woche", f"{df_result['MRR_Woche'].sum():.2f} €")

# =====================================================
# 🏗 Seitenlogik
# =====================================================
# 🌐 Seiten-Dispatcher
if page == "Platform":
    show_platform()
elif page == "Cardpayment":
    show_cardpayment()
elif page == "Pricing":
    show_pricing()
elif page == "Radien":
    show_radien()
elif page == "Contractnumbers":
    show_contractnumbers()  # <-- Korrekt
