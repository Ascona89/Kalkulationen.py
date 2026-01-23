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
    # (Der gesamte Platform-Code bleibt unverändert)
    pass

# =====================================================
# 💳 Cardpayment
# =====================================================
elif page == "Cardpayment":
    # (Der gesamte Cardpayment-Code bleibt unverändert)
    pass

# =====================================================
# 💰 Pricing
# =====================================================
elif page == "Pricing":
    # (Der gesamte Pricing-Code bleibt unverändert)
    pass

# =====================================================
# 🗺️ Radien
# =====================================================
elif page == "Radien":
    # (Der gesamte Radien-Code bleibt unverändert)
    pass

# =====================================================
# =================== TELESSALES ======================
# =====================================================
elif page == "Telesales":
    st.header("📞 Telesales – PLZ im Radius")

    CSV_FILE = "plz_geocoord.csv"  # <- lokale Datei im Repo/Ordner

    @st.cache_data
    def load_plz_data():
        df = pd.read_csv(CSV_FILE, dtype=str)
        df = df.rename(columns={
            "plz": "plz",
            "lat": "lat",
            "lon": "lon"
        })
        df["lat"] = df["lat"].astype(float)
        df["lon"] = df["lon"].astype(float)
        return df

    df_plz = load_plz_data()

    # ---------------- Session State ----------------
    st.session_state.setdefault("show_result", False)
    st.session_state.setdefault("df_result", None)
    st.session_state.setdefault("center", None)

    # ---------------- Inputs ----------------
    col1, col2 = st.columns(2)
    with col1:
        center_input = st.text_input("📍 Stadt oder PLZ", placeholder="z.B. Berlin oder 10115")
    with col2:
        radius_km = st.number_input("📏 Radius (km)", min_value=1, max_value=300, value=25)

    # ---------------- Button ----------------
    if st.button("🔍 PLZ berechnen"):
        geolocator = Nominatim(user_agent="telesales-app")
        center = geolocator.geocode(center_input + ", Deutschland")
        if not center:
            st.error("Ort oder PLZ nicht gefunden.")
            st.stop()

        lat_c, lon_c = center.latitude, center.longitude

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

        df_result = df_plz[df_plz["distance_km"] <= radius_km].sort_values("distance_km")
        st.session_state["df_result"] = df_result
        st.session_state["center"] = (lat_c, lon_c)
        st.session_state["show_result"] = True

    # ---------------- RESULTS (persisted) ----------------
    if st.session_state["show_result"] and st.session_state["df_result"] is not None:
        df_result = st.session_state["df_result"]
        lat_c, lon_c = st.session_state["center"]

        st.success(f"✅ {len(df_result)} PLZ im Umkreis")
        st.dataframe(
            df_result[["plz", "distance_km"]].round(2),
            use_container_width=True
        )

        # ---------------- MAP ----------------
        m = folium.Map(location=[lat_c, lon_c], zoom_start=9)
        folium.Marker(
            [lat_c, lon_c],
            popup="Zentrum",
            icon=folium.Icon(color="red")
        ).add_to(m)
        for _, row in df_result.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=4,
                fill=True,
                fill_opacity=0.6,
                popup=f"{row['plz']}"
            ).add_to(m)
        st_folium(m, width=1200, height=600)

# =====================================================
# Footer
# =====================================================
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
