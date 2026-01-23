import streamlit as st
import pandas as pd
import math
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# =====================================================
# Page Setup
# =====================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

# =====================================================
# Sidebar Navigation
# =====================================================
page = st.sidebar.radio(
    "Wähle eine Seite:",
    ["Platform", "Cardpayment", "Pricing", "Radien", "Telesales"]
)

# =====================================================
# =================== TELESSALES ======================
# =====================================================
if page == "Telesales":

    st.header("📞 Telesales – PLZ im Radius")

    CSV_URL = "https://raw.githubusercontent.com/openplzapi/openplzapi-data/main/DE/plz.csv"

    @st.cache_data
    def load_plz_data():
        df = pd.read_csv(CSV_URL, dtype=str)

        df = df.rename(columns={
            "postcode": "plz",
            "place": "ort",
            "latitude": "lat",
            "longitude": "lon"
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
            df_result[["plz", "ort", "distance_km"]].round(2),
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
                popup=f"{row['plz']} {row['ort']}"
            ).add_to(m)

        st_folium(m, width=1200, height=600)

# =====================================================
# =================== FOOTER ==========================
# =====================================================
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
