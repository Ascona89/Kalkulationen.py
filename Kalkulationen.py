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
USER_PASSWORD = "oyysouth"
SILENT_USER_PASSWORD = "silentlogin"
ADMIN_PASSWORD = "sebaforceo"
PIPELINE_PASSWORDS = {
    "south": "south",
    "mids": "mids",
    "east": "east",
    "north": "north"
}

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

    elif password == SILENT_USER_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        # bewusst KEIN log_login
        st.rerun()

    elif password == ADMIN_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.is_admin = True
        log_login("Admin", True)
        st.rerun()

    else:
        log_login("Unknown", False)
        st.error("❌ Falsches Passwort")
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
# 🔐 Login Abfrage
# =====================================================
if not st.session_state.get("logged_in", False):
    st.header("🔐 Login")
    pw = st.text_input("Passwort eingeben", type="password")
    if st.button("Login"):
        login(pw)
    st.stop()

# =====================================================
# 🔧 App Setup
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Radien", "Contractnumbers", "Pipeline"]
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
        toprank_per_order = persistent_number_input("TopRank per Order (€)", "toprank_per_order", 0.0, step=0.1)

        # ==============================
        # 🧮 Berechnung Cost on Platform direkt nach Eingaben
        # ==============================
        cost_platform = revenue * (commission_pct / 100) + \
                        (0.7 * revenue / avg_order_value if avg_order_value else 0) * service_fee

        sum_of_orders = revenue / avg_order_value if avg_order_value else 0
        toprank_cost = sum_of_orders * toprank_per_order

        total_cost = cost_platform + toprank_cost

        st.markdown("### 💶 Cost on Platform")
        st.markdown(f"<div style='color:red; font-size:28px;'>{total_cost:,.2f} €</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Vertragsdetails")
        OTF = persistent_number_input("One Time Fee (OTF) (€)", "OTF", 0.0, step=100.0)
        MRR = persistent_number_input("Monthly Recurring Revenue (MRR) (€)", "MRR", 0.0, step=10.0)
        contract_length = persistent_number_input("Contract length (Monate)", "contract_length", 24, step=12)

    # ==============================
    # Transaktion & monatliche Kosten
    # ==============================
    transaction = 0.7 * revenue / 5 * 0.35
    cost_monthly = MRR + transaction
    saving_monthly = total_cost - cost_monthly
    saving_over_contract = saving_monthly * contract_length

    # ==============================
    # 📊 Kennzahlen farbig dargestellt (wie Cardpayment)
    # ==============================
    st.markdown("---")
    st.subheader("📊 Kennzahlen")
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"<div style='color:red; font-size:28px;'>💶 {total_cost:,.2f} €</div>", unsafe_allow_html=True)
    col1.caption("Total Platform Cost")

    col2.markdown(f"<div style='color:blue; font-size:28px;'>💳 {cost_monthly:,.2f} €</div>", unsafe_allow_html=True)
    col2.caption("Cost Monthly (MRR + Transaction)")

    col3.markdown(f"<div style='color:green; font-size:28px;'>💰 {saving_monthly:,.2f} €</div>", unsafe_allow_html=True)
    col3.caption("Saving Monthly")

    col4.markdown(f"<div style='color:orange; font-size:28px;'>💸 {saving_over_contract:,.2f} €</div>", unsafe_allow_html=True)
    col4.caption("Saving over Contract Length")

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

    for i in range(len(df_sw)):
        st.session_state.setdefault(f"sw_{i}", 0)
    for i in range(len(df_hw)):
        st.session_state.setdefault(f"hw_{i}", 0)

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

    df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

    # 🔁 Übergabe an Contract Numbers
    for i in range(len(df_sw)):
        st.session_state[f"contract_sw_{i}"] = st.session_state[f"sw_{i}"]
    for i in range(len(df_hw)):
        st.session_state[f"contract_hw_{i}"] = st.session_state[f"hw_{i}"]

    list_otf = (df_sw["Menge"]*df_sw["List_OTF"]).sum() + (df_hw["Menge"]*df_hw["List_OTF"]).sum()
    min_otf = (df_sw["Menge"]*df_sw["Min_OTF"]).sum() + (df_hw["Menge"]*df_hw["Min_OTF"]).sum()
    list_mrr = (df_sw["Menge"]*df_sw["List_MRR"]).sum()
    min_mrr = (df_sw["Menge"]*df_sw["Min_MRR"]).sum()

    st.markdown("### 🧾 LIST PREISE")
    st.markdown(f"**OTF LIST gesamt:** {list_otf:,.2f} €")
    st.markdown(f"**MRR LIST gesamt:** {list_mrr:,.2f} €")
    st.markdown("---")

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
    import math
    import folium
    import pandas as pd
    from streamlit_folium import st_folium
    import json
    import requests
    import streamlit as st

    st.header("🗺️ Radien oder PLZ-Flächen anzeigen")

    # =====================================================
    # Session State für PLZ-Flächen
    # =====================================================
    if "plz_blocks" not in st.session_state:
        st.session_state["plz_blocks"] = [
            {"plz": "", "min_order": 0.0, "delivery_cost": 0.0}
        ]

    # =====================================================
    # Eingabe & Modus
    # =====================================================
    col_input, col_mode = st.columns([3, 1])
    with col_input:
        user_input = st.text_input(
            "📍 Adresse, Stadt oder PLZ eingeben (nur für Radien)"
        )
    with col_mode:
        mode = st.selectbox("Anzeige-Modus", ["Radien", "PLZ-Flächen"])

    # =====================================================
    # Karte vorbereiten
    # =====================================================
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)
    colors = [
        "blue", "green", "red", "orange", "purple",
        "darkred", "darkblue", "darkgreen", "cadetblue", "pink"
    ]

    # =====================================================
    # PLZ-FLÄCHEN
    # =====================================================
    if mode == "PLZ-Flächen":

        try:
            with open("plz-5stellig.geojson", "r", encoding="utf-8") as f:
                geojson_data = json.load(f)
        except Exception as e:
            st.error(f"GeoJSON konnte nicht geladen werden: {e}")
            return

        st.subheader("📦 Liefergebiete (PLZ-Flächen)")

        for idx, block in enumerate(st.session_state["plz_blocks"]):
            col_plz, col_min, col_del = st.columns([3, 1.5, 1.5])

            with col_plz:
                block["plz"] = st.text_input(
                    f"PLZ-Gruppe {idx+1} (Komma getrennt)",
                    value=block["plz"],
                    key=f"plz_{idx}"
                )

            with col_min:
                block["min_order"] = st.number_input(
                    "Mindestbestellwert (€)",
                    min_value=0.0,
                    step=1.0,
                    value=block["min_order"],
                    key=f"min_{idx}"
                )

            with col_del:
                block["delivery_cost"] = st.number_input(
                    "Lieferkosten (€)",
                    min_value=0.0,
                    step=0.5,
                    value=block["delivery_cost"],
                    key=f"del_{idx}"
                )

        if len(st.session_state["plz_blocks"]) < 10:
            if st.button("➕ Eingabefeld hinzufügen"):
                st.session_state["plz_blocks"].append(
                    {"plz": "", "min_order": 0.0, "delivery_cost": 0.0}
                )

        all_coords = []
        download_rows = []

        for block in st.session_state["plz_blocks"]:
            if not block["plz"].strip():
                continue

            plz_list = [p.strip() for p in block["plz"].split(",") if p.strip()]

            for feature in geojson_data.get("features", []):
                props = feature.get("properties", {})
                plz_val = props.get("plz") or props.get("POSTCODE")

                if plz_val in plz_list:
                    geom = feature["geometry"]
                    coords = geom["coordinates"]

                    if geom["type"] == "Polygon":
                        for ring in coords:
                            all_coords.extend([[lat, lon] for lon, lat in ring])
                    elif geom["type"] == "MultiPolygon":
                        for poly in coords:
                            for ring in poly:
                                all_coords.extend([[lat, lon] for lon, lat in ring])

                    folium.GeoJson(
                        feature,
                        style_function=lambda x, c=colors[st.session_state["plz_blocks"].index(block) % len(colors)]: {
                            "fillColor": c,
                            "color": "black",
                            "weight": 1,
                            "fillOpacity": 0.3
                        },
                        tooltip=f"""
                        PLZ: {plz_val}<br>
                        Mindestbestellwert: {block['min_order']} €<br>
                        Lieferkosten: {block['delivery_cost']} €
                        """
                    ).add_to(m)

                    download_rows.append({
                        "PLZ": plz_val,
                        "Mindestbestellwert": block["min_order"],
                        "Lieferkosten": block["delivery_cost"]
                    })

        if all_coords:
            m.fit_bounds(all_coords)

        st_folium(m, width=700, height=500)

        if download_rows:
            df_download = pd.DataFrame(download_rows)
            csv = df_download.to_csv(index=False).encode("utf-8")

            st.download_button(
                "📥 PLZ-Liefergebiete herunterladen",
                csv,
                "plz_liefergebiete.csv",
                "text/csv"
            )

    # =====================================================
    # RADIEN
    # =====================================================
    else:
        CSV_URL = "https://raw.githubusercontent.com/Ascona89/Kalkulationen.py/main/plz_geocoord.csv"

        @st.cache_data
        def load_plz_data():
            df = pd.read_csv(CSV_URL, dtype=str)
            df["lat"] = df["lat"].astype(float)
            df["lon"] = df["lon"].astype(float)
            return df

        df_plz = load_plz_data()

        if not user_input.strip():
            return

        headers = {"User-Agent": "kalkulations-app/1.0"}
        try:
            response = requests.get(
                "https://photon.komoot.io/api/",
                params={"q": user_input, "limit": 1, "lang": "de"},
                headers=headers,
                timeout=10
            )
            data = response.json()
            lon_c, lat_c = data["features"][0]["geometry"]["coordinates"]
        except Exception:
            st.error("🌍 Geocoding fehlgeschlagen.")
            return

        radien_input = st.text_input("📏 Radien eingeben (km, Komma getrennt)", value="5,10")

        radien = [float(r.strip()) for r in radien_input.split(",") if r.strip()]

        folium.Marker([lat_c, lon_c], tooltip=user_input, icon=folium.Icon(color="red")).add_to(m)

        all_coords = [[lat_c, lon_c]]

        for i, r in enumerate(radien):
            folium.Circle(
                [lat_c, lon_c],
                radius=r * 1000,
                color=colors[i % len(colors)],
                fill=True,
                fill_opacity=0.2,
                tooltip=f"{r} km"
            ).add_to(m)

            all_coords.append([lat_c + r / 110.574, lon_c + r / 110.574])
            all_coords.append([lat_c - r / 110.574, lon_c - r / 110.574])

        m.fit_bounds(all_coords)
        st_folium(m, width=700, height=500)

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

        st.subheader("📋 PLZ im Radius")
        st.dataframe(df_result[["plz", "lat", "lon", "distance_km"]], use_container_width=True)

