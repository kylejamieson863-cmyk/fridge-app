import os
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import re
import io
import time
from datetime import datetime, timedelta
from PIL import Image, ImageEnhance
from supabase import create_client

# ---------------------------------------------------------
# 1. PAGE CONFIG & LUXURY STYLING INJECTION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Pantry | Kitchen Management",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ms_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,400&display=swap');

    .stApp {
        background-color: #0F172A;
        font-family: 'Montserrat', sans-serif;
        color: #F8FAFC;
    }

    div[data-testid="stDateInput"] input {
        inputmode: none !important;
        cursor: pointer !important;
    }

    .ms-header {
        background: linear-gradient(135deg, #003B25 0%, #002417 100%);
        color: #FFFFFF;
        padding: 20px;
        text-align: center;
        border-bottom: 3px solid #C5A059;
        margin-bottom: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
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

    div[data-testid="stForm"] {
        border: 1px solid #C5A059 !important;
        border-radius: 12px !important;
        padding: 25px !important;
        background-color: #1E293B !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1E293B;
        border-radius: 8px 8px 0 0;
        border: 1px solid #334155;
        border-bottom: none;
        padding: 0 24px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        font-size: 13px;
        letter-spacing: 0.5px;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #003B25 !important;
        color: #FFFFFF !important;
        border-color: #C5A059 !important;
        font-weight: 600;
    }

    .stButton > button, form [data-testid="stFormSubmitButton"] > button {
        background-color: #003B25 !important;
        color: #FFFFFF !important;
        border: 1px solid #C5A059 !important;
        border-radius: 10px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        width: 100%;
        min-height: 44px !important;
    }
    .stButton > button:hover, form [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #C5A059 !important;
        border-color: #C5A059 !important;
        color: #0F172A !important;
    }

    .scan-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #C5A059;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }

    .storage-container {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border: 6px solid #334155;
        border-radius: 16px;
        padding: 15px;
        box-shadow: inset 0 0 30px rgba(0, 240, 255, 0.05), 0 20px 40px rgba(0,0,0,0.6);
        position: relative;
    }

    .shelf-header-banner {
        background: linear-gradient(90deg, #003B25 0%, #005F3B 100%);
        color: #E2E8F0;
        border-left: 4px solid #C5A059;
        padding: 8px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .glass-shelf-line {
        height: 6px;
        background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.8), rgba(255,255,255,0.1));
        border-bottom: 2px solid #38BDF8;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        margin-top: 12px;
        margin-bottom: 20px;
    }

    div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
        font-weight: 600 !important;
        padding: 10px 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        text-align: left !important;
        margin-bottom: 6px !important;
    }

    div[data-testid="stPopover"].exp-red > button {
        border: 2px solid #EF4444 !important;
        border-bottom: 4px solid #EF4444 !important;
        background: linear-gradient(135deg, #2D1215 0%, #1E293B 100%) !important;
    }

    div[data-testid="stPopover"].exp-amber > button {
        border: 2px solid #F59E0B !important;
        border-bottom: 4px solid #F59E0B !important;
        background: linear-gradient(135deg, #2B2111 0%, #1E293B 100%) !important;
    }

    div[data-testid="stPopover"].exp-green > button {
        border: 2px solid #10B981 !important;
        border-bottom: 4px solid #10B981 !important;
        background: linear-gradient(135deg, #0D261E 0%, #1E293B 100%) !important;
    }

    div[data-testid="stPopover"].zone-stable > button {
        border: 2px solid #38BDF8 !important;
        border-bottom: 4px solid #38BDF8 !important;
        background: linear-gradient(135deg, #0C2A3A 0%, #1E293B 100%) !important;
    }

    div[data-testid="stPopover"] > button:hover {
        transform: translateY(-2px);
    }

    .empty-shelf-msg {
        color: #64748B;
        font-size: 12px;
        font-style: italic;
        text-align: center;
        padding: 8px 0;
    }

    .recipe-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .recipe-card-ready {
        border-left: 5px solid #10B981;
    }
    .recipe-card-missing {
        border-left: 5px solid #F59E0B;
    }
</style>
"""
st.markdown(ms_css, unsafe_allow_html=True)

st.components.v1.html(
    """
    <script>
    const suppressDateKeyboard = () => {
        const dateInputs = window.parent.document.querySelectorAll('div[data-testid="stDateInput"] input');
        dateInputs.forEach(input => {
            input.setAttribute('readonly', 'readonly');
            input.setAttribute('inputmode', 'none');
        });
    };
    setInterval(suppressDateKeyboard, 500);
    </script>
    """,
    height=0,
)

# ---------------------------------------------------------
# 2. HEADER & SUPABASE CONNECTION
# ---------------------------------------------------------
header_html = """
<div class="ms-header">
    <div class="ms-brand">SMART PANTRY</div>
    <div class="ms-subbrand">FOOD &bull; STORAGE &bull; MEAL PLANNER</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def load_user_inventory(user_id):
    try:
        response = supabase.table("fridge_inventory").select("*").eq("username", str(user_id)).execute()
        rows = response.data or []
        
        inventory = []
        for row in rows:
            inventory.append({
                "id": float(row["item_id"]),
                "name": str(row["name"]),
                "category": str(row["category"]),
                "location": str(row.get("location", "Fridge")),
                "portion": float(row.get("portion", 1.0)),
                "nutrition": {
                    "calories": str(row.get("calories", "N/A")),
                    "protein": str(row.get("protein", "N/A")),
                    "carbs": str(row.get("carbs", "N/A")),
                    "fat": str(row.get("fat", "N/A"))
                },
                "expiry_date": str(row.get("expiry_date", ""))
            })
        return inventory
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        return []

def save_user_inventory(user_id, inventory):
    try:
        supabase.table("fridge_inventory").delete().eq("username", str(user_id)).execute()
        
        if inventory:
            new_rows = []
            for item in inventory:
                nut = item.get("nutrition", {})
                new_rows.append({
                    "username": str(user_id),
                    "item_id": item["id"],
                    "name": item["name"],
                    "category": item["category"],
                    "location": item.get("location", "Fridge"),
                    "portion": item.get("portion", 1.0),
                    "calories": nut.get("calories", "N/A"),
                    "protein": nut.get("protein", "N/A"),
                    "carbs": nut.get("carbs", "N/A"),
                    "fat": nut.get("fat", "N/A"),
                    "expiry_date": item.get("expiry_date", "")
                })
            supabase.table("fridge_inventory").insert(new_rows).execute()
    except Exception as e:
        st.error(f"Error saving inventory: {e}")

# ---------------------------------------------------------
# 3. AUTHENTICATION
# ---------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        st.success("Logged in successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

def register_user(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        st.success("Account registered successfully!")
    except Exception as e:
        st.error(f"Registration failed: {e}")

def logout_user():
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.active_inv = []
        st.session_state.loaded_user = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")

if not st.session_state.user:
    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    with auth_col2:
        auth_tab1, auth_tab2 = st.tabs(["🔑 Login", "📝 Register New Account"])

        with auth_tab1:
            with st.form("login_form"):
                st.markdown("<h3 style='text-align: center; color: #C5A059;'>Member Access</h3>", unsafe_allow_html=True)
                login_email = st.text_input("Email Address")
                login_password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Sign In")

                if submit_login:
                    if login_email and login_password:
                        login_user(login_email, login_password)
                    else:
                        st.error("Please fill in all fields.")

        with auth_tab2:
            with st.form("signup_form"):
                st.markdown("<h3 style='text-align: center; color: #C5A059;'>Create an Account</h3>", unsafe_allow_html=True)
                reg_email = st.text_input("Email Address")
                reg_password = st.text_input("Password", type="password")
                submit_signup = st.form_submit_button("Register Account")

                if submit_signup:
                    if reg_email and reg_password:
                        register_user(reg_email, reg_password)
                    else:
                        st.error("Please fill in all fields.")
    st.stop()

# ---------------------------------------------------------
# 4. ISOLATED SESSION & BARCODE SETUP
# ---------------------------------------------------------
current_user_id = st.session_state.user.id
current_user_email = st.session_state.user.email

if "loaded_user" not in st.session_state or st.session_state.loaded_user != current_user_id:
    st.session_state.active_inv = load_user_inventory(current_user_id)
    st.session_state.loaded_user = current_user_id

active_inv = st.session_state.active_inv

if "pending_scanned_item" not in st.session_state:
    st.session_state.pending_scanned_item = None

if "staged_receipt_items" not in st.session_state:
    st.session_state.staged_receipt_items = []

if "scan_target_date" not in st.session_state:
    st.session_state.scan_target_date = datetime.today().date()

if "manual_target_date" not in st.session_state:
    st.session_state.manual_target_date = datetime.today().date()

top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.write(f"Logged in as: **{current_user_email}**")
with top_col2:
    if st.button("Logout"):
        logout_user()

# ---------------------------------------------------------
# 5. BARCODE SCANNER COMPONENT
# ---------------------------------------------------------
os.makedirs("scanner_component", exist_ok=True)

HTML_SCANNER_CODE = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/html5-qrcode"></script>
  <style>
    body { margin: 0; padding: 0; font-family: 'Montserrat', sans-serif; background: transparent; }
    #reader { width: 100%; height: 280px; border-radius: 12px; overflow: hidden; background: #000; display: flex !important; align-items: center !important; justify-content: center !important; position: relative !important; border: 2px solid #C5A059; }
    #reader video { width: 100% !important; height: 100% !important; object-fit: cover !important; }
    #reader__scan_region { position: absolute !important; top: 50% !important; left: 50% !important; transform: translate(-50%, -50%) !important; margin: 0 !important; }
    #status { text-align: center; font-weight: 600; color: #C5A059; margin-top: 10px; font-size: 13px; letter-spacing: 0.5px; min-height: 22px; }
  </style>
</head>
<body>
  <div id="reader"></div>
  <div id="status">📷 Camera Active</div>

  <script>
    function sendMessage(type, data) {
        window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type: type }, data), "*");
    }

    sendMessage("streamlit:componentReady", {apiVersion: 1});
    sendMessage("streamlit:setFrameHeight", {height: 330});

    let isCooldown = false;

    function sendResult(val) {
        sendMessage("streamlit:setComponentValue", {value: val});
    }

    function onScanSuccess(decodedText) {
        if (isCooldown) return;
        isCooldown = true;

        if (navigator.vibrate) navigator.vibrate(120);
        document.getElementById('status').innerText = "✨ BARCODE DETECTED!";
        
        sendResult(decodedText);

        setTimeout(() => {
            sendResult(null);
            document.getElementById('status').innerText = "Ready for next item...";
            isCooldown = false;
        }, 2200);
    }

    const html5QrCode = new Html5Qrcode("reader");
    const config = { fps: 25, qrbox: { width: 260, height: 150 }, experimentalFeatures: { useBarCodeDetectorIfSupported: true } };

    html5QrCode.start({ facingMode: { exact: "environment" } }, config, onScanSuccess)
        .then(() => { document.getElementById('status').innerText = "READY TO SCAN"; })
        .catch(() => {
            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
                .then(() => { document.getElementById('status').innerText = "READY TO SCAN"; })
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
# 6. HELPER FUNCTIONS & ROUTING
# ---------------------------------------------------------
def categorize_and_locate_item(name_str, category_tags=[]):
    text = (name_str + " " + " ".join(category_tags)).lower()

    frozen_keywords = ["frozen", "ice cream", "pizza", "chips", "peas", "nuggets", "waffles", "ice", "gelato"]
    cupboard_keywords = ["canned", "tin", "pasta", "rice", "sauce", "cereal", "spices", "flour", "oil", 
                         "biscuit", "crisps", "beans", "tinned", "oats", "noodle", "sugar", "salt"]

    if any(w in text for w in frozen_keywords):
        location = "Freezer"
    elif any(w in text for w in cupboard_keywords):
        location = "Cupboard"
    else:
        location = "Fridge"

    produce_keywords = ["potato", "potatoes", "onion", "onions", "grape", "grapes", "apple", "banana", "berry",
                        "fruit", "veg", "vegetable", "salad", "produce", "pickle", "pickled", "lemon", "lime"]
    meat_keywords = ["chicken", "chk", "beef", "steak", "pork", "lamb", "bacon", "sausage", "meat",
                     "mince", "salmon", "fish", "burger", "burgers", "kebabs", "kebab", "poultry", "shish"]
    dairy_keywords = ["milk", "cheese", "butter", "cream", "yogurt", "cheddar", "dip", "egg", "eggs", "lurpak", "spreadable", "drink"]

    if any(w in text for w in produce_keywords):
        category = "produce"
    elif any(w in text for w in meat_keywords):
        category = "meat"
    elif any(w in text for w in dairy_keywords):
        category = "dairy"
    else:
        category = "ready_meal"

    return category, location

def get_expiry_status(expiry_str, location="Fridge"):
    if location in ["Freezer", "Cupboard"] or not expiry_str:
        return "zone-stable", "🟦"
    try:
        exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        days_left = (exp_date - datetime.today().date()).days
        if days_left <= 1:
            return "exp-red", "🔴"
        elif days_left <= 3:
            return "exp-amber", "🟠"
        else:
            return "exp-green", "🟢"
    except Exception:
        return "exp-green", "🟢"

def lookup_barcode(barcode_str):
    barcode_clean = str(barcode_str).strip()
    default_nutrition = {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fat": "N/A"}
    
    saved_location = None
    try:
        mem_res = supabase.table("barcode_memory").select("location").eq("barcode", barcode_clean).execute()
        if mem_res.data and len(mem_res.data) > 0:
            saved_location = mem_res.data[0]["location"]
    except Exception:
        pass

    for test_code in [barcode_clean, barcode_clean.zfill(13)]:
        url = f"https://world.openfoodfacts.org/api/v2/product/{test_code}.json"
        headers = {"User-Agent": "SmartPantryApp/1.0"}
        try:
            res = requests.get(url, headers=headers, timeout=3).json()
            if res.get("status") == 1:
                product = res.get("product", {})
                name = product.get("product_name") or product.get("product_name_en") or f"Product ({barcode_str})"
                categories = product.get("categories_tags", [])
                
                nutriments = product.get("nutriments", {})
                nutrition = {
                    "calories": f"{nutriments.get('energy-kcal_100g', 'N/A')} kcal",
                    "protein": f"{nutriments.get('proteins_100g', 'N/A')} g",
                    "carbs": f"{nutriments.get('carbohydrates_100g', 'N/A')} g",
                    "fat": f"{nutriments.get('fat_100g', 'N/A')} g"
                }
                
                cat, loc = categorize_and_locate_item(name, categories)
                final_loc = saved_location if saved_location else loc
                return name, cat, final_loc, nutrition
        except Exception:
            pass
            
    cat, loc = categorize_and_locate_item(str(barcode_str))
    final_loc = saved_location if saved_location else loc
    return f"Scanned Item ({barcode_str})", cat, final_loc, default_nutrition

def process_receipt_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img.thumbnail((1200, 1200))
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        clean_bytes = buffer.getvalue()
        
        url = "https://api.ocr.space/parse/image"
        payload = {
            'apikey': 'helloworld',
            'language': 'eng',
            'OCREngine': '2',
            'isTable': 'true'
        }
        files = [('file', ('receipt.jpg', clean_bytes, 'image/jpeg'))]
        
        res = requests.post(url, data=payload, files=files, timeout=20)
        data = res.json()
        
        parsed_results = data.get('ParsedResults', [])
        if not parsed_results:
            return []
            
        raw_text = parsed_results[0].get('ParsedText', '')
        lines = raw_text.split('\r\n')
        
        ignore_keywords = [
            "total", "subtotal", "vat", "tax", "change", "cash", "visa", "mastercard",
            "card", "balance", "thank", "receipt", "store", "tel", "date", "time",
            "savings", "discount", "auth", "merchant", "pound", "http", "marks", "spencer",
            "manager", "street", "lane", "road", "order", "server", "table", "largs",
            "ka30", "vat no", "www", "saving", "tendered", "declined", "items", "m&s"
        ]
        
        extracted_items = []
        for line in lines:
            clean_line = re.sub(r'[^a-zA-Z0-9\s\&\.\-]', '', line).strip()
            if not clean_line or len(clean_line) < 4:
                continue
                
            line_lower = clean_line.lower()
            if any(k in line_lower for k in ignore_keywords):
                continue
                
            line_no_sku = re.sub(r'^\d{4,14}\s*', '', clean_line)
            cleaned_item = re.sub(r'[\s\d\.\-]{2,}$', '', line_no_sku).strip()
            
            letters_only = re.sub(r'[^a-zA-Z]', '', cleaned_item)
            if len(letters_only) < 3:
                continue
                
            cat, loc = categorize_and_locate_item(cleaned_item)
            extracted_items.append({"name": cleaned_item.title(), "category": cat, "location": loc})
            
        return extracted_items
    except Exception as e:
        st.error(f"Receipt Exception: {str(e)}")
        return []

def analyze_inventory_for_meals(inventory):
    if not inventory:
        return [], []

    counts = {}
    items_map = {}
    for item in inventory:
        clean_name = item["name"].strip().title()
        key = clean_name.lower()
        counts[key] = counts.get(key, 0) + 1
        items_map[key] = clean_name

    keys = set(counts.keys())

    def find_items(words):
        return [k for k in keys if any(w in k for w in words)]

    ready_meals = []
    missing_meals = []

    kebabs = find_items(["kebab", "shish", "kebabs"])
    naans = find_items(["naan", "naans", "pita", "flatbread"])
    dips = find_items(["dip", "sauce", "chutney"])
    pickles = find_items(["pickle", "pickled", "onion"])
    bolognese = find_items(["bolognese", "spaghetti"])
    burgers = find_items(["burger", "burgers", "smash burger"])
    potatoes = find_items(["potato", "potatoes", "maris piper"])
    protein_drinks = find_items(["protein drink", "shake"])

    if kebabs:
        k_title = items_map[kebabs[0]]
        in_stock = [f"{k_title} (x{counts[kebabs[0]]})"]
        missing = []

        if naans:
            in_stock.append(items_map[naans[0]])
        else:
            missing.append("Tandoori Naans or Flatbreads")

        if dips:
            in_stock.append(items_map[dips[0]])
        else:
            missing.append("Fresh Mint Yogurt or Garlic Dip")

        if pickles:
            in_stock.append(items_map[pickles[0]])

        dish_title = f"Gourmet {k_title} & Warm Naan Platter"
        instructions = "Grill or sizzle kebabs until charred. Serve over warm naans with gourmet dips and crisp pickled red onions."

        if not missing:
            ready_meals.append({"title": dish_title, "in_stock": in_stock, "missing": [], "instructions": instructions})
        else:
            missing_meals.append({"title": dish_title, "in_stock": in_stock, "missing": missing, "instructions": instructions})

    if bolognese:
        b_title = items_map[bolognese[0]]
        qty = counts[bolognese[0]]
        ready_meals.append({
            "title": f"Classic Italian Spaghetti Bolognese ({qty} Servings Ready)",
            "in_stock": [f"{b_title} (x{qty})"],
            "missing": [],
            "instructions": "Simmer gently until steaming hot. Pair with cracked black pepper and freshly grated Parmigiano-Reggiano."
        })

    if burgers:
        b_title = items_map[burgers[0]]
        in_stock = [f"{b_title} (x{counts[burgers[0]]})"]
        missing = ["Brioche Burger Buns", "Aged Cheddar Slices"]

        if pickles:
            in_stock.append(items_map[pickles[0]])

        missing_meals.append({
            "title": f"Artisanal {b_title} Brioche Stack",
            "in_stock": in_stock,
            "missing": missing,
            "instructions": "Sear patties on high heat for caramelized edges. Serve on toasted brioche with melted cheddar and tangy pickles."
        })

    if potatoes:
        p_title = items_map[potatoes[0]]
        p_stock = [p_title]
        p_missing = ["Ribeye Steak or Chicken Breasts", "Fresh Garlic & Rosemary Butter"]

        missing_meals.append({
            "title": f"Triple-Cooked Rosemary & Butter {p_title}",
            "in_stock": p_stock,
            "missing": p_missing,
            "instructions": "Parboil potatoes, crush gently, and crisp in pan with butter and herbs until golden-brown. Pair with seared protein."
        })

    if protein_drinks:
        p_name = items_map[protein_drinks[0]]
        qty = counts[protein_drinks[0]]
        ready_meals.append({
            "title": f"Post-Workout Fitness Fuel ({p_name})",
            "in_stock": [f"{p_name} (x{qty})"],
            "missing": [],
            "instructions": "Chill thoroughly before serving. Perfect for immediate post-workout macro recovery."
        })

    return ready_meals, missing_meals

# ---------------------------------------------------------
# 7. MAIN INTERFACE
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛒 Trolley Scanner", 
    "🧊 Fridge", 
    "❄️ Freezer", 
    "🥫 Cupboard", 
    "🍴 Meal Planner"
])

# --- TAB 1: SCANNING & RECEIPT ---
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Barcode Scanner")
        st.caption("Scan items directly in the aisle")
        
        scanned_code = barcode_scanner(key="live_barcode_reader")
        
        if scanned_code:
            item_name, category, location, nutrition = lookup_barcode(scanned_code)
            st.session_state.pending_scanned_item = {
                "barcode": str(scanned_code).strip(),
                "name": item_name,
                "category": category,
                "location": location,
                "nutrition": nutrition
            }
            st.session_state.scan_target_date = datetime.today().date()
            st.rerun()

        if st.session_state.pending_scanned_item:
            item = st.session_state.pending_scanned_item

            st.markdown(f"""
            <div class="scan-card">
                <h3 style="color: #C5A059; margin-top:0;">🛒 Item Scanned</h3>
                <h2 style="color: #FFFFFF; margin-bottom:5px;">{item['name']}</h2>
                <p style="color: #38BDF8; margin-bottom:0;">Auto-Routed Zone: <strong>{item['location']}</strong></p>
            </div>
            """, unsafe_allow_html=True)

            selected_location = st.selectbox(
                "Storage Location Zone:", 
                ["Fridge", "Freezer", "Cupboard"], 
                index=["Fridge", "Freezer", "Cupboard"].index(item["location"])
            )

            if selected_location == "Fridge":
                d_col1, d_col2 = st.columns([3, 1])
                with d_col1:
                    selected_scan_date = st.date_input(
                        "📅 Select Use-By / Best Before Date:",
                        value=st.session_state.scan_target_date,
                        key="scan_date_picker"
                    )
                    st.session_state.scan_target_date = selected_scan_date
                with d_col2:
                    st.write("&nbsp;")
                    if st.button("➕ 30 Days", key="add_30_scan"):
                        st.session_state.scan_target_date += timedelta(days=30)
                        st.rerun()
            else:
                st.info("ℹ️ Items in Freezer or Cupboard do not require tracking strict use-by dates.")

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("✅ Confirm & Save"):
                    unique_id = datetime.now().timestamp() + (time.time() % 1)
                    active_inv.append({
                        "id": unique_id,
                        "name": item["name"],
                        "category": item["category"],
                        "location": selected_location,
                        "portion": 1.0,
                        "nutrition": item["nutrition"],
                        "expiry_date": st.session_state.scan_target_date.strftime("%Y-%m-%d") if selected_location == "Fridge" else ""
                    })
                    save_user_inventory(current_user_id, active_inv)

                    if item.get("barcode"):
                        try:
                            supabase.table("barcode_memory").upsert({
                                "barcode": str(item["barcode"]),
                                "location": selected_location
                            }).execute()
                        except Exception:
                            pass

                    st.session_state.pending_scanned_item = None
                    st.session_state.scan_target_date = datetime.today().date()
                    st.toast(f"✨ Added to {selected_location}: **{item['name']}**", icon="🛒")
                    st.rerun()

            with c_btn2:
                if st.button("❌ Cancel"):
                    st.session_state.pending_scanned_item = None
                    st.session_state.scan_target_date = datetime.today().date()
                    st.rerun()

        st.divider()
        st.caption("Quick Manual Lookup:")
        manual_name = st.text_input("Product Name or Barcode Digits:", key="manual_barcode")
        manual_cat = st.selectbox("Category:", ["meat", "dairy", "produce", "ready_meal"])
        manual_loc = st.selectbox("Storage Location:", ["Fridge", "Freezer", "Cupboard"])
        
        if manual_loc == "Fridge":
            m_col1, m_col2 = st.columns([3, 1])
            with m_col1:
                selected_manual_date = st.date_input(
                    "Use-By Date:",
                    value=st.session_state.manual_target_date,
                    key="manual_date_picker"
                )
                st.session_state.manual_target_date = selected_manual_date
            with m_col2:
                st.write("&nbsp;")
                if st.button("➕ 30 Days", key="add_30_manual"):
                    st.session_state.manual_target_date += timedelta(days=30)
                    st.rerun()
        
        if st.button("Add Item to Storage"):
            if manual_name:
                if manual_name.isdigit():
                    name, cat, loc, nutrition = lookup_barcode(manual_name)
                    try:
                        supabase.table("barcode_memory").upsert({
                            "barcode": str(manual_name).strip(),
                            "location": manual_loc
                        }).execute()
                    except Exception:
                        pass
                else:
                    name = manual_name
                    cat = manual_cat
                    loc = manual_loc
                    nutrition = {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fat": "N/A"}
                
                unique_id = datetime.now().timestamp() + (time.time() % 1)
                active_inv.append({
                    "id": unique_id,
                    "name": name,
                    "category": cat,
                    "location": loc,
                    "portion": 1.0,
                    "nutrition": nutrition,
                    "expiry_date": st.session_state.manual_target_date.strftime("%Y-%m-%d") if loc == "Fridge" else ""
                })
                save_user_inventory(current_user_id, active_inv)
                st.session_state.manual_target_date = datetime.today().date()
                st.success(f"Added to {loc}: **{name}**")
                st.rerun()

    with col2:
        st.subheader("2. Receipt OCR Photo Scanner")
        st.caption("Snap a photo of your receipt")
        
        receipt_photo = st.file_uploader("Upload Receipt Image:", type=["jpg", "png", "jpeg"], key="receipt_upload")
        receipt_date = st.date_input("Use-By Date for Fresh Receipt Items:", datetime.today(), key="receipt_exp_date")
        
        if receipt_photo:
            if st.button("📄 Scan Receipt"):
                with st.spinner("Extracting grocery items..."):
                    img_bytes = receipt_photo.getvalue()
                    st.session_state.staged_receipt_items = process_receipt_image(img_bytes)

        if st.session_state.staged_receipt_items:
            st.markdown("---")
            st.subheader("Review Extracted Items:")
            staged_df = pd.DataFrame(st.session_state.staged_receipt_items)
            edited_df = st.data_editor(staged_df, num_rows="dynamic", key="receipt_editor")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Confirm & Save Receipts"):
                    confirmed_items = edited_df.to_dict("records")
                    for item in confirmed_items:
                        unique_id = datetime.now().timestamp() + (time.time() % 1)
                        loc = str(item.get("location", "Fridge"))
                        active_inv.append({
                            "id": unique_id,
                            "name": str(item["name"]),
                            "category": str(item["category"]),
                            "location": loc,
                            "portion": 1.0,
                            "nutrition": {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fat": "N/A"},
                            "expiry_date": receipt_date.strftime("%Y-%m-%d") if loc == "Fridge" else ""
                        })
                    save_user_inventory(current_user_id, active_inv)
                    st.session_state.staged_receipt_items = []
                    st.success("Saved receipt items into respective zones!")
                    st.rerun()
            with col_b:
                if st.button("❌ Discard Receipt"):
                    st.session_state.staged_receipt_items = []
                    st.rerun()

# --- REUSABLE ZONE DISPLAY RENDERER ---
def render_storage_zone(zone_name, shelves_config):
    zone_items = [
        item for item in active_inv 
        if str(item.get("location", "Fridge")).strip().title() == zone_name.title()
    ]

    if zone_name == "Fridge":
        st.markdown("""
        <div style="display: flex; gap: 15px; margin-bottom: 12px; font-size: 12px; justify-content: center; background: #1E293B; padding: 8px; border-radius: 8px; border: 1px solid #334155;">
            <span>🔴 Today/Tomorrow (&le; 1 day)</span>
            <span>🟠 2–3 Days</span>
            <span>🟢 Safe (&ge; 4 Days)</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="storage-container">', unsafe_allow_html=True)
    
    for shelf_idx, (title, cats) in enumerate(shelves_config):
        shelf_raw_items = [item for item in zone_items if item.get("category") in cats or (cats[0] == "ready_meal" and item.get("category") not in ["meat", "produce"])]
        
        total_items_count = len(shelf_raw_items)
        st.markdown(f'<div class="shelf-header-banner"><span>{title}</span><span>{total_items_count} ITEMS</span></div>', unsafe_allow_html=True)

        if not shelf_raw_items:
            st.markdown('<div class="empty-shelf-msg">Shelf is empty</div>', unsafe_allow_html=True)
        else:
            grouped_dict = {}
            for item in shelf_raw_items:
                group_key = (item["name"].strip().title(), item.get("expiry_date", "N/A"))
                if group_key not in grouped_dict:
                    grouped_dict[group_key] = []
                grouped_dict[group_key].append(item)

            grouped_keys = list(grouped_dict.keys())
            cols = st.columns(2)
            
            for idx, key in enumerate(grouped_keys):
                item_group = grouped_dict[key]
                first_item = item_group[0]
                qty = len(item_group)
                
                name, exp_date = key
                color_class, status_emoji = get_expiry_status(exp_date, zone_name)
                
                if zone_name == "Fridge":
                    label = f"{status_emoji} {name} (x{qty}) — Exp: {exp_date}" if qty > 1 else f"{status_emoji} {name} — Exp: {exp_date}"
                else:
                    label = f"🟦 {name} (x{qty})" if qty > 1 else f"🟦 {name}"

                col = cols[idx % 2]
                with col:
                    st.markdown(f'<div class="{color_class}">', unsafe_allow_html=True)
                    with st.popover(label, use_container_width=True):
                        st.markdown(f"### **{status_emoji} {name}**")
                        st.write(f"**Total Quantity in Stack:** {qty}")
                        if zone_name == "Fridge":
                            st.write(f"**Use-By Date:** {exp_date}")
                        
                        st.markdown("---")
                        st.markdown("**📊 Portion & Usage Tracker:**")
                        
                        current_portion = float(first_item.get("portion", 1.0))
                        st.progress(current_portion, text=f"Remaining: {int(current_portion * 100)}%")

                        p_col1, p_col2, p_col3 = st.columns(3)
                        btn_key_prefix = f"{zone_name}_{shelf_idx}_{idx}_{first_item['id']}"

                        if p_col1.button("1/4 Used", key=f"q_use_{btn_key_prefix}"):
                            first_item["portion"] -= 0.25
                            if first_item["portion"] <= 0:
                                active_inv.remove(first_item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()

                        if p_col2.button("1/2 Used", key=f"h_use_{btn_key_prefix}"):
                            first_item["portion"] -= 0.50
                            if first_item["portion"] <= 0:
                                active_inv.remove(first_item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()

                        if p_col3.button("Finish All", key=f"fin_use_{btn_key_prefix}"):
                            for itm in item_group:
                                active_inv.remove(itm)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()

                        if zone_name == "Fridge":
                            st.markdown("---")
                            if st.button("❄️ Move to Freezer", key=f"move_freezer_{btn_key_prefix}"):
                                for itm in item_group:
                                    itm["location"] = "Freezer"
                                    itm["expiry_date"] = ""
                                save_user_inventory(current_user_id, active_inv)
                                st.toast(f"Moved {name} to Freezer!")
                                st.rerun()

                        st.markdown("---")
                        st.markdown("**📊 Nutrition Info (per 100g):**")
                        nut = first_item.get("nutrition", {})
                        st.write(f"• **Calories:** {nut.get('calories', 'N/A')}")
                        st.write(f"• **Protein:** {nut.get('protein', 'N/A')}")
                        st.write(f"• **Carbs:** {nut.get('carbs', 'N/A')}")
                        st.write(f"• **Fat:** {nut.get('fat', 'N/A')}")

                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-shelf-line"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: FRIDGE INTERIOR ---
with tab2:
    render_storage_zone("Fridge", [
        ("🥛 TOP SHELF — Dairy, Drinks & Prepared Items", ["dairy", "ready_meal"]),
        ("🥩 MIDDLE SHELF — Meat & Poultry", ["meat"]),
        ("🥗 CRISPER DRAWER — Fresh Produce", ["produce"])
    ])

# --- TAB 3: FREEZER INTERIOR ---
with tab3:
    render_storage_zone("Freezer", [
        ("🍕 TOP DRAWER — Frozen Ready Meals & Snacks", ["ready_meal"]),
        ("🥩 MIDDLE DRAWER — Frozen Meat, Fish & Poultry", ["meat"]),
        ("🥦 BOTTOM DRAWER — Frozen Produce, Fruit & Veg", ["produce", "dairy"])
    ])

# --- TAB 4: CUPBOARD INTERIOR ---
with tab4:
    render_storage_zone("Cupboard", [
        ("🥫 TOP SHELF — Canned Foods & Tins", ["ready_meal"]),
        ("🍝 MIDDLE SHELF — Dry Grains, Pasta & Sauces", ["produce", "meat"]),
        ("☕ BOTTOM SHELF — Snacks, Spices & Essentials", ["dairy"])
    ])

# --- TAB 5: SMART GOURMET MEAL PLANNER ---
with tab5:
    st.subheader("🍴 Gourmet Meal Suggestions")
    st.caption("Matches your combined fridge, freezer, and cupboard items into complete dishes.")

    if not active_inv:
        st.info("Your kitchen inventory is empty! Add items using the scanner to view meal ideas.")
    else:
        ready_meals, missing_meals = analyze_inventory_for_meals(active_inv)

        st.markdown("### ✅ Ready-to-Serve Meals & Feasts")
        st.caption("Complete dishes made using the items currently in your storage zones.")

        if not ready_meals:
            st.write(" *No complete multi-ingredient dishes available right now.*")
        else:
            for meal in ready_meals:
                st.markdown(f"""
                <div class="recipe-card recipe-card-ready">
                    <h3 style="color: #10B981; margin: 0 0 8px 0;">{meal['title']}</h3>
                    <p style="margin: 0 0 8px 0; color: #E2E8F0; font-size: 13px;">
                        <strong>🥦 In Your Storage:</strong> {', '.join(meal['in_stock'])}
                    </p>
                    <p style="margin: 0; color: #94A3B8; font-size: 12px; font-style: italic;">
                        <strong>Chef's Note:</strong> {meal['instructions']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        st.markdown("### 🛒 Gourmet Recipes (Missing 1–2 Ingredients)")
        st.caption("Elevated meal ideas requiring a small shopping top-up.")

        if not missing_meals:
            st.write(" *No recipe ideas found.*")
        else:
            for meal in missing_meals:
                missing_str = ", ".join(meal['missing'])
                st.markdown(f"""
                <div class="recipe-card recipe-card-missing">
                    <h3 style="color: #C5A059; margin: 0 0 8px 0;">{meal['title']}</h3>
                    <p style="margin: 0 0 6px 0; color: #E2E8F0; font-size: 13px;">
                        <strong>🥦 In Your Storage:</strong> {', '.join(meal['in_stock'])}
                    </p>
                    <p style="margin: 0 0 10px 0; color: #F59E0B; font-size: 13px; font-weight: 600;">
                        🛒 <strong>What You Need to Buy:</strong> {missing_str}
                    </p>
                    <p style="margin: 0; color: #94A3B8; font-size: 12px; font-style: italic;">
                        <strong>Chef's Note:</strong> {meal['instructions']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
