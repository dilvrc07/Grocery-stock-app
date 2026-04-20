import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from streamlit_lottie import st_lottie
import json
import hashlib
import time

# ---------------- CONFIG & STYLING ----------------
st.set_page_config(page_title="Grocery Stock Manager Pro", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
    /* Premium Font & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Clean up standard Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden; display: none !important;}
    
    /* Reduce Top Whitespace */
    div.block-container {
        padding-top: 1.2rem !important;
    }
    
    /* Aggressively Reduce Sidebar Top Whitespace */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebarNav"] {
        padding-top: 0rem !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 0rem !important;
    }
    
    /* Premium Input Styling */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 10px !important;
        border: 1px solid #d1d5db !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        padding: 12px 14px !important;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
    }
    
    /* Premium Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 15px rgba(79, 70, 229, 0.3) !important;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 600 !important;
        color: #4F46E5 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: #6B7280 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SECURITY FUNCTIONS ----------------
def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def secure_auth(username, password, users_df):
    """Validates user securely. Auto-upgrades plaintext passwords to hashed versions."""
    username_match = users_df["username"].astype(str).str.strip().str.lower() == username.strip().lower()
    user_rows = users_df[username_match]
    
    if user_rows.empty:
        return False, users_df
        
    db_password = str(user_rows.iloc[0]["password"]).strip()
    idx = user_rows.index[0]
    
    # Check if DB password is a hash (64 chars for SHA-256)
    if len(db_password) == 64:
        if hash_password(password) == db_password:
            return True, users_df
    else:
        # Plaintext fallback for legacy accounts, auto-upgrade to hash!
        if password.strip() == db_password:
            users_df.loc[idx, "password"] = hash_password(password.strip())
            users_df.to_csv(USERS_FILE, index=False)
            return True, users_df
            
    return False, users_df

# ---------------- TWILIO DETAILS ----------------
# Security Note: Moving to st.secrets() is advised for production!
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

lottie_login = load_lottiefile("login.json.json")
lottie_add_stock = load_lottiefile("add_stock.json.json")
lottie_expiry = load_lottiefile("expiry.json.json")

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN PAGE ----------------
def login_page():
    # Centered modern login box
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if lottie_login:
            st_lottie(lottie_login, height=220, key="login_anim")
        
        st.markdown("<h1 style='text-align: center; color: #1f2937; margin-bottom: 0;'>Secure Login</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 2rem; font-size: 1.1rem;'>Grocery Stock Manager Pro</p>", unsafe_allow_html=True)
        
        with st.container(border=True): # New Streamlit container border feature
            users_df = pd.read_csv(USERS_FILE, dtype=str)
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In 🔐", use_container_width=True)
                
                if submitted:
                    success, updated_users_df = secure_auth(username, password, users_df)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username.strip().title()
                        idx = updated_users_df[updated_users_df["username"].str.lower() == username.strip().lower()].index[0]
                        st.session_state.user_phone = str(updated_users_df.loc[idx, "phone"]).strip()
                        st.toast(f"Welcome back, {st.session_state.username}! 👋", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid username or password. ❌")

# ---------------- MAIN APP ----------------
def main_app():
    stock_df = pd.read_csv(STOCK_FILE)
    stock_df["barcode"] = stock_df["barcode"].astype(str)
    
    # Normalize data
    stock_df['quantity'] = pd.to_numeric(stock_df['quantity'], errors='coerce').fillna(0).astype(int)
    
    try:
        stock_df['expiry'] = pd.to_datetime(stock_df['expiry']).dt.date
    except Exception:
        pass

    # --- Modern Sidebar Action Panel ---
    st.sidebar.markdown(f"""
        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #374151;">👤 {st.session_state.username}</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.9em;">📱 {st.session_state.user_phone}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<h4 style='color: #4b5563;'>📌 App Navigation</h4>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Navigation", [
        "📊 Analytics Dashboard", 
        "🛒 Interactive Inventory", 
        "➕ Add New Stock", 
        "⏳ Expiry Alerts & SMS"
    ], label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.toast("Logging out securely...", icon="🔒") # Premium subtle effect
        time.sleep(0.5)
        st.session_state.clear()
        st.rerun()

    # --- Dashboard Header ---
    st.markdown(f"<h1 style='color: #1f2937; margin-bottom: -15px;'>{menu.split(' ', 1)[1]}</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #e5e7eb; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # ----- 1. ANALYTICS DASHBOARD -----
    if menu == "📊 Analytics Dashboard":
        # Premium metrics row
        m1, m2, m3, m4 = st.columns(4)
        total_items = len(stock_df)
        total_qty = stock_df["quantity"].sum() if not stock_df.empty else 0
        low_stock_count = len(stock_df[stock_df["quantity"] <= 5]) if not stock_df.empty else 0
        
        today = datetime.now().date()
        expiring_count = 0
        if not stock_df.empty:
            alert_date = today + timedelta(days=7)
            expiring_count = len(stock_df[stock_df["expiry"] <= alert_date])
            
        m1.metric("📦 Total Unique Items", f"{total_items:,}")
        m2.metric("📈 Total Quantity", f"{total_qty:,}")
        m3.metric("⚠️ Low Stock Items", f"{low_stock_count:,}", delta="-5 Threshold", delta_color="inverse")
        m4.metric("⏳ Expiring (7 Days)", f"{expiring_count:,}", delta="Urgent", delta_color="inverse")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 📊 Stock Distribution")
            if not stock_df.empty:
                # Beautiful native bar chart
                top_stock = stock_df.sort_values(by="quantity", ascending=False).head(15)
                chart_data = top_stock.set_index("name")["quantity"]
                st.bar_chart(chart_data, color="#4F46E5", height=350)
            else:
                st.info("No stock data available to visualize.")

        with col2:
            st.markdown("### 🚨 Quick Alerts")
            with st.container(border=True):
                st.markdown("**Low Stock Items (<= 5)**")
                if low_stock_count > 0:
                    st.dataframe(stock_df[stock_df["quantity"] <= 5][["name", "quantity"]], use_container_width=True, hide_index=True)
                else:
                    st.success("Stock levels look healthy! ✅")
                
                st.markdown("**Expiring Soon (<= 7 Days)**")
                if expiring_count > 0:
                    st.toast(f"{expiring_count} items are expiring soon!", icon="⚠️")
                    st.dataframe(stock_df[stock_df["expiry"] <= alert_date][["name", "expiry"]], use_container_width=True, hide_index=True)
                else:
                    st.success("No items expiring this week! ✅")

    # ----- 2. INTERACTIVE INVENTORY -----
    elif menu == "🛒 Interactive Inventory":
        st.markdown("Double-click any cell to instantly update it. Use checkboxes to delete rows, or the '+' row at the bottom to quickly add.")
        
        # Super simple and premium table editor
        search_term = st.text_input("🔍 Quick Global Search", placeholder="Type barcode or name...").lower()
        
        display_df = stock_df.copy()
        if search_term:
            display_df = display_df[
                display_df["barcode"].str.lower().str.contains(search_term) | 
                display_df["name"].str.lower().str.contains(search_term)
            ]
            
        edited_df = st.data_editor(
            display_df,
            num_rows="dynamic",               # Allow adding/removing rows directly!
            use_container_width=True,
            hide_index=True,
            key="inventory_editor",
            column_config={
                "barcode": st.column_config.TextColumn("Barcode", required=True),
                "name": st.column_config.TextColumn("Item Name", required=True),
                "quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1, required=True),
                "expiry": st.column_config.DateColumn("Expiry Date", required=True)
            }
        )
        
        # Save mechanism
        if st.button("💾 Save All Inventory Changes", type="primary"):
            # If we were searching, we must merge the changes back. If not, just overwrite.
            if search_term:
                # Merge logic to avoid destroying non-matched rows when searching
                combined_df = pd.concat([stock_df[~stock_df.index.isin(display_df.index)], edited_df]).reset_index(drop=True)
                combined_df.to_csv(STOCK_FILE, index=False)
            else:
                edited_df.to_csv(STOCK_FILE, index=False)
            st.toast("Inventory safely synced to database! 💾", icon="✅")
            st.rerun()

    # ----- 3. ADD NEW STOCK -----
    elif menu == "➕ Add New Stock":
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("### Item Details Form")
            with st.form("add_stock_form", clear_on_submit=True, border=True):
                barcode = st.text_input("Barcode", max_chars=30)
                name = st.text_input("Item Name")
                quantity = st.number_input("Quantity", min_value=1, value=1)
                expiry = st.date_input("Expiry Date", min_value=datetime.now().date())
                
                submitted = st.form_submit_button("➕ Register Item to Database", use_container_width=True)
                
                if submitted:
                    # Robust Data Validation
                    if not barcode.strip() or not name.strip():
                        st.error("❌ Barcode and Item Name cannot be empty.")
                    elif barcode.strip() in stock_df["barcode"].values:
                        # Auto-merging quantity if it exists, Premium Feature!
                        st.toast("Barcode exists! Automatically aggregating quantity.", icon="🔄")
                        idx = stock_df.index[stock_df["barcode"] == barcode.strip()][0]
                        stock_df.loc[idx, "quantity"] += quantity
                        stock_df.loc[idx, "expiry"] = expiry # Update expiry
                        stock_df.to_csv(STOCK_FILE, index=False)
                        st.success(f"Aggregated {quantity} to '{name}'! ✅")
                    else:
                        new_row = pd.DataFrame([{
                            "barcode": "".join(filter(str.isalnum, barcode.strip())),  # Sanitize
                            "name": name.strip(), 
                            "quantity": quantity, 
                            "expiry": expiry
                        }])
                        stock_df = pd.concat([stock_df, new_row], ignore_index=True)
                        stock_df.to_csv(STOCK_FILE, index=False)
                        st.toast(f"'{name}' successfully added! ✨")
                        st.success(f"New item '{name}' added successfully! ✅")

        with col2:
            if lottie_add_stock:
                st_lottie(lottie_add_stock, height=350, key="add_anim")

    # ----- 4. EXPIRY CHECK + SMS -----
    elif menu == "⏳ Expiry Alerts & SMS":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### ⚠️ Urgent Expiry Action Board")
            today = datetime.now().date()
            alert_date = today + timedelta(days=3)
            
            # Use valid datetime logic
            stock_df['expiry'] = pd.to_datetime(stock_df['expiry'], errors='coerce').dt.date
            expiring = stock_df[stock_df["expiry"] <= alert_date]
            
            if expiring.empty:
                st.info("All items are fresh! No emergencies within the next 3 days. 🎉")
            else:
                st.error(f"⚠️ {len(expiring)} Items are expiring within 3 days and require immediate action!")
                
                st.dataframe(expiring, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                if st.button("📱 Dispatch Manager SMS Alert", type="primary", use_container_width=True):
                    with st.spinner("Establishing secure connection to Twilio..."):
                        message_text = "🚨 URGENT: Grocery Stock Alert!\nThese items are expiring:\n"
                        for _, row in expiring.iterrows():
                            message_text += f"• {row['name']} (Exp: {row['expiry']})\n"
                            
                        try:
                            client = Client(ACCOUNT_SID, AUTH_TOKEN)
                            message = client.messages.create(
                                body=message_text,
                                from_=TWILIO_NUMBER,
                                to=st.session_state.user_phone
                            )
                            st.toast(f"Traceable SMS disptached to {st.session_state.user_phone}!", icon="📲")
                            st.success("Alert successfully routed to manager device. ✅")
                        except Exception as e:
                            st.error(f"Failed to communicate with GSM Gateway ❌: {e}")

        with col2:
            if lottie_expiry:
                st_lottie(lottie_expiry, height=250, key="expiry_anim")

# ---------------- ROUTER ----------------
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()