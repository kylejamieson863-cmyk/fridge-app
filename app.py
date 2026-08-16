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
    page_title="Smart Fridge | Food & Meal Planner",
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

    .fridge-container {
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
    
    .qty-badge {
        background-color: #C5A059;
        color: #0F172A;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 10px;
        font-size: 11px;
        margin-left: 6px;
    }

    /* Recipe Card Styling */
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
    .missing-tag {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid #F59E0B;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
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
    <div class="ms-brand">SMART FRIDGE</div>
    <div class="ms-subbrand">FOOD &bull; MEAL PLANNER</div>
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
                "portion": float(row["portion"]),
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
                    "portion": item["portion"],
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

# Top User Info Bar
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
# 6. ENHANCED HELPER FUNCTIONS & CATEGORY MATCHING
# ---------------------------------------------------------
def categorize_item(name_str, category_tags=[]):
    text = (name_str + " " + " ".join(category_tags)).lower()
    
    produce_keywords = ["potato", "potatoes", "onion", "onions", "grape", "grapes", "apple", "banana", "berry", 
                        "fruit", "veg", "vegetable", "salad", "produce", "pickle", "pickled", "lemon", "lime"]
    if any(w in text for w in produce_keywords):
        return "produce"
        
    meat_keywords = ["chicken", "chk", "beef", "steak", "pork", "lamb", "bacon", "sausage", "meat", 
                     "mince", "salmon", "fish", "burger", "burgers", "kebabs", "kebab", "poultry"]
    if any(w in text for w in meat_keywords):
        return "meat"
        
    dairy_keywords = ["milk", "cheese", "butter", "cream", "yogurt", "cheddar", "dip", "egg", "eggs", "lurpak", "spreadable"]
    if any(w in text for w in dairy_keywords):
        return "dairy"
        
    return "ready_meal"

def get_expiry_status(expiry_str):
    if not expiry_str:
        return "exp-green", "🟢"
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
                
                cat = categorize_item(name, categories)
                return name, cat, nutrition
        except Exception:
            pass
            
    return f"Scanned Item ({barcode_str})", categorize_item(str(barcode_str)), default_nutrition

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
                
            cat = categorize_item(cleaned_item)
            extracted_items.append({"name": cleaned_item.title(), "category": cat})
            
        return extracted_items
    except Exception as e:
        st.error(f"Receipt Exception: {str(e)}")
        return []

# ---------------------------------------------------------
# NEW CULINARY MEAL PLANNER ENGINE
# ---------------------------------------------------------
def analyze_fridge_for_meals(inventory):
    """Categorizes items and matches them against recipes & missing ingredient ideas."""
    if not inventory:
        return [], []

    # Sort items by expiration so earliest items are prioritized
    sorted_inv = sorted(inventory, key=lambda x: x.get("expiry_date", "9999-99-99"))
    
    # Names normalized
    item_names = [i["name"].strip().title() for i in sorted_inv]
    item_names_lower = [i.lower() for i in item_names]
    
    # Helper to check if ingredient is present
    def is_in_fridge(keyword):
        return any(keyword in name for name in item_names_lower)

    # Helper to get exact item display name
    def get_fridge_name(keyword):
        for name in item_names:
            if keyword in name.lower():
                return name
        return keyword.title()

    ready_meals = []
    missing_meals = []

    # Check for direct ready meals / pre-made dishes first
    for item in sorted_inv:
        cat = item.get("category")
        name = item.get("name")
        if cat == "ready_meal" or any(w in name.lower() for w in ["bolognese", "kebab", "burger", "curry", "pasta", "pizza"]):
            ready_meals.append({
                "title": f"Ready-to-Heat: {name}",
                "in_stock": [name],
                "missing": [],
                "instructions": "Pre-prepared meal. Reheat thoroughly according to package instructions until piping hot."
            })

    # Recipe Database with intelligent ingredient matching
    RECIPE_DATABASE = [
        {
            "title": "Gourmet Lamb Kebabs with Minted Salad & Dip",
            "required": ["kebab", "lamb"],
            "optional": [
                {"keys": ["dip", "sauce", "yogurt"], "name": "Fresh Dip/Yogurt"},
                {"keys": ["salad", "grape", "fruit", "lemon"], "name": "Side Salad/Garnish"},
                {"keys": ["pita", "bread", "wrap"], "name": "Flatbread or Pita"}
            ],
            "instructions": "Grill or pan-fry the lamb kebabs until charred and cooked through. Serve alongside fresh dip and a crisp side salad."
        },
        {
            "title": "Classic Spaghetti Bolognese Feast",
            "required": ["bolognese", "spaghetti"],
            "optional": [
                {"keys": ["cheese", "cheddar", "parmesan"], "name": "Grated Cheese"},
                {"keys": ["bread", "garlic"], "name": "Garlic Bread"}
            ],
            "instructions": "Heat the bolognese sauce gently. Toss with freshly cooked pasta and top generously with grated cheese."
        },
        {
            "title": "Loaded Gourmet Smash Burgers",
            "required": ["burger", "burgers"],
            "optional": [
                {"keys": ["cheese", "cheddar"], "name": "Burger Cheese Slices"},
                {"keys": ["bun", "bread", "roll"], "name": "Brioche Buns"},
                {"keys": ["pickle", "onion", "salad"], "name": "Pickles or Sliced Onion"}
            ],
            "instructions": "Sear smash patties on a high-heat griddle for crispy edges. Melt cheese on top and serve in toasted buns with pickles."
        },
        {
            "title": "Pan-Seared Protein & Potato Skillet",
            "required": ["potato", "potatoes"],
            "optional": [
                {"keys": ["chicken", "steak", "pork", "sausage", "bacon", "lamb"], "name": "Protein Choice (Chicken/Steak/Sausages)"},
                {"keys": ["butter", "oil"], "name": "Butter or Herbs"},
                {"keys": ["onion", "veg"], "name": "Sautéed Veggies"}
            ],
            "instructions": "Parboil potatoes, then crisp them in a pan with butter. Pair with seared protein and sautéed vegetables."
        },
        {
            "title": "High-Protein Greek Yogurt Parfait",
            "required": ["yogurt"],
            "optional": [
                {"keys": ["grape", "grapes", "berry", "fruit", "apple"], "name": "Fresh Fruit/Grapes"},
                {"keys": ["honey", "oats", "granola"], "name": "Honey or Granola"}
            ],
            "instructions": "Layer thick Greek yogurt in a bowl with fresh fruit and top with a drizzle of honey or crisp granola."
        },
        {
            "title": "Rich Chocolate Cookie Dough Dessert Bowl",
            "required": ["cookie dough", "dough", "chocolate"],
            "optional": [
                {"keys": ["cream", "ice cream", "milk"], "name": "Fresh Cream or Ice Cream"},
                {"keys": ["berry", "fruit"], "name": "Fresh Berries"}
            ],
            "instructions": "Bake or warm the cookie dough until gooey in the center. Serve warm with cream or fresh berries."
        }
    ]

    for recipe in RECIPE_DATABASE:
        # Check required primary ingredients
        has_req = False
        matched_req_name = ""
        for req in recipe["required"]:
            if is_in_fridge(req):
                has_req = True
                matched_req_name = get_fridge_name(req)
                break

        if has_req:
            in_stock = [matched_req_name]
            missing = []

            for opt in recipe["optional"]:
                found_opt = False
                for key in opt["keys"]:
                    if is_in_fridge(key):
                        in_stock.append(get_fridge_name(key))
                        found_opt = True
                        break
                if not found_opt:
                    missing.append(opt["name"])

            meal_data = {
                "title": recipe["title"],
                "in_stock": in_stock,
                "missing": missing,
                "instructions": recipe["instructions"]
            }

            if not missing:
                ready_meals.append(meal_data)
            else:
                missing_meals.append(meal_data)

    return ready_meals, missing_meals

# ---------------------------------------------------------
# 7. MAIN INTERFACE
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🛒 Trolley Scanner", "🧊 Fridge Interior", "🍴 Gourmet Meal Planner"])

# --- TAB 1: SCANNING & RECEIPT ---
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Barcode Scanner")
        st.caption("Scan items directly in the aisle")
        
        scanned_code = barcode_scanner(key="live_barcode_reader")
        
        if scanned_code:
            item_name, category, nutrition = lookup_barcode(scanned_code)
            st.session_state.pending_scanned_item = {
                "name": item_name,
                "category": category,
                "nutrition": nutrition
            }
            st.session_state.scan_target_date = datetime.today().date()
            st.rerun()

        if st.session_state.pending_scanned_item:
            item = st.session_state.pending_scanned_item

            st.markdown(f"""
            <div class="scan-card">
                <h3 style="color: #C5A059; margin-top:0;">🛒 Item Scanned</h3>
                <h2 style="color: #FFFFFF; margin-bottom:10px;">{item['name']}</h2>
            </div>
            """, unsafe_allow_html=True)

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

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("✅ Confirm & Save"):
                    unique_id = datetime.now().timestamp() + (time.time() % 1)
                    active_inv.append({
                        "id": unique_id,
                        "name": item["name"],
                        "category": item["category"],
                        "portion": 1.0,
                        "nutrition": item["nutrition"],
                        "expiry_date": st.session_state.scan_target_date.strftime("%Y-%m-%d")
                    })
                    save_user_inventory(current_user_id, active_inv)
                    st.session_state.pending_scanned_item = None
                    st.session_state.scan_target_date = datetime.today().date()
                    st.toast(f"✨ Added to Fridge: **{item['name']}**", icon="🛒")
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
        
        if st.button("Add Item to Fridge"):
            if manual_name:
                if manual_name.isdigit():
                    name, cat, nutrition = lookup_barcode(manual_name)
                else:
                    name = manual_name
                    cat = categorize_item(manual_name) if manual_cat == "ready_meal" else manual_cat
                    nutrition = {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fat": "N/A"}
                
                unique_id = datetime.now().timestamp() + (time.time() % 1)
                active_inv.append({
                    "id": unique_id,
                    "name": name,
                    "category": cat,
                    "portion": 1.0,
                    "nutrition": nutrition,
                    "expiry_date": st.session_state.manual_target_date.strftime("%Y-%m-%d")
                })
                save_user_inventory(current_user_id, active_inv)
                st.session_state.manual_target_date = datetime.today().date()
                st.success(f"Added: **{name}**")
                st.rerun()

    with col2:
        st.subheader("2. Receipt OCR Photo Scanner")
        st.caption("Snap a photo of your receipt")
        
        receipt_photo = st.file_uploader("Upload Receipt Image:", type=["jpg", "png", "jpeg"], key="receipt_upload")
        receipt_date = st.date_input("Use-By Date for Receipt Items:", datetime.today(), key="receipt_exp_date")
        
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
                        active_inv.append({
                            "id": unique_id,
                            "name": str(item["name"]),
                            "category": str(item["category"]),
                            "portion": 1.0,
                            "nutrition": {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fat": "N/A"},
                            "expiry_date": receipt_date.strftime("%Y-%m-%d")
                        })
                    save_user_inventory(current_user_id, active_inv)
                    st.session_state.staged_receipt_items = []
                    st.success("Saved items to Fridge!")
                    st.rerun()
            with col_b:
                if st.button("❌ Discard Receipt"):
                    st.session_state.staged_receipt_items = []
                    st.rerun()

# --- TAB 2: VISUAL FRIDGE INTERIOR ---
with tab2:
    st.markdown("""
    <div style="display: flex; gap: 15px; margin-bottom: 12px; font-size: 12px; justify-content: center; background: #1E293B; padding: 8px; border-radius: 8px; border: 1px solid #334155;">
        <span>🔴 Today/Tomorrow (&le; 1 day)</span>
        <span>🟠 2–3 Days</span>
        <span>🟢 Safe (&ge; 4 Days)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fridge-container">', unsafe_allow_html=True)
    
    shelves = [
        ("🥛 TOP SHELF — Dairy, Drinks & Prepared Items", ["dairy", "ready_meal"]),
        ("🥩 MIDDLE SHELF — Meat & Poultry", ["meat"]),
        ("🥗 CRISPER DRAWER — Fresh Produce", ["produce"])
    ]

    for title, cats in shelves:
        shelf_raw_items = [item for item in active_inv if item.get("category") in cats or (cats[0] == "ready_meal" and item.get("category") not in ["meat", "produce"])]
        
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
                color_class, status_emoji = get_expiry_status(exp_date)
                
                label = f"{status_emoji} {name} (x{qty}) — Exp: {exp_date}" if qty > 1 else f"{status_emoji} {name} — Exp: {exp_date}"

                col = cols[idx % 2]
                with col:
                    st.markdown(f'<div class="{color_class}">', unsafe_allow_html=True)
                    with st.popover(label, use_container_width=True):
                        st.markdown(f"### **{status_emoji} {name}**")
                        st.write(f"**Total Quantity in Stack:** {qty}")
                        st.write(f"**Use-By Date:** {exp_date}")
                        
                        st.markdown("---")
                        st.markdown("**📊 Nutrition Info (per 100g):**")
                        nut = first_item.get("nutrition", {})
                        st.write(f"• **Calories:** {nut.get('calories', 'N/A')}")
                        st.write(f"• **Protein:** {nut.get('protein', 'N/A')}")
                        st.write(f"• **Carbs:** {nut.get('carbs', 'N/A')}")
                        st.write(f"• **Fat:** {nut.get('fat', 'N/A')}")
                        
                        st.markdown("---")
                        st.markdown("**🍽️ Log Usage / Consume:**")
                        
                        btn_col1, btn_col2 = st.columns(2)
                        if btn_col1.button(f"Consume 1 Unit", key=f"use_one_{first_item['id']}"):
                            active_inv.remove(first_item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()
                            
                        if btn_col2.button(f"Clear All ({qty})", key=f"clear_all_{first_item['id']}"):
                            for itm in item_group:
                                active_inv.remove(itm)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()
                            
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-shelf-line"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if active_inv:
        st.divider()
        if st.button("🗑️ Clear Entire Fridge"):
            st.session_state.active_inv = []
            save_user_inventory(current_user_id, [])
            st.rerun()

# --- TAB 3: SMART GOURMET MEAL PLANNER ---
with tab3:
    st.subheader("🍴 Gourmet Meal Suggestions")
    st.caption("Matches your current fridge inventory with complete meals & missing ingredient ideas.")

    if not active_inv:
        st.info("Your fridge is empty! Add items using the scanner or manual lookup to view meal ideas.")
    else:
        ready_meals, missing_meals = analyze_fridge_for_meals(active_inv)

        # 1. MEALS YOU CAN MAKE RIGHT NOW
        st.markdown("### ✅ Meals You Can Make Right Now")
        st.caption("Made 100% with ingredients currently in your fridge.")

        if not ready_meals:
            st.write(" *No complete single-dish meals available with current items alone.*")
        else:
            for idx, meal in enumerate(ready_meals):
                st.markdown(f"""
                <div class="recipe-card recipe-card-ready">
                    <h3 style="color: #10B981; margin: 0 0 8px 0;">{meal['title']}</h3>
                    <p style="margin: 0 0 8px 0; color: #E2E8F0; font-size: 13px;">
                        <strong>🥦 In Your Fridge:</strong> {', '.join(meal['in_stock'])}
                    </p>
                    <p style="margin: 0; color: #94A3B8; font-size: 12px; font-style: italic;">
                        <strong>Chef's Note:</strong> {meal['instructions']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # 2. MEALS YOU CAN MAKE IF YOU BUY A FEW INGREDIENTS
        st.markdown("### 🛒 Meals You Can Make (Missing 1–2 Ingredients)")
        st.caption("Great meal ideas requiring just a quick top-up run.")

        if not missing_meals:
            st.write(" *No missing ingredient meal suggestions available.*")
        else:
            for idx, meal in enumerate(missing_meals):
                missing_str = ", ".join(meal['missing'])
                st.markdown(f"""
                <div class="recipe-card recipe-card-missing">
                    <h3 style="color: #C5A059; margin: 0 0 8px 0;">{meal['title']}</h3>
                    <p style="margin: 0 0 6px 0; color: #E2E8F0; font-size: 13px;">
                        <strong>🥦 In Your Fridge:</strong> {', '.join(meal['in_stock'])}
                    </p>
                    <p style="margin: 0 0 10px 0; color: #F59E0B; font-size: 13px; font-weight: 600;">
                        🛒 <strong>What You Need to Buy:</strong> {missing_str}
                    </p>
                    <p style="margin: 0; color: #94A3B8; font-size: 12px; font-style: italic;">
                        <strong>Chef's Note:</strong> {meal['instructions']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
