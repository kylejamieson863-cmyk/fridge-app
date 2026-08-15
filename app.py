import os
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIG & LUXURY CSS INJECTION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Pantry | Food & Meal Planner",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Aesthetic CSS
ms_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,400&display=swap');

    /* Global Background & Typography */
    .stApp {
        background-color: #F8F9F6;
        font-family: 'Montserrat', sans-serif;
        color: #1E1E1E;
    }

    /* Header Banner */
    .ms-header {
        background-color: #003B25;
        color: #FFFFFF;
        padding: 24px 20px;
        text-align: center;
        border-bottom: 3px solid #C5A059;
        margin-bottom: 25px;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 4px 12px rgba(0, 59, 37, 0.15);
    }
    .ms-brand {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: 4px;
        margin: 0;
        color: #FFFFFF;
    }
    .ms-subbrand {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #C5A059;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Custom Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #E0E0E0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #FFFFFF;
        border-radius: 8px 8px 0 0;
        border: 1px solid #E0E0E0;
        border-bottom: none;
        padding: 0 24px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        font-size: 13px;
        letter-spacing: 0.5px;
        color: #555555;
    }
    .stTabs [aria-selected="true"] {
        background-color: #003B25 !important;
        color: #FFFFFF !important;
        border-color: #003B25 !important;
        font-weight: 600;
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: #003B25 !important;
        color: #FFFFFF !important;
        border: 1px solid #003B25 !important;
        border-radius: 6px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .stButton > button:hover {
        background-color: #C5A059 !important;
        border-color: #C5A059 !important;
        color: #1E1E1E !important;
    }

    /* Card Containers */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
        border-radius: 12px;
    }

    /* Inputs */
    input, select {
        border-radius: 6px !important;
        border: 1px solid #CCCCCC !important;
    }
</style>
"""
st.markdown(ms_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CREATE NATIVE SCANNER COMPONENT (CENTERED OVERLAY)
# ---------------------------------------------------------
os.makedirs("scanner_component", exist_ok=True)

HTML_SCANNER_CODE = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/html5-qrcode"></script>
  <style>
    body { 
        margin: 0; 
        padding: 0; 
        font-family: 'Montserrat', -apple-system, sans-serif; 
        background: transparent; 
    }
    #reader { 
        width: 100%; 
        height: 300px;
        border-radius: 12px; 
        overflow: hidden; 
        background: #000; 
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        border: 2px solid #C5A059;
    }
    #reader video {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
    }
    #reader__scan_region {
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        margin: 0 !important;
    }
    #status { 
        text-align: center; 
        font-weight: 600; 
        color: #003B25; 
        margin-top: 10px; 
        font-size: 13px; 
        letter-spacing: 0.5px;
        min-height: 22px; 
    }
  </style>
</head>
<body>
  <div id="reader"></div>
  <div id="status">📷 Initializing rear scanner...</div>

  <script>
    function sendMessage(type, data) {
        window.parent.postMessage(Object.assign({
            isStreamlitMessage: true,
            type: type
        }, data), "*");
    }

    sendMessage("streamlit:componentReady", {apiVersion: 1});
    sendMessage("streamlit:setFrameHeight", {height: 350});

    let isCooldown = false;

    function sendResult(val) {
        sendMessage("streamlit:setComponentValue", {value: val});
    }

    function onScanSuccess(decodedText) {
        if (isCooldown) return;
        isCooldown = true;

        if (navigator.vibrate) navigator.vibrate(120);
        document.getElementById('status').innerText = "✨ SAVED " + decodedText + " TO PANTRY";
        
        sendResult(decodedText);

        setTimeout(() => {
            sendResult(null);
            document.getElementById('status').innerText = "Ready for next item...";
            isCooldown = false;
        }, 2200);
    }

    const html5QrCode = new Html5Qrcode("reader");
    const config = {
        fps: 25,
        qrbox: { width: 260, height: 150 },
        experimentalFeatures: {
            useBarCodeDetectorIfSupported: true
        }
    };

    html5QrCode.start({ facingMode: { exact: "environment" } }, config, onScanSuccess)
        .then(() => {
            document.getElementById('status').innerText = "READY TO SCAN";
        })
        .catch(() => {
            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
                .then(() => {
                    document.getElementById('status').innerText = "READY TO SCAN";
                })
                .catch(err => {
                    html5QrCode.start({ facingMode: "user" }, config, onScanSuccess);
                    document.getElementById('status').innerText = "READY TO SCAN (FRONT CAMERA)";
                });
        });
  </script>
</body>
</html>
"""

