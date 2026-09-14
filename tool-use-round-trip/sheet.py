"""
The tools.

Everything Claude can reach lives in this one file:
  - four plain python functions that read the Google Sheet
  - the TOOLS list, which is all Claude ever sees of them

These are CLIENT tools. The code runs on YOUR machine.
Claude never executes any of it -- Claude only asks for it, by name.
"""

import os

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Read .env from this folder, so it works whatever directory you run from.
HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
CREDENTIALS = os.path.join(HERE, os.getenv("GOOGLE_CREDENTIALS_JSON", "service-account.json"))


# ============================================================================
# Reading the sheet
# ============================================================================

def read_tab(tab):
    """Return (headers, rows) for one tab of the spreadsheet."""
    creds = Credentials.from_service_account_file(
        CREDENTIALS, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=tab + "!A1:Z200").execute()

    values = result.get("values", [])
    if not values:
        return [], []
    return values[0], values[1:]


def look_up(tab, key):
    """
    Find one row by its first column and return it as a readable line.

    All four tools below are this function with a different tab name.
    """
    headers, rows = read_tab(tab)

    for row in rows:
        if row and row[0].lower() == key.lower():
            # Pair each column name with its value: "order_id: ORD002 | ..."
            pairs = []
            for i, name in enumerate(headers):
                if i < len(row) and row[i]:
                    pairs.append(name + ": " + row[i])
            return " | ".join(pairs)

    # Not found. Tell Claude what IS valid so it can explain the miss.
    valid = ", ".join(row[0] for row in rows if row)
    return "No '" + key + "' in " + tab + ". Valid ids: " + valid


def tab_names():
    """Every tab in the spreadsheet. The UI uses this to show the raw data."""
    creds = Credentials.from_service_account_file(
        CREDENTIALS, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    sheet = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    return [tab["properties"]["title"] for tab in sheet["sheets"]]


# ============================================================================
# THE FOUR TOOLS -- each one is STEP 2 of a round-trip
# ============================================================================
# One line each. This is the code Claude asks us to run.

def get_order(order_id):
    return look_up("Orders", order_id)


def get_customer(customer_id):
    return look_up("Customers", customer_id)


def get_product(product_id):
    return look_up("Products", product_id)


def get_shipping(order_id):
    return look_up("Shipping", order_id)


# ============================================================================
# THE SCHEMAS -- this is ALL Claude sees of the code above
# ============================================================================
# name         which button
# description  when to press it. Claude chooses the tool by reading this,
#              so the wording matters (that is tomorrow's lesson)
# input_schema what arguments the button takes

TOOLS = [
    {
        "name": "get_order",
        "description": "Look up an order by its order ID. Returns the customer_id, "
                       "product_id, quantity, amount, status and order date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g. 'ORD002'"},
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "get_customer",
        "description": "Look up a customer by their customer ID. Returns their name, "
                       "email, phone and city. If you only have an order, call "
                       "get_order first to find the customer_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "e.g. 'C002'"},
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "get_product",
        "description": "Look up a product by its product ID. Returns the name, "
                       "description, category and price. If you only have an order, "
                       "call get_order first to find the product_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "e.g. 'P102'"},
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "get_shipping",
        "description": "Look up delivery details for an order: courier, tracking ID, "
                       "delivery status and estimated arrival. Use this when someone "
                       "asks where a parcel is or when it will arrive.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g. 'ORD002'"},
            },
            "required": ["order_id"],
        },
    },
]

# Tool name -> the real function behind it.
TOOL_FUNCTIONS = {
    "get_order": get_order,
    "get_customer": get_customer,
    "get_product": get_product,
    "get_shipping": get_shipping,
}


def run_tool(name, tool_input):
    """
    STEP 2, in one place.
    Look up the function Claude named, call it with the arguments Claude filled in.
    """
    function = TOOL_FUNCTIONS[name]
    return function(**tool_input)
