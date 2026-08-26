"""
data_manager.py
---------------
Handles all data loading, saving, and basic validation for transactions.
Transactions are stored in a simple CSV file for easy inspection.

Author: Personal Finance Tracker Project
"""

import os
import pandas as pd
from datetime import datetime

# ─── Constants ────────────────────────────────────────────────────────────────

# Path to the CSV file (relative to the project root)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "transactions.csv")

# Column names used throughout the application
COLUMNS = ["Date", "Type", "Category", "Amount", "Description"]

# Valid transaction types
VALID_TYPES = ["Income", "Expense"]

# Suggested expense categories
EXPENSE_CATEGORIES = [
    "Food", "Transport", "Education", "Shopping",
    "Entertainment", "Bills", "Healthcare", "Other"
]

# Suggested income categories
INCOME_CATEGORIES = [
    "Salary", "Freelance", "Scholarship", "Gift", "Investment", "Other"
]


# ─── Core Functions ───────────────────────────────────────────────────────────

def ensure_data_file():
    """
    Make sure the data directory and CSV file exist.
    If the CSV does not exist, create an empty one with the correct headers.
    Called automatically whenever data is loaded.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(CSV_PATH):
        # Create an empty DataFrame and save it as the initial CSV
        empty_df = pd.DataFrame(columns=COLUMNS)
        empty_df.to_csv(CSV_PATH, index=False)


def load_transactions() -> pd.DataFrame:
    """
    Load all transactions from the CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Date, Type, Category, Amount, Description.
        Date is parsed as datetime. Amount is numeric (float).
        Returns an empty DataFrame if the file is empty.
    """
    ensure_data_file()

    try:
        df = pd.read_csv(CSV_PATH)

        # Return empty DataFrame with correct columns if file is empty
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)

        # ── Clean and convert columns ──────────────────────────────────────
        # Parse dates — errors become NaT so we can drop or handle them
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Convert Amount to float; invalid entries become NaN
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

        # Strip extra whitespace from string columns
        for col in ["Type", "Category", "Description"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # Drop rows where critical columns are missing
        df = df.dropna(subset=["Date", "Amount", "Type"])

        # Remove any rows with negative or zero amounts
        df = df[df["Amount"] > 0]

        # Sort by date (newest last) so history reads chronologically
        df = df.sort_values("Date").reset_index(drop=True)

        return df

    except Exception as e:
        # If anything goes wrong reading the file, return empty DataFrame
        print(f"Warning: Could not load transactions — {e}")
        return pd.DataFrame(columns=COLUMNS)


def save_transaction(date: str, txn_type: str, category: str,
                     amount: float, description: str) -> tuple[bool, str]:
    """
    Validate and append a single transaction to the CSV file.

    Parameters
    ----------
    date        : str   — Date string in 'YYYY-MM-DD' format
    txn_type    : str   — 'Income' or 'Expense'
    category    : str   — Category label
    amount      : float — Positive numeric amount
    description : str   — Short text description

    Returns
    -------
    (True, "Success message") on success
    (False, "Error message")  on validation failure
    """
    # ── Validation ────────────────────────────────────────────────────────

    # Check date
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        # Reject future dates beyond today
        if parsed_date.date() > datetime.today().date():
            return False, "Date cannot be in the future."
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD."

    # Check type
    if txn_type not in VALID_TYPES:
        return False, f"Transaction type must be one of: {VALID_TYPES}"

    # Check category
    if not category or category.strip() == "":
        return False, "Category cannot be empty."

    # Check amount
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be a positive number."
    except (ValueError, TypeError):
        return False, "Amount must be a valid number."

    # Check description
    if not description or description.strip() == "":
        return False, "Description cannot be empty."

    # ── Save to CSV ───────────────────────────────────────────────────────
    ensure_data_file()

    new_row = pd.DataFrame([{
        "Date": date,
        "Type": txn_type,
        "Category": category.strip(),
        "Amount": round(amount, 2),
        "Description": description.strip()
    }])

    # Append to existing file (write header only if file is new/empty)
    new_row.to_csv(CSV_PATH, mode="a",
                   header=not os.path.exists(CSV_PATH) or os.stat(CSV_PATH).st_size == 0,
                   index=False)

    return True, f"✅ Transaction of ₹{amount:.2f} saved successfully!"


def delete_transaction(index: int) -> tuple[bool, str]:
    """
    Delete a transaction by its positional index in the loaded DataFrame.

    Parameters
    ----------
    index : int — Zero-based row index

    Returns
    -------
    (True, "Success message") or (False, "Error message")
    """
    df = load_transactions()

    if index < 0 or index >= len(df):
        return False, "Invalid transaction index."

    df = df.drop(df.index[index]).reset_index(drop=True)

    # Save the updated DataFrame back (overwrite the whole file)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df.to_csv(CSV_PATH, index=False)

    return True, "Transaction deleted successfully."


def get_date_range() -> tuple:
    """
    Return the earliest and latest dates present in the transaction data.

    Returns
    -------
    (min_date, max_date) as datetime.date objects,
    or (today, today) if there is no data.
    """
    df = load_transactions()

    if df.empty:
        today = datetime.today().date()
        return today, today

    return df["Date"].min().date(), df["Date"].max().date()


def get_categories() -> list:
    """Return all unique categories found in the transaction history."""
    df = load_transactions()
    if df.empty:
        return EXPENSE_CATEGORIES + INCOME_CATEGORIES
    return sorted(df["Category"].unique().tolist())