# =====================================================
# Conract Numbers
# =====================================================
def show_contractnumbers():
    import streamlit as st
    import pandas as pd

    st.header("📑 Contract Numbers")

    # =====================================================
    # Produkte inkl. Mindestpreise
    # =====================================================
    df_sw = pd.DataFrame({
        "Produkt": ["Shop", "App", "POS", "Pay", "Connect", "TSE"],
        "List_OTF": [999, 49, 999, 49, 0, 0],
        "Min_OTF":  [365, 15, 365, 35, 0, 0],
        "List_MRR": [119, 49, 89, 25, 13.72, 12],
        "Min_MRR":  [50, 15, 49, 5, 13.72, 12],
        "Typ": ["Software"] * 6
    })

    df_hw = pd.DataFrame({
        "Produkt": ["Ordermanager", "POS inkl 1 Printer", "Cash Drawer", "Extra Printer", "Additional Display", "PAX"],
        "List_OTF": [299, 1699, 149, 199, 100, 299],
        "Min_OTF":  [135, 350, 50, 99, 100, 225],
        "List_MRR": [0] * 6,
        "Min_MRR":  [0] * 6,
        "Typ": ["Hardware"] * 6
    })

    # =====================================================
    # Session State Mengen (aus Pricing übernehmen, falls noch nicht gesetzt)
    # =====================================================
    for i in range(len(df_sw)):
        if f"qty_sw_{i}" not in st.session_state:
            st.session_state[f"qty_sw_{i}"] = st.session_state.get(f"contract_sw_{i}", 0)
    for i in range(len(df_hw)):
        if f"qty_hw_{i}" not in st.session_state:
            st.session_state[f"qty_hw_{i}"] = st.session_state.get(f"contract_hw_{i}", 0)

    # =====================================================
    # Eingabe Gesamtpreise
    # =====================================================
    col1, col2 = st.columns(2)
    with col1:
        total_mrr = st.number_input("💶 Gesamt MRR (€)", min_value=0.0, step=50.0)
    with col2:
        total_otf = st.number_input("💶 Gesamt OTF (€)", min_value=0.0, step=100.0)

    # =====================================================
    # Zahlungsoption
    # =====================================================
    st.subheader("💳 Zahlungsoption (optional)")
    zahlung = st.selectbox(
        "Auswahl",
        [
            "Keine",
            "Gemischte Zahlung (25% + 12 Wochen) 10%",
            "Online-Umsatz (100%) 10%",
            "Monatliche Raten (12 Monate) 35%",
            "Online-Umsatz (25% + 12 Wochen) 15%"
        ]
    )

    prozent_map = {
        "Keine": 0,
        "Gemischte Zahlung (25% + 12 Wochen) 10%": 0.10,
        "Online-Umsatz (100%) 10%": 0.10,
        "Monatliche Raten (12 Monate) 35%": 0.35,
        "Online-Umsatz (25% + 12 Wochen) 15%": 0.15
    }

    prozent = prozent_map[zahlung]
    otf_adjusted = total_otf * (1 - prozent)

    st.caption(f"Verwendete OTF für Kalkulation: **{round(otf_adjusted)} €**")

    # =====================================================
    # Mengen Eingabe Software
    # =====================================================
    st.subheader("💻 Software")
    cols = st.columns(len(df_sw))
    for i, row in df_sw.iterrows():
        with cols[i]:
            st.session_state[f"qty_sw_{i}"] = st.number_input(
                row["Produkt"],
                min_value=0,
                step=1,
                value=st.session_state[f"qty_sw_{i}"]
            )

    # =====================================================
    # Mengen Eingabe Hardware
    # =====================================================
    st.subheader("🖨️ Hardware")
    cols = st.columns(len(df_hw))
    for i, row in df_hw.iterrows():
        with cols[i]:
            st.session_state[f"qty_hw_{i}"] = st.number_input(
                row["Produkt"],
                min_value=0,
                step=1,
                value=st.session_state[f"qty_hw_{i}"]
            )

    # =====================================================
    # Mengen übernehmen
    # =====================================================
    df_sw["Menge"] = [st.session_state[f"qty_sw_{i}"] for i in range(len(df_sw))]
    df_hw["Menge"] = [st.session_state[f"qty_hw_{i}"] for i in range(len(df_hw))]

    # =====================================================
    # Mindestbedarf berechnen
    # =====================================================
    min_otf_required = (
        (df_sw["Menge"] * df_sw["Min_OTF"]).sum() +
        (df_hw["Menge"] * df_hw["Min_OTF"]).sum()
    )

    min_mrr_required = (df_sw["Menge"] * df_sw["Min_MRR"]).sum()

    if total_otf < min_otf_required:
        st.warning(
            f"⚠️ OTF zu niedrig: {total_otf:,.0f} € "
            f"(Minimum: {min_otf_required:,.0f} €)"
        )

    if total_mrr < min_mrr_required:
        st.warning(
            f"⚠️ MRR zu niedrig: {total_mrr:,.2f} € "
            f"(Minimum: {min_mrr_required:,.2f} €)"
        )

    # =====================================================
    # OTF Verteilung (nie unter Mindestpreis)
    # =====================================================
    base_otf = (
        (df_sw["Menge"] * df_sw["List_OTF"]).sum() +
        (df_hw["Menge"] * df_hw["List_OTF"]).sum()
    )

    factor_otf = otf_adjusted / base_otf if base_otf > 0 else 0

    df_sw["OTF"] = (
        df_sw["Menge"] *
        (df_sw["List_OTF"] * factor_otf)
    ).clip(lower=df_sw["Min_OTF"]).round(0)

    df_hw["OTF"] = (
        df_hw["Menge"] *
        (df_hw["List_OTF"] * factor_otf)
    ).clip(lower=df_hw["Min_OTF"]).round(0)

    # =====================================================
    # MRR Verteilung (nie unter Mindestpreis)
    # =====================================================
    mrr_base = (df_sw["Menge"] * df_sw["List_MRR"]).sum()
    mrr_factor = total_mrr / mrr_base if mrr_base > 0 else 0

    df_sw["MRR_Monat"] = (
        df_sw["Menge"] *
        (df_sw["List_MRR"] * mrr_factor)
    ).clip(lower=df_sw["Min_MRR"]).round(2)

    df_sw["MRR_Woche"] = (df_sw["MRR_Monat"] / 4).round(2)

    df_hw["MRR_Monat"] = 0.0
    df_hw["MRR_Woche"] = 0.0

    # =====================================================
    # Ausgabe Software
    # =====================================================
    st.markdown("---")
    st.subheader("💻 Software")

    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    c1.write("Produkt")
    c2.write("OTF")
    c3.write("MRR")
    c4.write("WRR")

    for _, r in df_sw[df_sw["Menge"] > 0].iterrows():
        menge = int(r["Menge"])
        otf = int(r["OTF"])
        einzel_otf = int(otf / menge) if menge > 0 else 0

        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        name = f"{r['Produkt']} ({menge}x)" if menge > 1 else r["Produkt"]

        c1.write(f"**{name}**")
        c2.write(f"{otf} €")
        c3.write(f"{r['MRR_Monat']:.2f} €")
        c4.write(f"{r['MRR_Woche']:.2f} €")

    # =====================================================
    # Ausgabe Hardware
    # =====================================================
    st.markdown("---")
    st.subheader("🖨️ Hardware")

    c1, c2, _, _ = st.columns([3, 2, 2, 2])
    c1.write("Produkt")
    c2.write("OTF")

    for _, r in df_hw[df_hw["Menge"] > 0].iterrows():
        menge = int(r["Menge"])
        otf = int(r["OTF"])
        name = f"{menge}x {r['Produkt']}" if menge > 1 else r["Produkt"]

        c1, c2, _, _ = st.columns([3, 2, 2, 2])
        c1.write(f"**{name}**")
        c2.write(f"{otf} €")

    # =====================================================
    # Kontrollübersicht
    # =====================================================
    st.markdown("---")
    st.subheader("📊 Kontrollübersicht")
    st.write(f"OTF eingegeben: {total_otf:,.0f} €")
    st.write(f"OTF verwendet: {round(otf_adjusted):,.0f} €")
    st.write(f"MRR Monat: {total_mrr:,.2f} €")
    st.write(f"MRR Woche: {(total_mrr / 4):,.2f} €")


