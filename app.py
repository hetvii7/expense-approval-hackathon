import streamlit as st
from datetime import date

# Sample data stores
users = ["Employee", "Manager", "Finance", "Director", "CFO"]
expenses = []
approver_flows = ["Manager", "Finance", "Director"]

# Simulated approval state
approval_states = ["Draft", "To Approve", "Approved", "Rejected"]

# Title
st.title("Expense Approval Demo")

# Sidebar: choose role
role = st.sidebar.selectbox("Select Role", users)

# Function to convert currency (USD -> INR example)
def convert_currency(amount, from_currency="USD", to_currency="INR"):
    rates = {"USD": 1, "INR": 82}  # mock exchange rate
    return amount * rates[to_currency] / rates[from_currency]

# ---------------- Employee view ----------------
if role == "Employee":
    st.header("Submit Expense")
    with st.form("expense_form"):
        amount = st.number_input("Amount", min_value=1.0)
        currency = st.selectbox("Currency", ["USD", "INR"])
        category = st.selectbox("Category", ["Travel", "Meals", "Office"])
        description = st.text_area("Description")
        submitted_date = st.date_input("Date", date.today())
        submit = st.form_submit_button("Submit Expense")

    if submit:
   expense = {
    "id": len(expenses)+1,
    "employee": role,
    "amount": amount,
    "currency": currency,
    "category": category,
    "description": description,
    "date": submitted_date,
    "state": "To Approve",
    "next_approver_index": 0,
    "approvals": []
}  # <- Make sure this closing } exists