with open("scanner_component/index.html", "w") as f:
    f.write(HTML_SCANNER_CODE)

barcode_scanner = components.declare_component("barcode_scanner", path="scanner_component")

# ---------------------------------------------------------
# 3. SESSION STATE & LOGIC
# ---------------------------------------------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = []

if "last_processed_code" not in st.session_state:
    st.session_state.last_processed_code = None

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
                name = product.get("product_name") or product.get("product_name_en") or f"Product ({barcode_str})"
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
            
    return f"Scanned Item ({barcode_str})", "produce" if "0857" in str(barcode_str) else "ready_meal"

def generate_smart_recipes(inventory):
    """Internal recipe planner matching expiring fridge contents."""
    if not inventory:
        return "Your Pantry is empty! Add items to generate recipe inspirations."
    
    sorted_items = sorted(inventory, key=lambda x: x.get("expiry_date", "9999-99-99"))
    expiring_soon = [i["name"] for i in sorted_items[:3]]
    
    meats = [i["name"] for i in inventory if i.get("category") == "meat"]
    produce = [i["name"] for i in inventory if i.get("category") == "produce"]
    dairy = [i["name"] for i in inventory if i.get("category") == "dairy"]
    
    recipes = []
    if meats and produce:
        recipes.append(f"**1. Pan-Seared {meats[0]} with Fresh {produce[0]}**\n* Prioritizing: {meats[0]}, {produce[0]}\n* *Chef's Note:* Sear {meats[0]} over medium-high heat; toss {produce[0]} in olive oil and roast gently.")
    if meats:
        recipes.append(f"**2. Premium {meats[0]} Gourmet Skillet**\n* Prioritizing: {meats[0]}\n* *Chef's Note:* Pair {meats[0]} with roasted potatoes and a splash of red wine reduction.")
    if produce or dairy:
        prod_str = produce[0] if produce else "seasoned greens"
        dairy_str = dairy[0] if dairy else "artisan cheese"
        recipes.append(f"**3. Fresh {prod_str.title()} & {dairy_str.title()} Salad Bowl**\n* Prioritizing: {prod_str}, {dairy_str}\n* *Chef's Note:* Dress {prod_str} with extra virgin olive oil and crumble {dairy_str} over top.")

    if not recipes:
        recipes.append(f"**1. Quick Chef's Special**\n* Prioritizing: {', '.join(expiring_soon)}\n* *Chef's Note:* Gently sauté earliest expiring ingredients together with herbs.")

    out = "### 🍴 Inspired Recipes (Prioritizing Earliest Expirations):\n\n"
    out += "\n\n---\n\n".join(recipes)
    return out

def render_visual_fridge(inventory):
    """Renders visual representation of pantry/fridge zones."""
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
            
            bg_color = "#8B0000" if is_urgent else "#003B25"
            html += f'''
            <span style="
                background-color: {bg_color};
                color: #FFFFFF;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
                display: inline-block;
                margin: 4px;
                border: 1px solid #C5A059;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                {item["name"]}
            </span>
            '''
        return html or '<span style="color:#888888; font-style:italic; font-size:12px;">No items stored</span>'

    fridge_html = f"""
    <div style="
        background: #FFFFFF;
        border: 2px solid #C5A059;
        border-radius: 16px;
        padding: 20px;
        max-width: 480px;
        margin: 0 auto;
        box-shadow: 0 8px 24px rgba(0, 59, 37, 0.08);">
        
        <div style="text-align: center; border-bottom: 1px solid #E0E0E0; padding-bottom: 10px; margin-bottom: 15px;">
            <span style="font-family: 'Playfair Display', serif; font-size: 16px; letter-spacing: 2px; color: #003B25; font-weight: 600;">CHILLED PANTRY</span>
        </div>

        <div style="background: #F8F9F6; border-left: 4px solid #C5A059; padding: 14px; min-height: 85px; border-radius: 6px; margin-bottom: 12px;">
            <small style="color: #003B25; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">🥛 TOP SHELF — Dairy & Prepared</small><br>
            <div style="margin-top: 8px;">{generate_pills(top_shelf)}</div>
        </div>

        <div style="background: #F8F9F6; border-left: 4px solid #003B25; padding: 14px; min-height: 85px; border-radius: 6px; margin-bottom: 12px;">
            <small style="color: #003B25; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">🥩 BOTTOM SHELF — Butcher & Fresh Meat</small><br>
            <div style="margin-top: 8px;">{generate_pills(bottom_shelf)}</div>
        </div>

        <div style="background: #F8F9F6; border-left: 4px solid #2E7D32; padding: 14px; min-height: 85px; border-radius: 6px;">
            <small style="color: #003B25; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">🥗 CRISPER DRAWER — Fresh Produce</small><br>
            <div style="margin-top: 8px;">{generate_pills(crisper)}</div>
        </div>
    </div>
    """
    st.html(fridge_html)