def show_pipeline():
    import streamlit as st
    import pandas as pd
    from datetime import date
    import folium
    from streamlit_folium import st_folium
    from geopy.geocoders import Nominatim
    import math

    # ======================================
    # Login-Passwörter pro Region
    # ======================================
    PIPELINE_PASSWORDS = ["south", "mids", "east", "north"]

    st.session_state.setdefault("pipeline_logged_in", False)
    st.session_state.setdefault("pipeline_region", None)
    st.session_state.setdefault("show_lead_form", False)
    st.session_state.setdefault("employees", {pw: 1 for pw in PIPELINE_PASSWORDS})

    # ======================================
    # Login
    # ======================================
    if not st.session_state.pipeline_logged_in:
        st.header("📈 Pipeline Login")
        pw = st.text_input("Passwort eingeben", type="password")
        if st.button("Login"):
            if pw in PIPELINE_PASSWORDS:
                st.session_state.pipeline_logged_in = True
                st.session_state.pipeline_region = pw
                st.rerun()
            else:
                st.error("❌ Falsches Passwort")
        return

    region = st.session_state.pipeline_region
    st.header(f"📈 Pipeline – Region {region.upper()}")

    # ======================================
    # Mitarbeiter Auswahl
    # ======================================
    st.subheader("👥 Mitarbeiter")
    ma_count = st.session_state.employees[region]
    ma_options = ["Alle anzeigen"] + [f"MA {i}" for i in range(1, ma_count + 1)]
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_ma = st.selectbox("Mitarbeiter auswählen", ma_options)
    with col2:
        if st.button("➕ MA hinzufügen"):
            st.session_state.employees[region] += 1
            st.rerun()

    # ======================================
    # Lead hinzufügen
    # ======================================
    st.markdown("---")
    if st.button("➕ Lead hinzufügen"):
        st.session_state.show_lead_form = True

    if st.session_state.show_lead_form:
        with st.form("lead_form"):
            st.subheader("🧾 Neuer Lead")
            last_contact = st.date_input("Last Contact", value=date.today())
            generated_by = st.selectbox("Generated by", ["WI", "TS", "Pay", "OMB"])
            am_nb = st.selectbox("AM / NB", ["AM", "NB"])
            name = st.text_input("Name")
            adresse = st.text_input("Adresse")
            ergebnis = st.selectbox("Ergebnis", ["Lost", "Hot", "Follow up booked", "Book follow up"])
            next_action = st.date_input("Next action", value=date.today())
            notes = st.text_area("Notes")

            assign_ma = st.selectbox(
                "Lead zuweisen an MA",
                [f"MA {i}" for i in range(1, ma_count + 1)],
                index=0
            )

            col_save, col_cancel = st.columns(2)
            submit = col_save.form_submit_button("💾 Speichern")
            cancel = col_cancel.form_submit_button("❌ Abbrechen")

        if cancel:
            st.session_state.show_lead_form = False
            st.rerun()

        if submit:
            # ======================================
            # Geocode Adresse
            # ======================================
            geolocator = Nominatim(user_agent="pipeline_app")
            lat, lon = None, None
            try:
                location = geolocator.geocode(adresse)
                if location:
                    lat, lon = location.latitude, location.longitude
            except:
                st.warning("⚠️ Adresse konnte nicht geocodet werden. Karte kann ungenau sein.")

            # ======================================
            # Insert in Supabase
            # ======================================
            supabase.table("pipeline_leads").insert({
                "region": region,
                "employee": int(assign_ma.split()[1]),
                "last_contact": last_contact.isoformat(),
                "generated_by": generated_by,
                "am_nb": am_nb,
                "name": name,
                "adresse": adresse,
                "ergebnis": ergebnis,
                "next_action": next_action.isoformat(),
                "notes": notes,
                "lat": lat,
                "lon": lon
            }).execute()
            st.success("✅ Lead gespeichert")
            st.session_state.show_lead_form = False
            st.rerun()

    # ======================================
    # Leads Tabelle
    # ======================================
    st.markdown("---")
    st.subheader("📋 Leads")
    query = supabase.table("pipeline_leads").select("*").eq("region", region)
    if selected_ma != "Alle anzeigen":
        query = query.eq("employee", int(selected_ma.split()[1]))
    data = query.order("created_at", desc=True).execute()
    df = pd.DataFrame(data.data)

    if df.empty:
        st.info("Noch keine Leads vorhanden.")
        m = folium.Map(location=[51.1657,10.4515], zoom_start=6)
        st_folium(m, width=700, height=500)
        return

    for col in ["lat","lon"]:
        if col not in df.columns:
            df[col] = None

    st.dataframe(df[['last_contact','generated_by','am_nb','name','adresse','ergebnis','next_action','notes']], use_container_width=True)

    # ======================================
    # Karte erstellen
    # ======================================
    st.markdown("---")
    st.subheader("🗺️ Leads Karte (Status-Farben)")

    def get_marker_color(status):
        if status.lower() == "hot":
            return "green"
        elif status.lower() in ["follow up booked", "book follow up"]:
            return "orange"
        elif status.lower() == "lost":
            return "red"
        else:
            return "blue"

    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)
    lead_coords = df.dropna(subset=["lat","lon"])
    for _, r in lead_coords.iterrows():
        folium.Marker(
            [r['lat'], r['lon']],
            tooltip=f"{r['name']} ({r['ergebnis']})",
            icon=folium.Icon(color=get_marker_color(r["ergebnis"]))
        ).add_to(m)

    # ======================================
    # Radius Filter
    # ======================================
    st.subheader("🔎 Radius Filter")
    search_address = st.text_input("Adresse oder PLZ")
    search_radius = st.number_input("Radius (km)", min_value=0.0, value=5.0, step=1.0)

    if search_address.strip():
        geolocator = Nominatim(user_agent="pipeline_app")
        loc = geolocator.geocode(search_address)
        if loc:
            search_lat, search_lon = loc.latitude, loc.longitude
            folium.Circle(
                [search_lat, search_lon],
                radius=search_radius*1000,
                color='blue',
                fill=True,
                fill_opacity=0.2,
                tooltip=f"{search_radius} km Radius"
            ).add_to(m)

            # Filter Leads innerhalb Radius
            filtered = []
            R = 6371
            for _, r in lead_coords.iterrows():
                dlat = math.radians(r['lat']-search_lat)
                dlon = math.radians(r['lon']-search_lon)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(search_lat))*math.cos(math.radians(r['lat']))*math.sin(dlon/2)**2
                c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R*c
                if distance <= search_radius:
                    filtered.append(r)

            # Neue Karte für Filter Leads
            m = folium.Map(location=[search_lat, search_lon], zoom_start=10)
            folium.Circle([search_lat, search_lon], radius=search_radius*1000,
                          color='blue', fill=True, fill_opacity=0.2).add_to(m)
            for r in filtered:
                folium.Marker(
                    [r['lat'], r['lon']],
                    tooltip=f"{r['name']} ({r['ergebnis']})",
                    icon=folium.Icon(color=get_marker_color(r["ergebnis"]))
                ).add_to(m)

    st_folium(m, width=700, height=500)

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
elif page == "Pipeline":
    show_pipeline()

