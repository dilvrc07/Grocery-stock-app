# 🛍️ Grocery Stock Manager Pro

A state-of-the-art, premium Point-of-Sale (POS) and Warehouse Management application built elegantly utilizing Python and Streamlit. This application completely bridges the gap between secure administrative backend logic and a gorgeous public e-commerce store catalog.

---

## ✨ Features Architecture

### 🔒 1. Iron-Clad Administrator Access  
- **SHA-256 Cryptography:** Passwords are mathematically hashed natively. It automatically patches legacy plaintext databases into secure ciphertexts on sign-in.
- **Dynamic Role Verification:** Access to user profiles and store databases relies heavily on verified administrative token gating.
- **Secure Configuration Engine:** Employees have unique profiles dynamically tracked down to their mobile Twilio device nodes.

### 💰 2. Premium Analytics Dashboard
- Native **Financial Value Tracking** computes your aggregate live inventory value (`Quantity * Price`).
- Data Visualization rendered asynchronously through custom **Streamlit Metrics Boards** alongside interactive Bar Chart mapping.
- Top-level reporting natively generates downloadable `.csv` excel-formats directly from the internal Pandas DataFrames.
- **Intelligent Alerting Boards:** Dedicated DataFrames highlight products expiring under 7-days and stock hitting thresholds (<= 5).

### 🛒 3. E-Commerce "Customer Mode" & Shopping Cart
- Built-in Public Gateway allows guests to anonymously browse the inventory without disrupting backend configurations.
- Dynamic 2-column rendering visualizer creates a **Store Catalogue Front-end** complete with Stock Badges (`✅ In Stock`, `❌ Out of Stock`).
- Fully-Featured **Shopping Basket microservices** compute realtime calculations, map exact pricing, manipulate quantity deletions safely, and simulate live checkout proceedings.

### ⚙️ 4. Streamlined Developer Database
- Powered by `st.data_editor`, backend warehouse operators can visually manipulate hundreds of rows (Add, Replace, Delete) in parallel directly from their UI!
- Included in this repository is an active **50-Product Curated Dataset (`stock.csv`)**, pre-calculated uniquely alongside UPC-styled Barcodes and realistic perishability indices for optimal demonstration.
- **Auto-Aggregator:** When adding a duplicate item barcode into the system, the architecture avoids crashes by algorithmically absorbing and mathematically *aggregating* the exact inventory parameters onto the original entry dynamically.

### 📱 5. Twilio GSM Module Integration
- In life-threatening expiration conditions, managers can utilize the localized Lottie-powered Dashboard to remotely dispatch SMS Trace Alerts instantly through a hard-coded Twilio API bridge routing.

---

## 🚀 How to Run Locally

You must have **Python** and **VS Code** configured perfectly. 

### 1. Download Dependencies 
Install the required micro-components via your terminal:
```bash
pip install -r requirements.txt
```

### 2. Initiate the Streamlit Gateway
Deploy the local web-application container routing module safely:
```bash
python -m streamlit run app.py
```

### 3. Log In 
You may choose to **Continue as a Customer** to test the store, or authenticate securely using one of the default role-based accounts below.

> **Important:** *All default passwords are set to `1234`.*

- **Administrator:** `admin` _(Has full access to all Dashboards and Personnel Management.)_
- **Store Manager:** `manager` _(Manage Inventory and Export capabilities.)_
- **Cashier/Staff:** `cashier` or `staff` _(Standard inventory operations.)_
- **Public Sandbox:** Just click the `🛍️ Continue as Customer` button!
