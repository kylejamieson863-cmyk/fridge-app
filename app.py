import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE SETUP & SESSION STATE
# ---------------------------------------------------------
st.set_page_config(page_title="Smart Pantry & Meal Planner", page_icon="🥩", layout="wide")

if "inventory" not in st.session_state:
    st.session_state.inventory = []

# ---------------------------------------------------------
# 2. HANDLE AUTO-SAVED BARCODE FROM CAMERA
# ---------------------------------------------------------
def lookup_barcode(barcode_str):
    """Fetches product details from public Open Food Facts API."""
    barcode_clean = str(barcode_str).strip()
    
    for test_code in [barcode_clean, barcode_clean.zfill(13)]:
        url = f"https://world.openfoodfacts.org/api/v2/product/{test_code}.json"
        headers = {"User-Agent": "SmartPantryApp/1.0"}
        try:
            res = requests.get(url, headers=headers, timeout=3).json()
            if res.get("status") == 1:
                product = res.get("product", {})
                name = product.get("product_name") or product.get("product_name_en") or f"M&S Product ({barcode_str})"
                categories = product.get("categories_tags", [])
                
                cat = "ready_meal"
                if any("meat" in c or "poultry" in c for c in categories):
                    cat = "meat"
                elif any("dairy" in c or "cheese" in c or "milk" in c for c in categories):
                    cat = "dairy"
                elif any("vegetable" in c or "fruit" in c or "produce" in c or "grape" in c for c in categories):
                    cat = "produce"
                    
                return name, cat
        except Exception:
            pass
            
    return f"M&S Item ({barcode_str})", "produce" if "0857" in str(barcode_str) else "ready_meal"

# Auto-catch scanned code sent via URL parameter
if "scanned" in st.query_params:
    scanned_code = st.query_params["scanned"]
    st.query_params.clear() # Clear param so browser is ready for next scan
    
    item_name, category = lookup_barcode(scanned_code)
    st.session_state.inventory.append({
        "name": item_name,
        "category": category,
        "source": "M&S",
        "barcode": scanned_code,
        "expiry_date": datetime.today().strftime("%Y-%m-%d")
    })
    st.toast(f"✅ Auto-Saved: **{item_name}**", icon="🛒")

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------
def generate_smart_recipes(inventory):
    """Internal recipe planner matching expiring fridge contents."""
    if not inventory:
        return "Your fridge is empty! Add items to generate recipe ideas."
    
    sorted_items = sorted(inventory, key=lambda x: x.get("expiry_date", "9999-99-99"))
    expiring_soon = [i["name"] for i in sorted_items[:3]]
    
    meats = [i["name"] for i in inventory if i.get("category") == "meat"]
    produce = [i["name"] for i in inventory if i.get("category") == "produce"]
    dairy = [i["name"] for i in inventory if i.get("category") == "dairy"]
    
    recipes = []
    if meats and produce:
        recipes.append(f"**1. Pan-Seared {meats[0]} with Fresh {produce[0]}**\n* Prioritizing: {meats[0]}, {produce[0]}\n* *Instructions:* Sear {meats[0]} in a hot pan; sauté {produce[0]} as a fresh side.")
    if meats:
        recipes.append(f"**2. High-Protein {meats[0]} Skillet**\n* Prioritizing: {meats[0]}\n* *Instructions:* Cook {meats[0]} thoroughly and serve alongside your favorite staple grains.")
    if produce or dairy:
        prod_str = produce[0] if produce else "greens"
        dairy_str = dairy[0] if dairy else "cheese"
        recipes.append(f"**3. Quick {prod_str.title()} & {dairy_str.title()} Bowl**\n* Prioritizing: {prod_str}, {dairy_str}\n* *Instructions:* Mix {prod_str} with {dairy_str} for a fast meal.")

    if not recipes:
        recipes.append(f"**1. Quick Pantry Stir-Fry**\n* Prioritizing: {', '.join(expiring_soon)}\n* *Instructions:* Sauté earliest expiring ingredients together with seasonings.")

    out = "### 🍳 Suggested Meals (Prioritizing Earliest Expirations):\n\n"
    out += "\n\n---\n\n".join(recipes)
    return out

def render_visual_fridge(inventory):
    """Renders visual CSS representation of fridge zones."""
    top_shelf = [i for i in inventory if i.get("category") in ["dairy", "ready_meal"]]
    bottom_shelf = [i for i in inventory if i.get("category") == "meat"]
    crisper = [i for i in inventory if i.get("category") == "produce"]

    def generate_pills(items):
        html = ""
        for item in items:
            exp_str = item.get("expiry_date", "")
            is_urgent = False
            if exp_str:
                try:
                    days = (datetime.strptime(exp_str, "%Y-%m-%d").date() - datetime.today().date()).days
                    if days <= 2:
                        is_urgent = True
                except ValueError:
                    pass
            
            color = "#ff4d4d" if is_urgent else "#2e7d32"
            html += f'''
            <span style="
                background-color: {color};
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 13px;
                font-weight: bold;
                display: inline-block;
                margin: 3px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);">
                {item["name"]}
            </span>
            '''
        return html or '<span style="color:#888; font-style:italic;">Empty</span>'

    fridge_html = f"""
    <div style="
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
        border: 5px solid #90caf9;
        border-radius: 20px;
        padding: 15px;
        max-width: 450px;
        margin: 0 auto;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);">
        
        <div style="background: rgba(255,255,255,0.75); border-bottom: 5px solid #90caf9; padding: 12px; min-height: 90px; border-radius: 12px 12px 0 0;">
            <small style="color: #1565c0; font-weight: bold;">🥛 TOP SHELF (Dairy & Prepared)</small><br>
            {generate_pills(top_shelf)}
        </div>

        <div style="background: rgba(255,255,255,0.75); border-bottom: 5px solid #90caf9; padding: 12px; min-height: 90px; margin-top: 6px;">
            <small style="color: #1565c0; font-weight: bold;">🥩 BOTTOM SHELF (Butcher & Fresh Meat)</small><br>
            {generate_pills(bottom_shelf)}
        </div>

        <div style="display: flex; gap: 6px; margin-top: 6px;">
            <div style="flex: 1; background: rgba(255,255,255,0.85); padding: 10px; min-height: 80px; border-radius: 0 0 12px 12px; border: 2px solid #a5d6a7;">
                <small style="color: #2e7d32; font-weight: bold;">🥗 CRISPER DRAWER</small><br>
                {generate_pills(crisper)}
            </div>
        </div>
    </div>
    """
    st.html(fridge_html)

