import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import math

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

# 🗂 Seitenauswahl (Sidebar)
page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Radien", "Telesales"]
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
    # (Der bestehende Pricing-Code unverändert)
    st.info("Pricing-Seite hier einfügen")

# =====================================================
# 🗺️ Radien
# =====================================================
elif page == "Radien":
    st.info("Radien-Seite hier einfügen (bestehender Code)")

# =====================================================
# 📞 Telesales (neu)
# =====================================================
elif page == "Telesales":
    st.header("📞 Telesales PLZ Suche")

    # --- GitHub CSV mit allen PLZ in Deutschland ---
    CSV_URL = "https://raw.githubusercontent.com/WZBSocialScienceCenter/plz_geocoord/master/plz_geocoord.csv"

    @st.cache_data
    def load_plz_data():
        df = pd.read_csv(CSV_URL, dtype={"plz": str})
        # Spalten anpassen
        if "latitude" in df.columns and "longitude" in df.columns:
            df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
        return df

    df_plz = load_plz_data()

    center_input = persistent_text_input("Stadt oder PLZ eingeben", "telesales_center")
    radius_input = persistent_number_input("Radius (km)", "telesales_radius", 5.0, step=1.0)

    if st.button("PLZs anzeigen"):
        if center_input.strip():
            geolocator = Nominatim(user_agent="telesales-plz-map", timeout=10)
            location = geolocator.geocode(center_input)
            if location:
                lat_c, lon_c = location.latitude, location.longitude

                # Haversine-Funktion
                def haversine(lat1, lon1, lat2, lon2):
                    R = 6371
                    phi1, phi2 = math.radians(lat1), math.radians(lat2)
                    dphi = math.radians(lat2-lat1)
                    dlambda = math.radians(lon2-lon1)
                    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
                    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
                    return R * c

                df_plz["distance_km"] = df_plz.apply(lambda row: haversine(lat_c, lon_c, row["lat"], row["lon"]), axis=1)
                df_result = df_plz[df_plz["distance_km"] <= radius_input].sort_values("distance_km")

                st.success(f"{len(df_result)} PLZs innerhalb von {radius_input} km gefunden:")
                st.dataframe(df_result[["plz", "ort", "distance_km"]].reset_index(drop=True))

                # Karte
                m = folium.Map(location=[lat_c, lon_c], zoom_start=10)
                folium.Marker([lat_c, lon_c], popup="Zentrum", icon=folium.Icon(color="red")).add_to(m)
                for _, row in df_result.iterrows():
                    folium.CircleMarker(
                        location=[row["lat"], row["lon"]],
                        radius=5,
                        color="blue",
                        fill=True,
                        fill_opacity=0.6,
                        popup=f"{row['plz']} {row['ort']}"
                    ).add_to(m)
                st_folium(m, width=1000, height=600)
            else:
                st.warning("Adresse oder PLZ nicht gefunden.")
        else:
            st.warning("Bitte Stadt oder PLZ eingeben.")

# =====================================================
# Footer
# =====================================================
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
