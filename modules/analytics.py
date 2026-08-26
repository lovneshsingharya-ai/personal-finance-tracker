"""
analytics.py
------------
All data analysis functions for the Personal Finance Tracker.
Uses Pandas for grouping, aggregating, and calculating statistics.

Author: Personal Finance Tracker Project
"""

import pandas as pd
import numpy as np
from datetime import datetime


# ─── Summary Statistics ───────────────────────────────────────────────────────

def get_summary(df: pd.DataFrame) -> dict:
    """
    Compute high-level financial summary metrics.

    Parameters
    ----------
    df : pd.DataFrame — Full transactions DataFrame

    Returns
    -------
    dict with keys:
        total_income, total_expenses, balance, total_savings,
        savings_pct, avg_daily_spending, highest_category
    """
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "balance": 0.0,
            "total_savings": 0.0,
            "savings_pct": 0.0,
            "avg_daily_spending": 0.0,
            "highest_category": "N/A",
        }

    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expenses = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expenses
    total_savings = max(balance, 0)  # Savings can't be negative

    # Savings percentage = savings / income × 100
    savings_pct = (total_savings / total_income * 100) if total_income > 0 else 0.0

    # Average daily spending (over all days in the dataset)
    expense_df = df[df["Type"] == "Expense"]
    if not expense_df.empty:
        date_range_days = max(
            1, (df["Date"].max() - df["Date"].min()).days + 1
        )
        avg_daily_spending = total_expenses / date_range_days
    else:
        avg_daily_spending = 0.0

    # Highest spending category
    highest_category = "N/A"
    if not expense_df.empty:
        cat_totals = expense_df.groupby("Category")["Amount"].sum()
        highest_category = cat_totals.idxmax()

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "balance": round(balance, 2),
        "total_savings": round(total_savings, 2),
        "savings_pct": round(savings_pct, 1),
        "avg_daily_spending": round(avg_daily_spending, 2),
        "highest_category": highest_category,
    }


def get_current_month_summary(df: pd.DataFrame) -> dict:
    """
    Return financial summary for the current calendar month.

    Returns the same structure as get_summary() but filtered to this month.
    """
    today = datetime.today()
    month_df = df[
        (df["Date"].dt.year == today.year) &
        (df["Date"].dt.month == today.month)
    ]
    return get_summary(month_df)


# ─── Category Analysis ────────────────────────────────────────────────────────

def spending_by_category(df: pd.DataFrame) -> pd.Series:
    """
    Return total expenses grouped by category, sorted descending.

    Returns
    -------
    pd.Series indexed by category name
    """
    expenses = df[df["Type"] == "Expense"]
    if expenses.empty:
        return pd.Series(dtype=float)
    return expenses.groupby("Category")["Amount"].sum().sort_values(ascending=False)


def spending_percentage_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with category, total amount, and percentage of spending.

    Returns
    -------
    pd.DataFrame with columns: Category, Amount, Percentage
    """
    by_cat = spending_by_category(df)
    if by_cat.empty:
        return pd.DataFrame(columns=["Category", "Amount", "Percentage"])

    total = by_cat.sum()
    pct = (by_cat / total * 100).round(1)

    result = pd.DataFrame({
        "Category": by_cat.index,
        "Amount": by_cat.values,
        "Percentage": pct.values
    }).reset_index(drop=True)

    return result


# ─── Monthly Analysis ─────────────────────────────────────────────────────────

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate income, expenses, and net savings per calendar month.

    Returns
    -------
    pd.DataFrame with columns:
        Month (period), Income, Expenses, Savings, Savings_Pct
    """
    if df.empty:
        return pd.DataFrame(columns=["Month", "Income", "Expenses", "Savings", "Savings_Pct"])

    # Create a Year-Month period column
    df = df.copy()
    df["Month"] = df["Date"].dt.to_period("M")

    # Pivot income and expenses separately then merge
    income_m = (
        df[df["Type"] == "Income"]
        .groupby("Month")["Amount"]
        .sum()
        .rename("Income")
    )
    expense_m = (
        df[df["Type"] == "Expense"]
        .groupby("Month")["Amount"]
        .sum()
        .rename("Expenses")
    )

    monthly = pd.concat([income_m, expense_m], axis=1).fillna(0)
    monthly["Savings"] = monthly["Income"] - monthly["Expenses"]
    monthly["Savings_Pct"] = np.where(
        monthly["Income"] > 0,
        (monthly["Savings"] / monthly["Income"] * 100).round(1),
        0.0
    )
    monthly = monthly.reset_index()
    monthly["Month"] = monthly["Month"].astype(str)  # e.g. "2026-08"

    return monthly


