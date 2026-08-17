import streamlit as st
import requests
import json
import os
import time
from datetime import datetime, date

# ==========================================
# 1. DATABASE / STORAGE HELPERS
# ==========================================
DATA_FILE = "pantry_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_inventory(user_id, inventory):
    data = load_data()
    data[user_id] = inventory
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_inventory(user_id):
    data = load_data()
    return data.get(user_id, [])

# ==========================================
# 2. ENHANCED BARCODE & CATEGORIZATION LOGIC
# ==========================================
def determine_storage_and_category(name_str, category_tags=[]):
    """Determines storage location (fridge/freezer/cupboard) and food category."""
    text = (name_str + " " + " ".join(category_tags)).lower()

    # Determine Storage Location
    frozen_keywords = ["frozen", "ice cream", "freezer", "deep freeze"]
    cupboard_keywords = ["canned", "tin", "tinned", "dry", "pasta", "rice", "flour", "sugar", "sauce", "spices", "cereal", "ambient"]

    if any(w in text for w in frozen_keywords):
        storage = "freezer"
    elif any(w in text for w in cupboard_keywords):
        storage = "cupboard"
    else:
        storage = "fridge" # Default

    # Determine Food Category
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

    return storage, category

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

                storage, cat = determine_storage_and_category(name, categories)
                return name, storage, cat, nutrition
        except Exception:
            pass

    storage, cat = determine_storage_and_category(str(barcode_str))
    return f"Scanned Item ({barcode_str})", storage, cat, default_nutrition

# ==========================================
# 3. MAIN APP ROUTING & INTERFACE
# ==========================================
st.set_page_config(page_title="Smart Food & Pantry Tracker", page_icon="📦", layout="wide")

current_user_id = st.sidebar.text_input("User Account ID", value="default_user")
active_inv = get_user_inventory(current_user_id)

st.title("📦 Smart Pantry & Consumption Tracker")

tab1, tab2, tab3 = st.tabs(["➕ Add Items", "📊 Inventory Tracker", "⚙️ Quick Tools"])

# --- TAB 1: ADD ITEMS ---
with tab1:
    st.subheader("Add Product to Inventory")
    
    add_type = st.radio("Input Type", ["Barcode Lookup", "Manual Entry"], horizontal=True)
    
    if add_type == "Barcode Lookup":
        bc = st.text_input("Enter or Scan Barcode")
        if st.button("Lookup & Add"):
            if bc:
                name, storage, category, nutrition = lookup_barcode(bc)
                exp = "No Expiry" if storage != "fridge" else date.today().strftime("%Y-%m-%d")
                
                new_item = {
                    "id": time.time(),
                    "name": name,
                    "storage": storage,
                    "category": category,
                    "portion": 1.0,
                    "nutrition": nutrition,
                    "expiry_date": exp
                }
                active_inv.append(new_item)
                save_user_inventory(current_user_id, active_inv)
                st.success(f"Added {name} to {storage.title()}!")
                st.rerun()
    else:
        with st.form("manual_add"):
            name = st.text_input("Item Name")
            storage = st.selectbox("Storage Location", ["fridge", "freezer", "cupboard"])
            category = st.selectbox("Category", ["produce", "meat", "dairy", "ready_meal"])
            exp_date = st.date_input("Expiry Date") if storage == "fridge" else None
            
            submitted = st.form_submit_button("Add Item")
            if submitted and name:
                new_item = {
                    "id": time.time(),
                    "name": name,
                    "storage": storage,
                    "category": category,
                    "portion": 1.0,
                    "nutrition": {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fat": "N/A"},
                    "expiry_date": exp_date.strftime("%Y-%m-%d") if exp_date else "No Expiry"
                }
                active_inv.append(new_item)
                save_user_inventory(current_user_id, active_inv)
                st.success(f"Added {name} to {storage.title()}!")
                st.rerun()

# --- TAB 2: INVENTORY & CONSUMPTION ---
with tab2:
    st.subheader("Current Inventory Management")
    
    selected_storage = st.radio("Filter Location", ["All", "Fridge", "Freezer", "Cupboard"], horizontal=True)
    
    filtered_inv = active_inv
    if selected_storage != "All":
        filtered_inv = [i for i in active_inv if i.get("storage", "fridge").lower() == selected_storage.lower()]

    if not filtered_inv:
        st.info("No items found in this section.")
    else:
        # Group items by name to show consolidated quantities
        grouped_items = {}
        for item in filtered_inv:
            grouped_items.setdefault(item["name"], []).append(item)

        cols = st.columns(3)
        for idx, (name, item_group) in enumerate(grouped_items.items()):
            first_item = item_group[0]
            qty = len(item_group)
            
            # Status Indicator
            if first_item.get("storage") == "fridge" and first_item.get("expiry_date") != "No Expiry":
                status_emoji = "🟢"
            else:
                status_emoji = "❄️" if first_item.get("storage") == "freezer" else "📦"

            label = f"{status_emoji} {name} (x{qty})"
            
            with cols[idx % 3]:
                with st.popover(label, use_container_width=True):
                    st.markdown(f"### **{status_emoji} {name}**")
                    st.caption(f"Storage: **{first_item.get('storage', 'fridge').upper()}**")
                    
                    st.markdown("**📊 Nutrition Info (per 100g):**")
                    nut = first_item.get("nutrition", {})
                    st.write(f"• **Calories:** {nut.get('calories', 'N/A')} | **Protein:** {nut.get('protein', 'N/A')}")
                    st.write(f"• **Carbs:** {nut.get('carbs', 'N/A')} | **Fat:** {nut.get('fat', 'N/A')}")
                    
                    st.markdown("---")
                    st.markdown("**⚙️ Quick Actions:**")
                    
                    # Action Row 1: Quantity Stepper
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        if st.button("➖", key=f"dec_{first_item['id']}"):
                            active_inv.remove(first_item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()
                    with c2:
                        st.markdown(f"<h4 style='text-align: center; margin:0;'>Qty: {qty}</h4>", unsafe_allow_html=True)
                    with c3:
                        if st.button("➕", key=f"inc_{first_item['id']}"):
                            new_item = first_item.copy()
                            new_item["id"] = time.time()
                            active_inv.append(new_item)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()

                    # Action Row 2: Transfer & Removal Actions
                    st.write("&nbsp;")
                    a1, a2 = st.columns(2)
                    
                    if first_item.get("storage") != "freezer":
                        with a1:
                            if st.button("❄️ Move to Freezer", key=f"freeze_{first_item['id']}"):
                                for itm in item_group:
                                    itm["storage"] = "freezer"
                                    itm["expiry_date"] = "No Expiry"
                                save_user_inventory(current_user_id, active_inv)
                                st.toast(f"Moved {name} to Freezer!", icon="❄️")
                                st.rerun()
                                
                    with a2:
                        if st.button("🗑️ Remove All", key=f"clear_all_{first_item['id']}"):
                            for itm in item_group:
                                active_inv.remove(itm)
                            save_user_inventory(current_user_id, active_inv)
                            st.rerun()

# --- TAB 3: TOOLS ---
with tab3:
    st.subheader("Data Management")
    if st.button("Clear Entire Inventory"):
        save_user_inventory(current_user_id, [])
        st.warning("Inventory cleared.")
        st.rerun()
