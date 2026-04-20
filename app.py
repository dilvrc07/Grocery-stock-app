import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from streamlit_lottie import st_lottie
import json

# ---------------- CONFIG & STYLING ----------------
st.set_page_config(page_title="Grocery Stock Manager", page_icon="🛒", layout="wide")

st.markdown("""
<style>
    /* Premium font and clean background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean up the header and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Enhance inputs and buttons */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 8px !important;
    }
    
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- TWILIO DETAILS ----------------
ACCOUNT_SID = "AC1d50b24f9c09875ea85105bc196afbd8"
AUTH_TOKEN = "c5630078cbf72cd003be296bb46f7a5b"
TWILIO_NUMBER = "+19133996249"

# ---------------- FILES ----------------
USERS_FILE = "users.csv"
STOCK_FILE = "stock.csv"

def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username","password","phone"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(STOCK_FILE):
        pd.DataFrame(columns=["barcode","name","quantity","expiry"]).to_csv(STOCK_FILE, index=False)

init_files()

# ---------------- LOTTIE FUNCTION ----------------
@st.cache_data
def load_lottiefile(filepath: str):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as f:
            return json.load(f)
    return None

# Load local lottie files instead of from network
lottie_login = load_lottiefile("login.json.json")
lottie_add_stock = load_lottiefile("add_stock.json.json")
lottie_view_stock = load_lottiefile("view_stock.json.json")
lottie_expiry = load_lottiefile("expiry.json.json")
lottie_success = load_lottiefile("success.json.json")

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""

# ---------------- LOGIN PAGE ----------------
def login_page():
    # Centered login box using columns
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if lottie_login:
            st_lottie(lottie_login, height=220, key="login_anim")
        st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Welcome Back</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray; margin-bottom: 2rem;'>Please login to your account</p>", unsafe_allow_html=True)
        
        users_df = pd.read_csv(USERS_FILE)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                # Basic Auth
                user = users_df[
                    (users_df["username"].astype(str).str.strip().str.lower() == username.strip().lower()) &
                    (users_df["password"].astype(str).str.strip() == password.strip())
                ]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_phone = str(user.iloc[0]["phone"]).strip()
                    st.rerun()
                else:
                    st.error("Invalid username or password ❌")

# ---------------- MAIN APP ----------------
def main_app():
    stock_df = pd.read_csv(STOCK_FILE)
    stock_df["barcode"] = stock_df["barcode"].astype(str)

    # --- Sidebar Navigation ---
    st.sidebar.markdown(f"### 👤 Profile")
    st.sidebar.info(f"Connected Phone: {st.session_state.user_phone}")
    
    st.sidebar.markdown("### 📌 Navigation")
    menu = st.sidebar.radio("Select an option", [
        "📦 View Stock", 
        "➕ Add Stock", 
        "🔍 Search by Barcode", 
        "✏️ Manage Items", 
        "⏳ Check Expiry"
    ], label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_phone = ""
        st.rerun()

    # --- Dashboard Header ---
    st.title("🛒 Grocery Stock Management")
    st.markdown("---")

    # ----- VIEW STOCK -----
    if menu == "📦 View Stock":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📋 Current Inventory")
            st.dataframe(stock_df, use_container_width=True, hide_index=True)
        with col2:
            if lottie_view_stock:
                st_lottie(lottie_view_stock, height=200, key="view_anim")
            
            st.metric("Total Unique Items", len(stock_df))
            if not stock_df.empty:
                st.metric("Total Stock Quantity", stock_df["quantity"].sum())

    # ----- ADD STOCK -----
    elif menu == "➕ Add Stock":
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.subheader("Add New Item")
            with st.form("add_stock_form", clear_on_submit=True):
                barcode = st.text_input("Barcode")
                name = st.text_input("Item Name")
                quantity = st.number_input("Quantity", min_value=1)
                expiry = st.date_input("Expiry Date")
                submitted = st.form_submit_button("➕ Add Item", use_container_width=True)
                
                if submitted:
                    if not barcode or not name:
                        st.error("Please fill all required fields.")
                    else:
                        new_row = pd.DataFrame([{
                            "barcode": barcode.strip(), 
                            "name": name.strip(), 
                            "quantity": quantity, 
                            "expiry": expiry
                        }])
                        stock_df = pd.concat([stock_df, new_row], ignore_index=True)
                        stock_df.to_csv(STOCK_FILE, index=False)
                        st.success(f"'{name}' added successfully! ✅")
                        if lottie_success:
                            st_lottie(lottie_success, height=100, key="success_anim")
        with col2:
            if lottie_add_stock:
                st_lottie(lottie_add_stock, height=300, key="add_anim")

    # ----- SEARCH BY BARCODE -----
    elif menu == "🔍 Search by Barcode":
        st.subheader("Search Inventory")
        search_barcode = st.text_input("Enter Barcode", placeholder="Scan or type barcode...")
        
        if search_barcode:
            result = stock_df[stock_df["barcode"] == search_barcode.strip()]
            if result.empty:
                st.warning("No item found with this barcode ❌")
            else:
                st.success("Item Found! ✅")
                st.dataframe(result, use_container_width=True, hide_index=True)

    # ----- UPDATE / DELETE -----
    elif menu == "✏️ Manage Items":
        st.subheader("Update or Delete Item")
        barcode_input = st.text_input("Enter Barcode to Manage", placeholder="Scan or type barcode...")
        
        if barcode_input:
            item = stock_df[stock_df["barcode"] == barcode_input.strip()]
            if not item.empty:
                st.markdown("### Item Details")
                
                idx = item.index[0]
                name_val = item.loc[idx, "name"]
                quantity_val = int(item.loc[idx, "quantity"])
                
                try:
                    expiry_val = pd.to_datetime(item.loc[idx, "expiry"]).date()
                except:
                    expiry_val = datetime.now().date()
                
                with st.expander("Edit Item", expanded=True):
                    new_name = st.text_input("Name", name_val)
                    new_quantity = st.number_input("Quantity", min_value=1, value=quantity_val)
                    new_expiry = st.date_input("Expiry", expiry_val)
                    
                    c1, c2 = st.columns(2)
                    if c1.button("💾 Update Item", use_container_width=True):
                        stock_df.loc[idx, ["name","quantity","expiry"]] = [new_name, new_quantity, new_expiry]
                        stock_df.to_csv(STOCK_FILE, index=False)
                        st.success("Item updated successfully! ✅")
                        st.rerun()
                        
                    if c2.button("🗑️ Delete Item", type="primary", use_container_width=True):
                        stock_df = stock_df.drop(idx)
                        stock_df.to_csv(STOCK_FILE, index=False)
                        st.success("Item deleted successfully! ✅")
                        st.rerun()
            else:
                st.warning("Barcode not found ❌")

    # ----- EXPIRY CHECK + SMS -----
    elif menu == "⏳ Check Expiry":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Expiry Alerts")
            stock_df["expiry"] = pd.to_datetime(stock_df["expiry"])
            today = datetime.now()
            alert_date = today + timedelta(days=3)
            
            expiring = stock_df[stock_df["expiry"] <= alert_date]
            
            if expiring.empty:
                st.info("All items are fresh! No items expiring soon. ✅")
            else:
                st.error(f"⚠️ {len(expiring)} Items expiring within 3 days:")
                
                # Format dataframe for display
                display_df = expiring.copy()
                display_df['expiry'] = display_df['expiry'].dt.strftime('%Y-%m-%d')
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                if st.button("📱 Send SMS Alert to Manager", use_container_width=True):
                    with st.spinner("Sending SMS..."):
                        message_text = "🚨 Grocery Stock Alert!\nThese items are expiring soon:\n"
                        for i in expiring.itertuples():
                            message_text += f"- {i.name} (Exp: {i.expiry.date()})\n"
                        try:
                            client = Client(ACCOUNT_SID, AUTH_TOKEN)
                            message = client.messages.create(
                                body=message_text,
                                from_=TWILIO_NUMBER,
                                to=st.session_state.user_phone
                            )
                            st.success(f"SMS Alert sent successfully to {st.session_state.user_phone}! ✅")
                        except Exception as e:
                            st.error(f"Failed to send SMS ❌: {e}")

        with col2:
            if lottie_expiry:
                st_lottie(lottie_expiry, height=200, key="expiry_anim")

# ---------------- ROUTER ----------------
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()