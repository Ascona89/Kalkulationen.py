            accessory_otf_shares = {
                name: accessory_pool * qty / total_accessory_qty
                for name, qty in selected_accessories.items()
            }
        elif pos_qty > 0:
            pos_otf_share = pos_otf_total * 0.50
            sunmi_otf_share = pos_otf_total * 0.50
        else:
            pos_otf_share = pos_otf_total

        # Kiosk-OTF: 25 % für die Einrichtungsgebühr, maximal 500 €;
        # der Rest wird gleichmäßig auf die ausgewählte Gerätemenge verteilt.
        kiosk_qty = hardware_qty.get("Kiosk", 0)
        kiosk_otf_total = otf_values.get("Kiosk", 0.0)
        kiosk_setup_fee = min(kiosk_otf_total * 0.25, 500.0) if kiosk_otf_total > 0 else 0.0
        kiosk_device_pool = max(0.0, kiosk_otf_total - kiosk_setup_fee)

        # Die Zeilen bleiben nach Produkt gruppiert: Subscription direkt vor OTF.
        output_order = list(percentages.keys())
        for extra_product in ("POS", "Kiosk"):
            if extra_product in percentages and extra_product not in output_order:
                output_order.append(extra_product)

        for product in output_order:
            subscription_label, otf_label = product_line_items[product]
            if product in mrr_values:
                add_row(subscription_label, mrr_values[product] / 4.0, weekly=True)
            if otf_label and product in otf_values:
                if product == "POS":
                    add_row("POS OTF", pos_otf_share)
                    if pos_qty > 0:
                        add_row("SunMi D3 Pro", sunmi_otf_share / pos_qty)
                    for accessory, allocated_total in accessory_otf_shares.items():
                        qty = hardware_qty.get(accessory, 0)
                        add_row(accessory, allocated_total / qty if qty else allocated_total)
                elif product == "Kiosk":
                    if "Kiosk" in selected_sw or kiosk_qty > 0:
                        add_row("YOYOKiosk Setup Fee", kiosk_setup_fee)
                        if kiosk_qty > 0:
                            add_row(f"Kiosk {kiosk_variant}", kiosk_device_pool / kiosk_qty)
                        elif kiosk_device_pool > 0:
                            add_row(f"Kiosk {kiosk_variant}", kiosk_device_pool)
                else:
                    add_row(otf_label, otf_values[product])
    else:
        st.info(
            "Für diese Produktauswahl ist in der Tabelle keine Prozentverteilung hinterlegt. "
            "Bitte prüfe die ausgewählten Softwareprodukte und – bei Shop allein oder Shop + App – den Ordermanager."
        )

    # TSE, Loyalty und Connect werden ebenfalls durch 4 geteilt und wöchentlich ausgewiesen.
    if has_pos or has_tse:
        add_row("POS TSE Fee", 12.0 / 4.0, weekly=True)
    if has_loyalty:
        add_row("Loyalty", 15.0 / 4.0, weekly=True)
    if has_connect:
        add_row("Connect", 15.0 / 4.0, weekly=True)

    # Hardware-Mengen ohne doppelte Preiszeilen aus der OTF-Aufteilung.
    hardware_line_items = {
        "Ordermanager": "Order Manager Hardware",
        "PAX": "PAX A920 Pro",
    }
    for product, line_item in hardware_line_items.items():
        qty = hardware_qty.get(product, 0)
        if qty > 0:
            add_row(f"{line_item} (Menge {qty})", None)

    # Falls keine passende Software-Kombination gewählt wurde, die Hardware
    # trotzdem als Auswahl anzeigen; andernfalls sind die Preise oben verteilt.
    if not percentages:
        fallback_hardware = {
            "POS inkl 1 Printer": "SunMi D3 Pro",
            "Extra Printer": "Extra Printer",
            "Additional Display": "Additional Display",
            "Cash Drawer": "Cash Drawer",
            "Kiosk": f"Kiosk {kiosk_variant}",
        }
        for product, line_item in fallback_hardware.items():
            qty = hardware_qty.get(product, 0)
            if qty > 0:
                add_row(f"{line_item} (Menge {qty})", None)

    # Google Adwords nur anzeigen, wenn dafür ein Betrag ausgewählt wurde.
    # Die Laufzeit in Wochen ergibt sich aus der ausgewählten Monatsanzahl × 4.
    if google_ads_monthly > 0:
        add_row("Google Adwords", google_ads_monthly / 4.0, weekly=True, period=str(google_ads_months * 4))

    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    else:
        st.caption("Wähle Produkte aus, um die Ergebnisse hier als Tabelle zu sehen.")# =====================================================
# 🏪 Restaurants
# =====================================================
def show_restaurants():
    st.header(" Restaurants")
    st.info("Only available for MIDS/ wrong Permission.")
# =====================================================
# ⚡ Seite auswählen
# =====================================================
if page == "Platform":
    show_platform()
elif page == "Cardpayment":
    show_cardpayment()
elif page == "Contractnumbers":
    show_contractnumbers()
elif page == "Pricing":
    show_pricing()
elif page == "Radien":
    show_radien()
elif page == "Pipeline":
    show_pipeline()
elif page == "Hubspot":
    show_hubspot()
elif page == "Restaurants":
    show_restaurants() 