# ---------------------------------------------------------
# 4. BRANDED HEADER & INTERFACE TABS
# ---------------------------------------------------------
st.markdown("""
<div class="ms-header">
    <div class="ms-brand">SMART PANTRY</div>
    <div class="ms-subbrand">FOOD &bull; MEAL PLANNER</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 Trolley Scanner", "🧊 Chilled Pantry", "🍴 Gourmet Meal Planner"])

# --- TAB 1: SHOPPING & SCANNING ---
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Hands-Free Scanner")
        st.caption("Point camera at barcode — items auto-save to your Pantry.")
        
        item_exp = st.date_input("Use-By Date:", datetime.today(), key="scan_exp_date")
        
        # Native Camera Feed
        scanned_code = barcode_scanner(height=360, key="live_barcode_reader")
        
        if scanned_code and scanned_code != st.session_state.last_processed_code:
            st.session_state.last_processed_code = scanned_code
            item_name, category = lookup_barcode(scanned_code)
            
            st.session_state.inventory.append({
                "name": item_name,
                "category": category,
                "source": "Scan",
                "barcode": scanned_code,
                "expiry_date": item_exp.strftime("%Y-%m-%d")
            })
            st.toast(f"✨ Auto-Saved: **{item_name}**", icon="🛒")

        st.divider()
        st.caption("Quick Manual Lookup:")
        manual_name = st.text_input("Product Name or Barcode Digits:", key="manual_barcode")
        manual_cat = st.selectbox("Category:", ["meat", "dairy", "produce", "ready_meal"])
        
        if st.button("Add Item to Pantry"):
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
        st.subheader("2. Butcher Selection")
        st.caption("Add fresh butcher cuts directly to your bottom shelf")
        
        butcher_item = st.text_input("Meat Cut Name (e.g., Ribeye Steak, Minced Beef):")
        butcher_exp = st.date_input("Use-By Date:", datetime.today(), key="butcher_exp_date")
        
        if st.button("Add Meat Selection"):
            if butcher_item:
                st.session_state.inventory.append({
                    "name": butcher_item,
                    "category": "meat",
                    "source": "Butcher",
                    "expiry_date": butcher_exp.strftime("%Y-%m-%d")
                })
                st.success(f"Added: **{butcher_item}** to Fresh Meat Shelf!")

# --- TAB 2: VISUAL FRIDGE ---
with tab2:
    if st.session_state.inventory:
        render_visual_fridge(st.session_state.inventory)
        
        st.divider()
        st.subheader("Pantry Inventory Overview")
        df = pd.DataFrame(st.session_state.inventory)
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Clear Pantry"):
            st.session_state.inventory = []
            st.session_state.last_processed_code = None
            st.rerun()
    else:
        st.info("Your Pantry is currently empty! Use the Trolley Scanner to add fresh items.")

# --- TAB 3: MEAL PLANNER ---
with tab3:
    if st.session_state.inventory:
        if st.button("🍴 Generate Gourmet Recipe Ideas"):
            recipes = generate_smart_recipes(st.session_state.inventory)
            st.markdown(recipes)
    else:
        st.warning("Add food items to your pantry before generating meal inspirations.")
