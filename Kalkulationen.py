import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

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
    st.markdown("<h1 style='text-align:center;'>🔐 Login erforderlich</h1>", unsafe_allow_html=True)
    pw = st.text_input("Passwort", type="password")
    if st.button("Login"):
        login(pw)
    st.stop()

# =====================================================
# 👑 Admin Backend
# =====================================================
if st.session_state.is_admin:
    st.markdown("<h1 style='text-align:center;'>👑 Admin Dashboard</h1>", unsafe_allow_html=True)
    tab_data, tab_password = st.tabs(["Login-Historie", "User Passwort ändern"])

    with tab_data:
        data = supabase.table("login_events").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(data.data)
        if not df.empty:
            df["Datum"] = pd.to_datetime(df["created_at"]).dt.date
            st.subheader("📄 Login-Historie")
            st.dataframe(df, use_container_width=True)
            st.subheader("📊 Logins pro Tag")
            logins_per_day = df[df["success"]==True].groupby("Datum").size().reset_index(name="Logins")
            st.bar_chart(logins_per_day.set_index("Datum"))
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("CSV Export", csv, "login_history.csv", "text/csv")
        else:
            st.info("Noch keine Login-Daten vorhanden.")

    with tab_password:
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
st.markdown("<h1 style='text-align:center;'>📊 Kalkulations-App</h1>", unsafe_allow_html=True)

# 🗂 Seitenauswahl (Sidebar)
page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Radien"]
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
# 🏁 Platform – Modern & Dashboard Style
# =====================================================
if page == "Platform":
    st.header("🏁 Platform Kalkulation")
    tab_inputs, tab_results = st.tabs(["Eingaben", "Ergebnisse"])

    with tab_inputs:
        with st.expander("💻 Plattform-Eingaben", expanded=True):
            col1, col2 = st.columns([2,1.5])
            with col1:
                revenue = persistent_number_input("Revenue on platform (€)", "revenue", 0.0, step=250.0)
                commission_pct = persistent_number_input("Commission (%)", "commission_pct", 14.0, step=1.0)
                avg_order_value = persistent_number_input("Average order value (€)", "avg_order_value", 25.0, step=5.0)
                service_fee = persistent_number_input("Service Fee (€)", "service_fee", 0.69, step=0.1)
            with col2:
                st.subheader("Vertragsdetails")
                OTF = persistent_number_input("One Time Fee (OTF) (€)", "OTF", 0.0, step=100.0)
                MRR = persistent_number_input("Monthly Recurring Revenue (MRR) (€)", "MRR", 0.0, step=10.0)
                contract_length = persistent_number_input("Contract length (Monate)", "contract_length", 24, step=12)

    with tab_results:
        total_cost = revenue*(commission_pct/100) + \
                     (0.7*revenue/avg_order_value if avg_order_value else 0)*service_fee
        transaction = 0.7*revenue/5*0.35
        cost_monthly = MRR + transaction
        saving_monthly = total_cost - cost_monthly
        saving_over_contract = saving_monthly*contract_length

        st.subheader("📊 Kennzahlen")
        col1, col2, col3 = st.columns(3)
        col1.metric(label="💶 Cost monthly", value=f"{cost_monthly:,.2f} €", delta_color="inverse")
        col2.metric(label="💰 Saving monthly", value=f"{saving_monthly:,.2f} €", delta=f"{saving_over_contract:,.2f} € über {contract_length} Monate")
        col3.markdown(f"""
        <div style='background-color:#f0f8ff; padding:15px; border-radius:12px; text-align:center; box-shadow:2px 2px 8px rgba(0,0,0,0.1);'>
            <h3 style='color:red;'>Total Cost on Platform</h3>
            <p style='font-size:28px;'>{total_cost:,.2f} €</p>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# 💳 Cardpayment – Dashboard Style
# =====================================================
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")
    tab_inputs, tab_results = st.tabs(["Eingaben", "Ergebnisse"])

    with tab_inputs:
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

    with tab_results:
        total_actual = rev_a*(comm_a/100) + sum_a*auth_a + mrr_a
        total_offer  = rev_o*(comm_o/100) + sum_o*auth_o + mrr_o
        saving = total_offer - total_actual

        col1, col2, col3 = st.columns(3)
        col1.metric("💳 Total Actual", f"{total_actual:,.2f} €")
        col2.metric("💳 Total Offer", f"{total_offer:,.2f} €")
        col3.metric("💰 Ersparnis (Offer - Actual)", f"{saving:,.2f} €")

# =====================================================
# 💰 Pricing – Dashboard Style
# =====================================================
elif page == "Pricing":
    st.header("💰 Pricing Kalkulation")
    tab_inputs, tab_results = st.tabs(["Eingaben", "Ergebnisse"])

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

    with tab_inputs:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Software")
            for i, p in enumerate(df_sw["Produkt"]):
                st.session_state[f"sw_{i}"] = st.number_input(p, min_value=0, step=1, key=f"sw_ui_{i}")
        with col2:
            st.subheader("Hardware")
            for i, p in enumerate(df_hw["Produkt"]):
                st.session_state[f"hw_{i}"] = st.number_input(p, min_value=0, step=1, key=f"hw_ui_{i}")

    with tab_results:
        df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
        df_hw["Menge"] = [st.session_state[f"hw_{i}"] for i in range(len(df_hw))]

        list_otf = (df_sw["Menge"]*df_sw["List_OTF"]).sum() + (df_hw["Menge"]*df_hw["List_OTF"]).sum()
        min_otf = (df_sw["Menge"]*df_sw["Min_OTF"]).sum() + (df_hw["Menge"]*df_hw["Min_OTF"]).sum()
        list_mrr = (df_sw["Menge"]*df_sw["List_MRR"]).sum()
        min_mrr = (df_sw["Menge"]*df_sw["Min_MRR"]).sum()

        col1, col2 = st.columns(2)
        col1.metric("🧾 OTF LIST gesamt", f"{list_otf:,.2f} €")
        col2.metric("🧾 MRR LIST gesamt", f"{list_mrr:,.2f} €")

# =====================================================
# 🗺️ Radien – Dashboard Style
# =====================================================
elif page == "Radien":
    import folium
    from geopy.geocoders import Nominatim
    from streamlit_folium import st_folium

    st.header("🗺️ Radien um eine Adresse")
    tab_inputs, tab_map = st.tabs(["Eingaben", "Karte"])

    with tab_inputs:
        adresse = persistent_text_input("Adresse eingeben", "adresse")
        radien_input = persistent_text_input("Radien eingeben (km, durch Komma getrennt)", "radien_input", "5,10")
        if st.button("Karte anzeigen"):
            st.session_state['show_map'] = True

    with tab_map:
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
                            folium.Marker([lat, lon], popup=adresse, tooltip="Zentrum", icon=folium.Icon(color="red")).add_to(m)
                            bounds = []
                            for r in radien:
                                folium.Circle([lat, lon], radius=r*1000, color="blue", weight=2, fill=True, fill_opacity=0.15).add_to(m)
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
# Footer – Modern
# =====================================================
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
