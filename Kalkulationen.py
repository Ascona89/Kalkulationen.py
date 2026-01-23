import streamlit as st
import pandas as pd
import math
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

st.set_page_config(page_title="Telesales", layout="wide")

st.title("📞 Telesales – PLZ Radius Analyse")

# =========================================================
# PLZ-DATEN (ALLE DEUTSCHEN PLZ) – DIREKT VON GITHUB
# =========================================================
CSV_URL = "https://raw.githubusercontent.com/WZBSocialScienceCenter/plz_geocoord/master/plz_geocoord.csv"

@st.cache_data
def load_plz_data():
    df = pd.read_csv(CSV_URL, dtype=str)

    # Spalten prüfen & normieren
    required_mapping = {
        "plz": ["plz", "postal_code"],
        "lat": ["lat", "latitude"],
        "lon": ["lon", "longitude"],
        "ort": ["ort", "place_name", "city"]
    }

    normalized = {}

    for target, candidates in required_mapping.items():
        for c in candidates:
            if c in df.columns:
                normalized[target] = c
                break

    missing = [k for k in ["plz", "lat", "lon"] if k not in normalized]
    if missing:
        st.error(f"❌ Fehlende Spalten in CSV: {missing}")
        st.error(f"Gefundene Spalten: {df.columns.tolist()}")
        st.stop()

    df = df.rename(columns={
        normalized["plz"]: "plz",
        normalized["lat"]: "lat",
        normalized["lon"]: "lon"
    })

    if "ort" in normalized:
        df = df.rename(columns={normalized["ort"]: "ort"})
    else:
        df["ort"] = ""

    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)

    return df


df_plz = load_plz_data()

# =========================================================
# EINGABEN
# =========================================================
col1, col2 = st.columns(2)

with col1:
    center_input = st.text_input("📍 Stadt oder PLZ", placeholder="z.B. Berlin oder 10115")

with col2:
    radius_km = st.number_input("📏 Radius in km", min_value=1, max_value=500, value=25)

# =========================================================
# BERECHNUNG
# =========================================================
if st.button("🔍 PLZ berechnen"):

    if not center_input:
        st.warning("Bitte Stadt oder PLZ eingeben.")
        st.stop()

    geolocator = Nominatim(user_agent="telesales-plz-app")
    location = geolocator.geocode(center_input)

    if not location:
        st.error("Adresse oder PLZ nicht gefunden.")
        st.stop()

    lat_c, lon_c = location.latitude, location.longitude

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # VEKTORISIERT → SCHNELL & STABIL
    df_plz["distance_km"] = haversine(
        lat_c,
        lon_c,
        df_plz["lat"],
        df_plz["lon"]
    )

    df_result = df_plz[df_plz["distance_km"] <= radius_km].sort_values("distance_km")

    st.success(f"✅ {len(df_result)} PLZs im Umkreis von {radius_km} km")

    st.dataframe(
        df_result[["plz", "ort", "distance_km"]]
        .round(2)
        .reset_index(drop=True),
        use_container_width=True
    )

    # =========================================================
    # KARTE
    # =========================================================
    m = folium.Map(location=[lat_c, lon_c], zoom_start=9)

    folium.Marker(
        [lat_c, lon_c],
        popup="Zentrum",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

    for _, row in df_result.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=f"{row['plz']} {row['ort']}"
        ).add_to(m)

    st_folium(m, width=1200, height=600)
