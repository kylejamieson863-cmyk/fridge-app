import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Smart Fridge Tracker", page_icon="🥦", layout="wide")

# ---------------------------------------------------------
# Supabase Database Connection
# ---------------------------------------------------------
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ---------------------------------------------------------
# Database Helper Functions
# ---------------------------------------------------------
def load_user_inventory(username):
    """Fetch stored fridge items for a specific user from Supabase."""
    try:
        response = supabase.table("fridge_inventory").select("*").eq("username", username).execute()
        rows = response.data
        if not rows:
            return []
        
        inventory = []
        for row in rows:
            inventory.append({
                "id": float(row["item_id"]),
                "name": str(row["name"]),
                "category": str(row["category"]),
                "portion": float(row["portion"]),
                "nutrition": {
                    "calories": str(row["calories"]),
                    "protein": str(row["protein"]),
                    "carbs": str(row["carbs"]),
                    "fat": str(row["fat"])
                },
                "expiry_date": str(row["expiry_date"])
            })
        return inventory
    except Exception as e:
        st.error(f"Error loading inventory from cloud: {e}")
        return []

def save_user_inventory(username, inventory):
    """Sync current user inventory to Supabase."""
    try:
        # Clear existing items for this user to keep database in sync
        supabase.table("fridge_inventory").delete().eq("username", username).execute()
        
        # Insert current inventory items
        if inventory:
            new_rows = []
            for item in inventory:
                nut = item.get("nutrition", {})
                new_rows.append({
                    "username": username,
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
        st.error(f"Error saving inventory to cloud: {e}")

# ---------------------------------------------------------
# User Session Management
# ---------------------------------------------------------
if "username" not in st.session_state:
    st.session_state.username = ""

st.sidebar.title("👤 User Switcher")
username_input = st.sidebar.text_input("Enter Username:", value=st.session_state.username)

if username_input != st.session_state.username:
    st.session_state.username = username_input
    st.session_state.inventory_loaded = False

if not st.session_state.username:
    st.warning("Please enter a username in the sidebar to load your fridge inventory.")
    st.stop()

# Load inventory from Supabase once when user logs in or switches username
if not st.session_state.get("inventory_loaded", False):
    st.session_state.inventory = load_user_inventory(st.session_state.username)
    st.session_state.inventory_loaded = True

# ---------------------------------------------------------
# Main App Interface
# ---------------------------------------------------------
st.title(f"🥦 Smart Fridge — {st.session_state.username.capitalize()}'s Inventory")

# Add New Item Section
with st.expander("➕ Add New Item to Fridge", expanded=False):
    with st.form("add_item_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            item_name = st.text_input("Item Name")
            item_category = st.selectbox("Category", ["Dairy", "Produce", "Meat & Seafood", "Bakery", "Beverages", "Condiments", "Other"])
        with col2:
            item_portion = st.number_input("Portion / Quantity", min_value=0.1, value=1.0, step=0.5)
            expiry = st.date_input("Expiry Date", date.today())
        with col3:
            st.markdown("**Nutrition Details**")
            cal = st.text_input("Calories", "N/A")
            protein = st.text_input("Protein (g)", "N/A")
            carbs = st.text_input("Carbs (g)", "N/A")
            fat = st.text_input("Fat (g)", "N/A")

        submitted = st.form_submit_button("Save Item")
        if submitted and item_name:
            new_item = {
                "id": datetime.now().timestamp(),
                "name": item_name,
                "category": item_category,
                "portion": item_portion,
                "nutrition": {
                    "calories": cal,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat
                },
                "expiry_date": str(expiry)
            }
            st.session_state.inventory.append(new_item)
            save_user_inventory(st.session_state.username, st.session_state.inventory)
            st.success(f"Added {item_name} to your fridge!")
            st.rerun()

# Display Inventory Section
st.subheader("📋 Current Fridge Contents")

if not st.session_state.inventory:
    st.info("Your fridge is empty. Add an item above to get started!")
else:
    for idx, item in enumerate(st.session_state.inventory):
        col_item, col_qty, col_exp, col_action = st.columns([3, 2, 2, 1])
        with col_item:
            st.markdown(f"**{item['name']}** ({item['category']})")
            nut = item.get("nutrition", {})
            st.caption(f"Calories: {nut.get('calories', 'N/A')} | P: {nut.get('protein', 'N/A')} | C: {nut.get('carbs', 'N/A')} | F: {nut.get('fat', 'N/A')}")
        with col_qty:
            st.write(f"Qty: {item['portion']}")
        with col_exp:
            st.write(f"Expires: {item['expiry_date']}")
        with col_action:
            if st.button("❌ Delete", key=f"del_{idx}"):
                st.session_state.inventory.pop(idx)
                save_user_inventory(st.session_state.username, st.session_state.inventory)
                st.success("Item removed!")
                st.rerun()

st.divider()
st.caption("🔒 All inventory data is saved securely to your Supabase cloud backend.")
