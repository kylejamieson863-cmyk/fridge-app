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

    /* Target ONLY Date Inputs to prevent mobile keyboard popup */
    div[data-testid="stDateInput"] input {
        inputmode: none !important;
        cursor: pointer !important;
    }

    /* Header */
    .ms-header {
        background: linear-gradient(135deg, #003B25 0%, #002417 100%);
        color: #FFFFFF;
        padding: 20px;
        text-align: center;
        border-bottom: 3px solid #C5A059;
        margin-bottom: 25px;
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

    /* Auth Forms & Cards */
    div[data-testid="stForm"] {
        border: 1px solid #C5A059 !important;
        border-radius: 12px !important;
        padding: 25px !important;
        background-color: #1E293B !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* Streamlit Tabs */
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

    /* Large Supermarket Touch Buttons */
    .stButton > button, form [data-testid="stFormSubmitButton"] > button {
        background-color: #003B25 !important;
        color: #FFFFFF !important;
        border: 1px solid #C5A059 !important;
        border-radius: 10px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        padding: 12px 18px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        width: 100%;
        min-height: 48px !important;
    }
    .stButton > button:hover, form [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #C5A059 !important;
        border-color: #C5A059 !important;
        color: #0F172A !important;
    }

    /* Pending Scan Supermarket Card */
    .scan-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #C5A059;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }

    /* ---------------------------------------------------------
       REALISTIC SMART FRIDGE GRAPHIC STYLING
    --------------------------------------------------------- */
    .fridge-container {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border: 8px solid #334155;
        border-radius: 20px;
        padding: 20px;
        box-shadow: inset 0 0 30px rgba(0, 240, 255, 0.05), 0 20px 40px rgba(0,0,0,0.6);
        position: relative;
    }

    .shelf-header-banner {
        background: linear-gradient(90deg, #003B25 0%, #005F3B 100%);
        color: #E2E8F0;
        border-left: 4px solid #C5A059;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .glass-shelf-line {
        height: 8px;
        background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.8), rgba(255,255,255,0.1));
        border-bottom: 3px solid #38BDF8;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        margin-top: 10px;
        margin-bottom: 25px;
    }

    div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%) !important;
        border: 1px solid #475569 !important;
        border-bottom: 3px solid #C5A059 !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
        font-weight: 600 !important;
        padding: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        text-align: left !important;
    }

    div[data-testid="stPopover"] > button:hover {
        border-color: #38BDF8 !important;
        transform: translateY(-2px);
    }

    .empty-shelf-msg {
        color: #64748B;
        font-size: 13px;
        font-style: italic;
        text-align: center;
        padding: 10px 0;
    }
