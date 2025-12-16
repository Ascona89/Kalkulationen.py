import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# =========================================================
# 🔐 Passwörter
# =========================================================
USER_PASSWORD = "welovekb"
ADMIN_PASSWORD = "sebaforceo"

# =========================================================
# 🧠 Supabase
# =========================================================
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

# =========================================================
# 🧠 Session State
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "USER_PASSWORD" not in st.session_state:
    st.session_state["USER_PASSWORD"] = USER_PASSWORD

# =========================================================
# 🔐 Login
# =========================================================
def login(password):
    if password == st.session_state["USER_PASSWORD"]:
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

# =========================================================
# 🔧 App Config
# =========================================================
st.set_page_config(page_title="Kalkulations-App", layout="wide")
st.title("📊 Kalkulations-App")

# =========================================================
# 📋 Navigation
# =========================================================
page = st.sidebar.radio(
    "Wähle eine Kalkulation:",
    ["Platform", "Cardpayment", "Pricing", "Contract Numbers"]
)

# =========================================================
# 🏁 PLATFORM
# =========================================================
if page == "Platform":
    st.header("🏁 Platform Kalkulation")

    revenue = st.number_input("Revenue (€)", step=250.0)
    commission = st.number_input("Commission (%)", value=14.0)
    aov = st.number_input("Average Order Value (€)", value=25.0)
    service_fee = st.number_input("Service Fee (€)", value=0.69)

    cost = revenue * commission / 100 + (0.7 * revenue / aov if aov else 0) * service_fee
    st.markdown(f"### 💶 Cost on Platform: **{cost:,.2f} €**")

# =========================================================
# 💳 CARDPAYMENT
# =========================================================
elif page == "Cardpayment":
    st.header("💳 Cardpayment Vergleich")

    revenue = st.number_input("Revenue (€)", step=250.0)
    commission = st.number_input("Commission (%)", value=1.39)
    monthly_fee = st.number_input("Monthly Fee (€)", value=0.0)

    total = revenue * commission / 100 + monthly_fee
    st.markdown(f"### 💳 Total: **{total:,.2f} €**")

# =========================================================
# 💰 PRICING (Single Source of Truth)
# =========================================================
elif page == "Pricing":
    st.header("💰 Pricing")

    software_data = {
        "Produkt": ["Web", "App", "Kasse"],
        "List_MRR (€)": [79.0, 129.0, 69.0],
        "List_OTF (€)": [999.0, 49.0, 999.0]
    }

    df_sw = pd.DataFrame(software_data)

    for i in range(len(df_sw)):
        if f"sw_{i}" not in st.session_state:
            st.session_state[f"sw_{i}"] = 0

    st.subheader("🧩 Software Auswahl")
    for i, row in df_sw.iterrows():
        st.number_input(
            f"{row['Produkt']} Menge",
            min_value=0,
            step=1,
            key=f"sw_{i}"
        )

    df_sw["Menge"] = [st.session_state[f"sw_{i}"] for i in range(len(df_sw))]
    st.dataframe(df_sw, use_container_width=True, hide_index=True)

# =========================================================
# 📑 CONTRACT NUMBERS
# =========================================================
elif page == "Contract Numbers":
    st.header("📑 Contract Numbers")

    # 🔗 Preise & Auswahl aus Pricing
    pricing_products = [
        {"name": "Web",   "price": 79.0,  "qty": st.session_state.get("sw_0", 0)},
        {"name": "App",   "price": 129.0, "qty": st.session_state.get("sw_1", 0)},
        {"name": "Kasse", "price": 69.0,  "qty": st.session_state.get("sw_2", 0)},
    ]

    active_products = [p for p in pricing_products if p["qty"] > 0]

    if not active_products:
        st.warning("⚠️ Bitte zuerst Produkte im Pricing auswählen.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        package_mrr = st.number_input(
            "Paket MRR gesamt (€)",
            min_value=0.0,
            step=1.0
        )
    with col2:
        package_otf = st.number_input(
            "Paket OTF gesamt (€)",
            min_value=0.0,
            step=10.0
        )

    total_original = sum(p["price"] for p in active_products)

    rows = []
    for p in active_products:
        pct = p["price"] / total_original if total_original else 0
        rows.append({
            "Produkt": p["name"],
            "Originalpreis (€)": f"{p['price']:,.2f}",
            "%-Anteil": f"{pct*100:,.2f} %",
            "MRR Vertrag (€)": f"{pct*package_mrr:,.2f}",
            "OTF Vertrag (€)": f"{pct*package_otf:,.2f}"
        })

    df_contract = pd.DataFrame(rows)

    st.subheader("📄 Vertragswerte (direkt eintragen)")
    st.dataframe(df_contract, use_container_width=True, hide_index=True)

    st.markdown(
        f"**Prüfsumme:** 100 % | "
        f"**MRR gesamt:** {package_mrr:,.2f} € | "
        f"**OTF gesamt:** {package_otf:,.2f} €"
    )

# =========================================================
# Footer
# =========================================================
st.markdown("""
<hr>
<p style='text-align:center; font-size:0.8rem; color:gray;'>
😉 Traue niemals Zahlen, die du nicht selbst gefälscht hast 😉
</p>
""", unsafe_allow_html=True)
