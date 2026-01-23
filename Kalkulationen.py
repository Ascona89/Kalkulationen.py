import streamlit as st
import pandas as pd
import math
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

st.set_page_config(page_title="Telesales", layout="wide")
st.title("📞 Telesales – PLZ Radius Finder (Live)")

geolocator = Nominatim(user_agent="telesales-app")

# =====================================================
# EINGABEN
# =====================================================
col1, col2 = st.columns(2)

with col1:
    center_input = st.text_input("📍 Stadt oder PLZ", placeholder="z.B. Berlin oder 10115")

with col2:
    radius_km = st.number_input("📏 Radius in km", min_value=1, max_value=300, value=25)

# =====================================================
# PLZ-SUCHE
# =====================================================
if st.button("🔍 PLZ berechnen"):

    if not center_input:
        st.warning("Bitte Stadt oder PLZ eingeben.")
        st.stop()

    center = geolocator.geocode(center_input + ", Deutschland")

    if not center:
        st.error("Ort oder PLZ nicht gefunden.")
        st.stop()

    lat_c, lon_c = center.latitude, center.longitude

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    results = []

    # Suche umliegende PLZ über Nominatim
    for zoom in range(10, 14):
        places = geolocator.reverse(
            (lat_c, lon_c),
            zoom=zoom,
            exactly_one=False,
            addressdetails=True
        )

        if not places:
            continue

        for p in places:
            addr = p.raw.get("address", {})
            plz = addr.get("postcode")
            ort = addr.get("city") or addr.get("town") or addr.get("village")

            if plz:
                dist = haversine(lat_c, lon_c, p.latitude, p.longitude)
                if dist <= radius_km:
                    results.append({
                        "plz": plz,
                        "ort": ort or "",
                        "lat": p.latitude,
                        "lon": p.longitude,
                        "distance_km": round(dist, 2)
                    })

    if not results:
        st.warning("Keine PLZ im Radius gefunden.")
        st.stop()

    df = pd.DataFrame(results).drop_duplicates("plz").sort_values("distance_km")

    st.success(f"✅ {len(df)} PLZ im Umkreis von {radius_km} km")

    st.dataframe(df[["plz", "ort", "distance_km"]], use_container_width=True)

    # =====================================================
    # KARTE
    # =====================================================
    m = folium.Map(location=[lat_c, lon_c], zoom_start=9)

    folium.Marker(
        [lat_c, lon_c],
        popup="Zentrum",
        icon=folium.Icon(color="red")
    ).add_to(m)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            fill=True,
            popup=f"{row['plz']} {row['ort']} ({row['distance_km']} km)"
        ).add_to(m)

    st_folium(m, width=1200, height=600)
