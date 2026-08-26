"""
insights.py
-----------
Automatically generates human-readable financial insights from transaction data.

All insights are computed from real calculations — nothing is hard-coded.
Each insight function returns a list of (emoji, message) tuples.

Author: Personal Finance Tracker Project
"""

import pandas as pd
from datetime import datetime

from modules.analytics import (
    get_current_month_summary,
    spending_by_category,
    monthly_summary,
    category_month_over_month_change,
    consecutive_increase_categories,
)


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[tuple[str, str]]:
    """
    Analyze the transaction data and return a list of insights.

    Each insight is a (emoji, message) tuple.
    Returns an empty list if there is not enough data.

    Parameters
    ----------
    df : pd.DataFrame — Full transactions DataFrame

    Returns
    -------
    list of (str, str) — (emoji, insight text)
    """
    if df.empty:
        return [("ℹ️", "No transactions found. Add some transactions to see insights.")]

    insights = []

    # Collect insights from different analysers
    insights += _highest_category_insight(df)
    insights += _monthly_comparison_insight(df)
    insights += _savings_rate_insight(df)
    insights += _consecutive_increase_insight(df)
    insights += _entertainment_reduction_insight(df)
    insights += _income_stability_insight(df)
    insights += _balance_health_insight(df)
    insights += _spending_share_insight(df)

    # If nothing was generated (very little data), give a generic message
    if not insights:
        insights.append(("📊", "Add more transactions to unlock detailed insights."))

    return insights


# ─── Individual Insight Functions ─────────────────────────────────────────────

def _highest_category_insight(df: pd.DataFrame) -> list:
    """Identify and report the highest spending category."""
    by_cat = spending_by_category(df)
    if by_cat.empty:
        return []

    top_cat = by_cat.idxmax()
    top_amt = by_cat.max()
    total = by_cat.sum()
    pct = round(top_amt / total * 100, 1) if total > 0 else 0

    return [("🏆", f"**{top_cat}** is your highest spending category "
                   f"(₹{top_amt:,.0f} — {pct}% of total expenses).")]


def _monthly_comparison_insight(df: pd.DataFrame) -> list:
    """Compare this month's expenses to last month."""
    monthly = monthly_summary(df)
    if len(monthly) < 2:
        return []

    this_month_exp = monthly["Expenses"].iloc[-1]
    last_month_exp = monthly["Expenses"].iloc[-2]

    if last_month_exp == 0:
        return []

    change = this_month_exp - last_month_exp
    change_pct = round(change / last_month_exp * 100, 1)

    if change > 0:
        return [("📈", f"Your expenses **increased by {change_pct}%** "
                       f"(₹{abs(change):,.0f}) compared to last month.")]
    elif change < 0:
        return [("📉", f"Great job! Your expenses **decreased by {abs(change_pct)}%** "
                       f"(₹{abs(change):,.0f}) compared to last month.")]
    else:
        return [("➡️", "Your expenses are the same as last month.")]


def _savings_rate_insight(df: pd.DataFrame) -> list:
    """Report the current month's savings rate."""
    summary = get_current_month_summary(df)
    savings_pct = summary["savings_pct"]

    if summary["total_income"] == 0:
        return []

    if savings_pct >= 30:
        return [("🌟", f"Excellent! You saved **{savings_pct}%** of your income this month. "
                       "You're building strong financial habits!")]
    elif savings_pct >= 15:
        return [("✅", f"You saved approximately **{savings_pct}%** of your income this month. "
                       "That's a healthy savings rate!")]
    elif savings_pct > 0:
        return [("⚠️", f"You saved only **{savings_pct}%** of your income this month. "
                       "Try to aim for at least 20%.")]
    else:
        return [("🚨", "Your expenses exceeded your income this month. "
                       "Review your spending and look for areas to cut back.")]


def _consecutive_increase_insight(df: pd.DataFrame) -> list:
    """Flag categories with spending increases for 3+ consecutive months."""
    increasing = consecutive_increase_categories(df, months=3)

    if not increasing:
        return []

    results = []
    for cat in increasing:
        results.append(("📊", f"Your **{cat}** spending has increased for "
                               "3 consecutive months. Consider reviewing this category."))
    return results


def _entertainment_reduction_insight(df: pd.DataFrame) -> list:
    """
    Suggest reducing entertainment if it's a significant portion of expenses.
    """
    by_cat = spending_by_category(df)
    if by_cat.empty or "Entertainment" not in by_cat.index:
        return []

    ent_amt = by_cat["Entertainment"]
    total = by_cat.sum()
    ent_pct = round(ent_amt / total * 100, 1) if total > 0 else 0

    if ent_pct >= 15:
        return [("💡", f"**Entertainment** accounts for {ent_pct}% of your expenses. "
                       "Reducing it could noticeably increase your monthly savings.")]
    return []


def _income_stability_insight(df: pd.DataFrame) -> list:
    """Check if income is stable or variable across months."""
    monthly = monthly_summary(df)
    if len(monthly) < 2:
        return []

    income_values = monthly["Income"]
    if income_values.std() == 0:
        return [("💼", "Your income has been **consistent** every month — great stability!")]

    cv = income_values.std() / income_values.mean()  # Coefficient of variation
    if cv > 0.3:
        return [("💡", "Your income **varies significantly** month to month. "
                       "Consider building an emergency fund for low-income months.")]
    return []


def _balance_health_insight(df: pd.DataFrame) -> list:
    """Check overall balance health."""
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expenses = df[df["Type"] == "Expense"]["Amount"].sum()

    if total_income == 0:
        return []

    ratio = total_expenses / total_income

    if ratio > 1:
        return [("🔴", f"Overall, your expenses (₹{total_expenses:,.0f}) have **exceeded** "
                       f"your income (₹{total_income:,.0f}). Immediate budget review recommended.")]
    elif ratio > 0.85:
        return [("🟡", f"You are spending **{round(ratio*100, 1)}%** of your total income. "
                       "You have very little room for savings or emergencies.")]
    else:
        return [("🟢", f"Your overall spending-to-income ratio is healthy at "
                       f"**{round(ratio*100, 1)}%**.")]


def _spending_share_insight(df: pd.DataFrame) -> list:
    """Identify if food spending is unusually high."""
    by_cat = spending_by_category(df)
    if by_cat.empty or "Food" not in by_cat.index:
        return []

    food_pct = round(by_cat["Food"] / by_cat.sum() * 100, 1)

    if food_pct > 35:
        return [("🍽️", f"**Food** takes up {food_pct}% of your expenses. "
                       "Meal prepping or cooking at home could help reduce costs.")]
    return []