</style>
"""
st.markdown(ms_css, unsafe_allow_html=True)

# Precision JavaScript: Only apply readonly to stDateInput elements
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
# 2. BRANDED HEADER & SUPABASE CLOUD CONNECTION
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
# 3. PROFESSIONAL SUPABASE AUTHENTICATION
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
# 5. NATIVE BARCODE SCANNER COMPONENT
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
# 6. HELPER FUNCTIONS
# ---------------------------------------------------------
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
                
                cat = "ready_meal"
                if any("meat" in c or "poultry" in c for c in categories):
                    cat = "meat"
                elif any("dairy" in c or "cheese" in c or "milk" in c or "yogurt" in c for c in categories):
                    cat = "dairy"
                elif any("vegetable" in c or "fruit" in c or "produce" in c or "grape" in c for c in categories):
                    cat = "produce"
                    
                return name, cat, nutrition
        except Exception:
            pass
            
    return f"Scanned Item ({barcode_str})", ("produce" if "0857" in str(barcode_str) else "ready_meal"), default_nutrition

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
                
            cat = "ready_meal"
            item_lower = cleaned_item.lower()
            if any(w in item_lower for w in ["chk", "chicken", "beef", "steak", "pork", "lamb", "bacon", "sausage", "meat", "mince", "salmon", "fish"]):
                cat = "meat"
            elif any(w in item_lower for w in ["milk", "cheese", "butter", "cream", "yogurt", "cheddar", "dip"]):
                cat = "dairy"
            elif any(w in item_lower for w in ["apple", "banana", "grape", "berry", "veg", "potato", "onion", "salad", "org", "fruit", "lemon"]):
                cat = "produce"
                
            extracted_items.append({"name": cleaned_item.title(), "category": cat})
            
        return extracted_items
    except Exception as e:
        st.error(f"Receipt Exception: {str(e)}")
        return []

def generate_smart_recipes(inventory):
    if not inventory:
        return "Your fridge is empty! Add items to generate recipe inspirations."
    
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
        
        # Intercept scanned code to trigger custom date modal
        if scanned_code:
            item_name, category, nutrition = lookup_barcode(scanned_code)
            st.session_state.pending_scanned_item = {
                "name": item_name,
                "category": category,
                "nutrition": nutrition
            }
            st.session_state.scan_target_date = datetime.today().date()
            st.rerun()

        # SUPERMARKET CUSTOM DATE SELECTION MODAL
        if st.session_state.pending_scanned_item:
            item = st.session_state.pending_scanned_item

            st.markdown(f"""
            <div class="scan-card">
                <h3 style="color: #C5A059; margin-top:0;">🛒 Item Scanned</h3>
                <h2 style="color: #FFFFFF; margin-bottom:10px;">{item['name']}</h2>
            </div>
            """, unsafe_allow_html=True)

            # Date Input and +30 Days Button Layout
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
                    # Microsecond timestamp ensures multiple scans of the same product get unique IDs
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
                    name, cat = manual_name, manual_cat
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

# --- TAB 2: CLEAN VISUAL FRIDGE INTERIOR ---
with tab2:
    st.markdown('<div class="fridge-container">', unsafe_allow_html=True)
    
    shelves = [
        ("🥛 TOP SHELF — Dairy & Prepared Items", ["dairy", "ready_meal"]),
        ("🥩 MIDDLE SHELF — Meat & Poultry", ["meat"]),
        ("🥗 CRISPER DRAWER — Fresh Produce", ["produce"])
    ]

    for title, cats in shelves:
        st.markdown(f'<div class="shelf-header-banner">{title}</div>', unsafe_allow_html=True)
        
        shelf_items = [item for item in active_inv if item.get("category") in cats]

        if not shelf_items:
            st.markdown('<div class="empty-shelf-msg">Shelf is currently empty</div>', unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for idx, item in enumerate(shelf_items):
                col = cols[idx % 2]
                with col:
                    portion_pct = int(item.get("portion", 1.0) * 100)
                    item_icon = "🥛" if item.get("category") == "dairy" else "🥩" if item.get("category") == "meat" else "🥗" if item.get("category") == "produce" else "📦"
                    label = f"{item_icon} {item['name']} ({portion_pct}%) — Exp: {item.get('expiry_date', 'N/A')}"

                    with st.popover(label, use_container_width=True):
                        st.markdown(f"### **{item['name']}**")
                        st.write(f"**Remaining Portion:** {portion_pct}%")
                        st.write(f"**Use-By Date:** {item.get('expiry_date', 'N/A')}")
                        
                        st.markdown("---")
                        st.markdown("**📊 Nutrition Info (per 100g):**")
                        nut = item.get("nutrition", {})
                        st.write(f"• **Calories:** {nut.get('calories', 'N/A')}")
                        st.write(f"• **Protein:** {nut.get('protein', 'N/A')}")
                        st.write(f"• **Carbs:** {nut.get('carbs', 'N/A')}")
                        st.write(f"• **Fat:** {nut.get('fat', 'N/A')}")
                        
                        st.markdown("---")
                        st.markdown("**🍽️ Log Usage:**")
                        p_col1, p_col2, p_col3 = st.columns(3)
                        
                        if p_col1.button("Used 1/4", key=f"quarter_{item['id']}"):
                            item["portion"] -= 0.25
                            if item["portion"] <= 0:
                                active_inv.remove(item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()
                            
                        if p_col2.button("Used 1/2", key=f"half_{item['id']}"):
                            item["portion"] -= 0.50
                            if item["portion"] <= 0:
                                active_inv.remove(item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()
                            
                        if p_col3.button("Finished", key=f"finish_{item['id']}"):
                            active_inv.remove(item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()

        st.markdown('<div class="glass-shelf-line"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if active_inv:
        st.divider()
        if st.button("🗑️ Clear Entire Fridge"):
            st.session_state.active_inv = []
            save_user_inventory(current_user_id, [])
            st.rerun()

# --- TAB 3: MEAL PLANNER ---
with tab3:
    if active_inv:
        if st.button("🍴 Generate Gourmet Recipe Ideas"):
            recipes = generate_smart_recipes(active_inv)
            st.markdown(recipes)
    else:
        st.warning("Add food items to your fridge before generating meal inspirations.")
