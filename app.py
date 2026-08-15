import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from PIL import Image
import numpy as np
import cv2

# ---------------------------------------------------------
# 1. PAGE SETUP & SESSION STATE
# ---------------------------------------------------------
st.set_page_config(page_title="Smart Pantry & Meal Planner", page_icon="🥩", layout="wide")

if "inventory" not in st.session_state:
    st.session_state.inventory = []

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS (ZERO API KEYS REQUIRED)
# ---------------------------------------------------------
def lookup_barcode(barcode_str):
    """Fetches product details from public Open Food Facts API (No API key required)."""
    barcode_clean = str(barcode_str).strip().zfill(13)
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode_clean}.json"
    headers = {"User-Agent": "SmartPantryApp/1.0"}
    try:
        res = requests.get(url, headers=headers, timeout=5).json()
        if res.get("status") == 1:
            product = res.get("product", {})
            name = product.get("product_name") or product.get("product_name_en") or f"M&S Item ({barcode_clean})"
            categories = product.get("categories_tags", [])
            
            cat = "ready_meal"
            if any("meat" in c or "poultry" in c for c in categories):
                cat = "meat"
            elif any("dairy" in c or "cheese" in c or "milk" in c for c in categories):
                cat = "dairy"
            elif any("vegetable" in c or "fruit" in c or "produce" in c for c in categories):
                cat = "produce"
                
            return name, cat
    except Exception:
        pass
    return f"Scanned Item ({barcode_clean})", "ready_meal"

def scan_barcode_from_image(pil_image):
    """Detects barcode numbers directly from a photo using OpenCV."""
    try:
        img_np = np.array(pil_image.convert("RGB"))
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        # Initialize OpenCV Barcode Detector
        detector = cv2.barcode.BarcodeDetector()
        retval, decoded_info, decoded_type = detector.detectAndDecode(img_cv)
        
        if retval and decoded_info:
            for code in decoded_info:
                if code:
                    return code.strip()
    except Exception as e:
        st.error(f"Error scanning photo: {e}")
    return None

def generate_smart_recipes(inventory):
    """Internal rule-based recipe matching engine based on expiring items."""
    if not inventory:
        return "Your fridge is empty! Add items to generate recipe ideas."
    
    # Sort inventory by expiry date
    sorted_items = sorted(inventory, key=lambda x: x.get("expiry_date", "9999-99-99"))
    expiring_soon = [i["name"] for i in sorted_items[:3]]
    
    meats = [i["name"] for i in inventory if i.get("category") == "meat"]
    produce = [i["name"] for i in inventory if i.get("category") == "produce"]
    dairy = [i["name"] for i in inventory if i.get("category") == "dairy"]
    
    recipes = []
    
    if meats and produce:
        recipes.append(f"**1. Fresh Pan-Seared {meats[0]} with {produce[0]}**\n* Priority items used: {meats[0]}, {produce[0]}\n* *Quick Instructions:* Sear the {meats[0]} in a hot pan. Sauté {produce[0]} alongside with seasonings and serve hot.")
    
    if meats:
        recipes.append(f"**2. High-Protein {meats[0]} Skillet**\n* Priority items used: {meats[0]}\n* *Quick Instructions:* Chop and cook {meats[0]} thoroughly. Pair with rice, pasta, or fresh salad.")
        
    if produce or dairy:
        prod_str = produce[0] if produce else "fresh greens"
        dairy_str = dairy[0] if dairy else "cheese/butter"
        recipes.append(f"**3. Quick {prod_str.title()} & {dairy_str.title()} Omelette/Bowl**\n* Priority items used: {prod_str}, {dairy_str}\n* *Quick Instructions:* Lightly sauté {prod_str}, mix with eggs or grains, and top with {dairy_str}.")

    if not recipes:
        recipes.append(f"**1. Quick Fridge Stir-Fry**\n* Priority items used: {', '.join(expiring_soon)}\n* *Quick Instructions:* Chop all items fine and flash-fry in oil with soy sauce or favorite spice rub.")

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
# 3. INTERFACE TABS
# ---------------------------------------------------------
st.title("🥩 Smart Fridge & Meal Planner")

tab1, tab2, tab3 = st.tabs(["🛒 Trolley Scanner", "🧊 What's in My Fridge?", "🍳 Meal Planner"])

# --- TAB 1: SHOPPING & SCANNING ---
with tab1:
    st.header("Add Items to Fridge")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Barcode Photo Scanner")
        st.caption("Point camera at barcode & tap snap")
        
        item_exp = st.date_input("Use-By Date:", datetime.today(), key="scan_exp_date")
        camera_photo = st.camera_input("Take photo of barcode")
        
        if camera_photo:
            img = Image.open(camera_photo)
            with st.spinner("Reading barcode digits..."):
                detected_code = scan_barcode_from_image(img)
                if detected_code:
                    item_name, category = lookup_barcode(detected_code)
                    st.session_state.inventory.append({
                        "name": item_name,
                        "category": category,
                        "source": "M&S",
                        "expiry_date": item_exp.strftime("%Y-%m-%d")
                    })
                    st.toast(f"✅ Added: **{item_name}**", icon="🛒")
                    st.success(f"Added: **{item_name}** ({category})")
                else:
                    st.warning("Barcode standard not recognized in photo. Use quick manual entry below.")

        st.divider()
        st.caption("Quick Manual Barcode / Name Entry:")
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
