import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from streamlit_lottie import st_lottie
import requests
import json

# ---------------- TWILIO DETAILS ----------------
ACCOUNT_SID = "AC1d50b24f9c09875ea85105bc196afbd8"
AUTH_TOKEN = "c5630078cbf72cd003be296bb46f7a5b"
TWILIO_NUMBER = "+19133996249"
TEST_NUMBER = "+919363735799"
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ---------------- FILES ----------------
USERS_FILE = "users.csv"
STOCK_FILE = "stock.csv"

# Create files if they don't exist
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["username","password","phone"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(STOCK_FILE):
    pd.DataFrame(columns=["barcode","name","quantity","expiry"]).to_csv(STOCK_FILE, index=False)

# ---------------- LOTTIE FUNCTION ----------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---------------- LOTTIE ANIMATIONS ----------------
lottie_login = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_5ngs2ksb.json")
lottie_add_stock = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_jbrw3hcz.json")
lottie_view_stock = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_tll0j4bb.json")
lottie_expiry = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_rnnlxazi.json")
lottie_success = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_qp1q7mct.json")

# ---------------- APP TITLE ----------------
st.title("🛒 Grocery Stock Management App")

# ---------------- LOGIN SYSTEM ----------------
users_df = pd.read_csv(USERS_FILE)
users_df["username"] = users_df["username"].astype(str).str.strip()
users_df["password"] = users_df["password"].astype(str).str.strip()
users_df["phone"] = users_df["phone"].astype(str).str.strip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- LOGIN PAGE ----------
if not st.session_state.logged_in:
    st_lottie(lottie_login, height=200)  # <-- Animation on login page
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = users_df[
            (users_df["username"].str.lower() == username.strip().lower()) &
            (users_df["password"] == password.strip())
        ]
        if not user.empty:
            st.success("Login successful ✅")
            st.session_state.logged_in = True
            st.session_state.user_phone = user.iloc[0]["phone"]
        else:
            st.error("Invalid username or password ❌")

# ---------- MAIN APP AFTER LOGIN ----------
else:
    st.sidebar.success("Logged in")
    menu = st.sidebar.selectbox("Menu", ["Add Stock", "View Stock", "Search by Barcode", "Update/Delete", "Check Expiry"])
    stock_df = pd.read_csv(STOCK_FILE)
    stock_df["barcode"] = stock_df["barcode"].astype(str)

    # ---------- ADD STOCK ----------
    if menu == "Add Stock":
        st_lottie(lottie_add_stock, height=150)  # <-- Animation on Add Stock page
        st.subheader("Add New Item")
        barcode = st.text_input("Barcode")
        name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=1)
        expiry = st.date_input("Expiry Date")
        if st.button("Add Item"):
            new_row = pd.DataFrame([[barcode, name, quantity, expiry]], columns=["barcode","name","quantity","expiry"])
            stock_df = pd.concat([stock_df, new_row], ignore_index=True)
            stock_df.to_csv(STOCK_FILE, index=False)
            st.success("Item added successfully ✅")
            st_lottie(lottie_success, height=100)  # <-- Success animation

    # ---------- VIEW STOCK ----------
    elif menu == "View Stock":
        st_lottie(lottie_view_stock, height=150)  # <-- Animation on View Stock
        st.subheader("All Stock")
        st.dataframe(stock_df)

    # ---------- SEARCH BY BARCODE ----------
    elif menu == "Search by Barcode":
        st.subheader("Search Item")
        search_barcode = st.text_input("Enter barcode").strip()
        if st.button("Search"):
            result = stock_df[stock_df["barcode"] == search_barcode]
            if result.empty:
                st.warning("Item not found ❌")
            else:
                st.dataframe(result)

    # ---------- UPDATE / DELETE ----------
    elif menu == "Update/Delete":
        st.subheader("Update or Delete Item")
        barcode_input = st.text_input("Enter barcode").strip()
        if barcode_input:
            item = stock_df[stock_df["barcode"] == barcode_input]
            if not item.empty:
                name_val = item.iloc[0]["name"]
                quantity_val = int(item.iloc[0]["quantity"])
                expiry_val = pd.to_datetime(item.iloc[0]["expiry"])
                name = st.text_input("Name", name_val)
                quantity = st.number_input("Quantity", min_value=1, value=quantity_val)
                expiry = st.date_input("Expiry", expiry_val)
                col1, col2 = st.columns(2)
                if col1.button("Update"):
                    stock_df.loc[stock_df["barcode"] == barcode_input, ["name","quantity","expiry"]] = [name, quantity, expiry]
                    stock_df.to_csv(STOCK_FILE, index=False)
                    st.success("Updated successfully ✅")
                if col2.button("Delete"):
                    stock_df = stock_df[stock_df["barcode"] != barcode_input]
                    stock_df.to_csv(STOCK_FILE, index=False)
                    st.success("Deleted successfully ✅")
            else:
                st.warning("Barcode not found ❌")

    # ---------- EXPIRY CHECK + SMS ----------
    elif menu == "Check Expiry":
        st_lottie(lottie_expiry, height=150)  # <-- Animation on Expiry page
        st.subheader("Expiry Alert (Next 3 days)")
        stock_df["expiry"] = pd.to_datetime(stock_df["expiry"])
        today = datetime.now()
        alert_date = today + timedelta(days=3)
        expiring = stock_df[stock_df["expiry"] <= alert_date]
        if expiring.empty:
            st.success("No items expiring soon ✅")
        else:
            st.warning("Items expiring soon:")
            st.dataframe(expiring)
            if st.button("Send SMS Alert"):
                message_text = "Alert! These items are expiring soon:\n"
                for i in expiring.itertuples():
                    message_text += f"{i.name} (Expiry: {i.expiry.date()})\n"
                try:
                    message = client.messages.create(
                        body=message_text,
                        from_=TWILIO_NUMBER,
                        to=st.session_state.user_phone
                    )
                    st.success("SMS sent successfully ✅")
                except Exception as e:
                    st.error(f"SMS failed ❌: {e}")

    # ---------- LOGOUT ----------
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()