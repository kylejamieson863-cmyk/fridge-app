import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from PIL import Image
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. PAGE SETUP & SESSION STATE
# ---------------------------------------------------------
st.set_page_config(page_title="Smart Pantry & Meal Planner", page_icon="🥩", layout="wide")

if "inventory" not in st.session_state:
    st.session_state.inventory = []

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def lookup_barcode(barcode_str):
    """Fetches product details from Open Food Facts API."""
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode_str}.json"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("status") == 1:
            product = res.get("product", {})
            name = product.get("product_name") or product.get("product_name_en") or f"M&S Item ({barcode_str})"
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
    return f"M&S Item ({barcode_str})", "ready_meal"

def scan_barcode_from_image(image):
    """Uses Gemini Vision API to extract barcode digits or product name from photo."""
    if not GEMINI_API_KEY:
        st.error("Please add `GEMINI_API_KEY` to your Streamlit secrets.")
        return None, "ready_meal"
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = """
        Analyze this photo of a food product or barcode.
        Extract:
        1. The barcode digits (EAN/UPC) if visible, OR the exact product name.
        2. Category: 'meat', 'dairy', 'produce', or 'ready_meal'.
        
        Return ONLY a JSON object:
        {"barcode_or_name": "5000169001234", "category": "meat"}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        val = data.get("barcode_or_name", "")
        cat = data.get("category", "ready_meal")
        
        # If Gemini returned numeric barcode, look it up in Open Food Facts
        if val.isdigit():
            name, official_cat = lookup_barcode(val)
            return name, official_cat
        return val, cat
    except Exception as e:
        st.error(f"Error reading scan photo: {e}")
        return None, "ready_meal"

def parse_receipt_with_gemini(image):
    """Uses Gemini Vision API to extract item names from printed receipts."""
    if not GEMINI_API_KEY:
        st.error("Please add `GEMINI_API_KEY` to your Streamlit secrets.")
        return []
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = """
        Extract all food items from this printed butcher receipt/invoice.
        Categorize each as 'meat', 'dairy', 'produce', or 'ready_meal'.
        Return ONLY a JSON array:
        [{"name": "Ribeye Steak 500g", "category": "meat"}]
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error processing receipt image: {e}")
        return []

def generate_recipes(inventory):
    """Generates recipe ideas based on current fridge contents."""
    if not GEMINI_API_KEY:
        return "Please add `GEMINI_API_KEY` to your Streamlit secrets to generate custom recipes."
    
    items_str = ", ".join([f"{item['name']} (exp: {item['expiry_date']})" for item in inventory])
    prompt = f"""
    You are a chef. Based on these ingredients currently in my fridge: [{items_str}],
    suggest 3 simple, delicious meal ideas. Prioritize ingredients expiring earliest.
    Format nicely in Markdown with bullet points for ingredients and quick instructions.
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Could not generate recipes: {e}"

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
        
        <!-- Top Shelf -->
        <div style="background: rgba(255,255,255,0.75); border-bottom: 5px solid #90caf9; padding: 12px; min-height: 90px; border-radius: 12px 12px 0 0;">
            <small style="color: #1565c0; font-weight: bold;">🥛 TOP SHELF (Dairy & Prepared)</small><br>
            {generate_pills(top_shelf)}
        </div>

        <!-- Middle/Lower Shelf -->
        <div style="background: rgba(255,255,255,0.75); border-bottom: 5px solid #90caf9; padding: 12px; min-height: 90px; margin-top: 6px;">
            <small style="color: #1565c0; font-weight: bold;">🥩 BOTTOM SHELF (Butcher & Fresh Meat)</small><br>
            {generate_pills(bottom_shelf)}
        </div>

        <!-- Crisper Drawers -->
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
        st.subheader("1. M&S Product Camera")
        st.caption("Point camera at product/barcode & tap snap to auto-add")
        
        item_exp = st.date_input("Use-By Date:", datetime.today(), key="scan_exp_date")
        camera_photo = st.camera_input("Take photo of item or barcode")
        
        if camera_photo:
            img = Image.open(camera_photo)
            with st.spinner("Analyzing photo & identifying product..."):
                item_name, category = scan_barcode_from_image(img)
                if item_name:
                    st.session_state.inventory.append({
                        "name": item_name,
                        "category": category,
                        "source": "M&S",
                        "expiry_date": item_exp.strftime("%Y-%m-%d")
                    })
                    st.toast(f"✅ Added: **{item_name}**", icon="🛒")
                    st.success(f"Added: **{item_name}** ({category})")

        st.divider()
        st.caption("Manual Entry Fallback:")
        barcode_input = st.text_input("Or type barcode manually:", key="manual_barcode")
        
        if st.button("Add Manual Barcode"):
            if barcode_input:
                name, cat = lookup_barcode(barcode_input)
                st.session_state.inventory.append({
                    "name": name,
                    "category": cat,
                    "source": "M&S",
                    "expiry_date": item_exp.strftime("%Y-%m-%d")
                })
                st.success(f"Added: **{name}**")

    with col2:
        st.subheader("2. Butcher Receipt Snap")
        uploaded_file = st.file_uploader("Snap photo of printed butcher invoice:", type=["jpg", "jpeg", "png"])
        butcher_exp = st.date_input("Default Meat Expiry Date:", datetime.today(), key="butcher_exp_date")
        
        if uploaded_file and st.button("Process Receipt"):
            img = Image.open(uploaded_file)
            st.image(img, caption="Invoice Photo", width=200)
            
            with st.spinner("Parsing items using Vision AI..."):
                parsed = parse_receipt_with_gemini(img)
                for item in parsed:
                    st.session_state.inventory.append({
                        "name": item.get("name", "Butcher Item"),
                        "category": item.get("category", "meat"),
                        "source": "Butcher",
                        "expiry_date": butcher_exp.strftime("%Y-%m-%d")
                    })
                st.success(f"Added {len(parsed)} items from butcher receipt!")

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
    st.header("AI Recipe Generator")
    st.write("Generates custom recipes prioritizing items closest to expiration.")
    
    if st.session_state.inventory:
        if st.button("🍳 What Should I Make for Dinner?"):
            with st.spinner("Consulting chef AI..."):
                recipes = generate_recipes(st.session_state.inventory)
                st.markdown(recipes)
    else:
        st.warning("Add food items to your fridge before requesting meal ideas.")