# ─── Trend Detection ──────────────────────────────────────────────────────────

def spending_trend_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a pivot table of monthly spending per category.
    Useful for detecting which categories are rising or falling.

    Returns
    -------
    pd.DataFrame — rows = months, columns = categories, values = total spent
    """
    expenses = df[df["Type"] == "Expense"].copy()
    if expenses.empty:
        return pd.DataFrame()

    expenses["Month"] = expenses["Date"].dt.to_period("M").astype(str)
    pivot = (
        expenses.groupby(["Month", "Category"])["Amount"]
        .sum()
        .unstack(fill_value=0)
        .sort_index()
    )
    return pivot


def category_month_over_month_change(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate month-over-month change (absolute and %) for each expense category.
    Compares the last two complete months.

    Returns
    -------
    pd.DataFrame with columns:
        Category, Last_Month, This_Month, Change, Change_Pct
    """
    pivot = spending_trend_by_category(df)

    if pivot.shape[0] < 2:
        return pd.DataFrame(columns=["Category", "Last_Month", "This_Month", "Change", "Change_Pct"])

    last_month = pivot.iloc[-2]
    this_month = pivot.iloc[-1]

    change = this_month - last_month
    change_pct = np.where(
        last_month > 0,
        (change / last_month * 100).round(1),
        0.0
    )

    result = pd.DataFrame({
        "Category": pivot.columns,
        "Last_Month": last_month.values,
        "This_Month": this_month.values,
        "Change": change.values,
        "Change_Pct": change_pct
    })

    return result.sort_values("Change", ascending=False).reset_index(drop=True)


def consecutive_increase_categories(df: pd.DataFrame, months: int = 3) -> list:
    """
    Return categories whose spending has increased for `months` consecutive months.

    Parameters
    ----------
    months : int — Number of consecutive months to check (default 3)

    Returns
    -------
    list of category names showing consecutive increases
    """
    pivot = spending_trend_by_category(df)

    if pivot.shape[0] < months:
        return []

    recent = pivot.tail(months)
    increasing = []

    for col in recent.columns:
        values = recent[col].values
        # Check if each month is strictly greater than the previous
        if all(values[i] > values[i - 1] for i in range(1, len(values))):
            increasing.append(col)

    return increasing


# ─── Income vs Expense Comparison ────────────────────────────────────────────

def income_vs_expense_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return monthly totals for income and expenses side-by-side.
    Alias for monthly_summary() — kept for readability in chart module.
    """
    return monthly_summary(df)


# ─── Average Spending ─────────────────────────────────────────────────────────

def average_monthly_income(df: pd.DataFrame) -> float:
    """Return the average monthly income across all months in the dataset."""
    monthly = monthly_summary(df)
    if monthly.empty:
        return 0.0
    return round(monthly["Income"].mean(), 2)


def average_monthly_expenses(df: pd.DataFrame) -> float:
    """Return the average monthly expenses across all months in the dataset."""
    monthly = monthly_summary(df)
    if monthly.empty:
        return 0.0
    return round(monthly["Expenses"].mean(), 2)


def highest_and_lowest_categories(df: pd.DataFrame) -> tuple[str, str]:
    """
    Return (highest_spending_category, lowest_spending_category).

    Returns ("N/A", "N/A") if there are no expenses.
    """
    by_cat = spending_by_category(df)
    if by_cat.empty:
        return "N/A", "N/A"
    return by_cat.idxmax(), by_cat.idxmin()
