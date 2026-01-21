elif page == "Radien":
    import folium
    from geopy.geocoders import Nominatim
    from streamlit_folium import st_folium

    st.header("🗺️ Radien um eine Adresse")

    # --- Eingaben ---
    adresse = st.text_input("Adresse eingeben", key="adresse")
    radien = st.multiselect(
        "Radien auswählen (km)",
        [1,3,5,10,15,20,25,50],
        default=[5,10],
        key="radien"
    )

    if st.button("Karte anzeigen"):
        st.session_state['show_map'] = True

    # --- Karte anzeigen, falls Button geklickt ---
    if st.session_state.get('show_map', False):
        if adresse.strip() and radien:
            geolocator = Nominatim(user_agent="streamlit-single-address-radius", timeout=10)
            try:
                location = geolocator.geocode(adresse)
                if location:
                    lat, lon = location.latitude, location.longitude

                    m = folium.Map(location=[lat, lon], zoom_start=12)

                    # Mittelpunkt Marker
                    folium.Marker(
                        [lat, lon],
                        popup=adresse,
                        tooltip="Zentrum",
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(m)

                    # Kreise für jeden Radius & Auto-Zoom
                    bounds = []
                    for r in radien:
                        circle = folium.Circle(
                            location=[lat, lon],
                            radius=r*1000,
                            color="blue",
                            weight=2,
                            fill=True,
                            fill_opacity=0.15
                        ).add_to(m)

                        # Eckpunkte für Auto-Zoom
                        bounds.append([lat + r/111, lon + r/111])
                        bounds.append([lat - r/111, lon - r/111])

                    m.fit_bounds(bounds)  # Auto-Zoom

                    st_folium(m, width=1000, height=600)
                else:
                    st.warning("Adresse nicht gefunden.")
            except Exception as e:
                st.error(f"Fehler bei Geocoding: {e}\nVersuche es in ein paar Sekunden erneut.")
        else:
            st.warning("Bitte Adresse eingeben und mindestens einen Radius auswählen.")