# ---------------------------------------------------------
# 4. INTERFACE TABS
# ---------------------------------------------------------
st.title("🥩 Smart Fridge & Meal Planner")

tab1, tab2, tab3 = st.tabs(["🛒 Trolley Scanner", "🧊 What's in My Fridge?", "🍳 Meal Planner"])

# --- TAB 1: SHOPPING & SCANNING ---
with tab1:
    st.header("Add Items to Fridge")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Hands-Free Barcode Scanner")
        st.caption("Point rear camera at barcode — auto-saves & resets instantly!")
        
        item_exp = st.date_input("Use-By Date:", datetime.today(), key="scan_exp_date")
        
        # HTML5 Continuous Scanner using Rear Camera
        scanner_html = """
        <div id="reader" style="width: 100%; border-radius: 12px; overflow: hidden;"></div>
        <div id="scan-status" style="text-align:center; font-weight:bold; color:#2e7d32; margin-top:8px;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            let isProcessing = false;

            function onScanSuccess(decodedText) {
                if (isProcessing) return;
                isProcessing = true;

                if (navigator.vibrate) navigator.vibrate(100);
                document.getElementById('scan-status').innerText = "✅ Saving code: " + decodedText + "...";

                // Pass barcode directly to top window URL to trigger Streamlit auto-save
                const targetUrl = new URL(window.top.location.href);
                targetUrl.searchParams.set("scanned", decodedText);
                window.top.location.href = targetUrl.href;
            }

            const html5QrCode = new Html5Qrcode("reader");
            
            const config = {
                fps: 15,
                qrbox: function(w, h) {
                    let minEdge = Math.min(w, h);
                    return { width: Math.floor(minEdge * 0.8), height: Math.floor(minEdge * 0.5) };
                },
                aspectRatio: 1.333333,
                experimentalFeatures: {
                    useBarCodeDetectorIfSupported: true
                }
            };

            // Force rear camera (environment mode)
            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
                .catch(err => {
                    html5QrCode.start({ facingMode: "user" }, config, onScanSuccess);
                });
        </script>
        """
        
        components.html(scanner_html, height=360)

        st.divider()
        st.caption("Quick Manual Entry:")
        manual_name = st.text_input("Enter Product Name or Barcode Digits:", key="manual_barcode")
        manual_cat = st.selectbox("Category:", ["meat", "dairy", "produce", "ready_meal"])
        
        if st.button("Add Manual Item"):
            if manual_name:
                if manual_name.isdigit():
                    name, cat = lookup_barcode(manual_name)
                else:
                    name, cat = manual_name, manual_cat
                    
                st.session_state.inventory.append({
                    "name": name,
                    "category": cat,
                    "source": "Manual",
                    "expiry_date": item_exp.strftime("%Y-%m-%d")
                })
                st.success(f"Added: **{name}**")

    with col2:
        st.subheader("2. Butcher Quick Entry")
        st.caption("Type butcher meat cuts directly")
        
        butcher_item = st.text_input("Meat Cut Name (e.g. Ribeye Steak, Minced Beef):")
        butcher_exp = st.date_input("Meat Expiry Date:", datetime.today(), key="butcher_exp_date")
        
        if st.button("Add Meat Item"):
            if butcher_item:
                st.session_state.inventory.append({
                    "name": butcher_item,
                    "category": "meat",
                    "source": "Butcher",
                    "expiry_date": butcher_exp.strftime("%Y-%m-%d")
                })
                st.success(f"Added: **{butcher_item}** to Bottom Shelf!")

# --- TAB 2: VISUAL FRIDGE ---
with tab2:
    st.header("Visual Fridge Display")
    
    if st.session_state.inventory:
        render_visual_fridge(st.session_state.inventory)
        
        st.divider()
        st.subheader("Item List Management")
        df = pd.DataFrame(st.session_state.inventory)
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Clear Entire Fridge"):
            st.session_state.inventory = []
            st.rerun()
    else:
        st.info("Your fridge is empty! Use the Trolley Scanner tab to add items.")

# --- TAB 3: MEAL PLANNER ---
with tab3:
    st.header("Smart Meal Planner")
    
    if st.session_state.inventory:
        if st.button("🍳 What Should I Make for Dinner?"):
            recipes = generate_smart_recipes(st.session_state.inventory)
            st.markdown(recipes)
    else:
        st.warning("Add food items to your fridge before requesting meal ideas.")
