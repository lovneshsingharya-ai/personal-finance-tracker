"""
predictions.py
--------------
Simple, explainable monthly savings prediction system.

Method used:
  1. Moving Average  — average of the last N months (primary)
  2. Linear Trend    — if there are enough months, apply a trend correction
  3. Fallback        — if only 1 month of data exists, use that month's figures

The prediction is clearly labeled as an *estimate*, not financial advice.

Author: Personal Finance Tracker Project
"""

import numpy as np
import pandas as pd
from modules.analytics import monthly_summary


# ─── Configuration ─────────────────────────────────────────────────────────────

# Number of recent months to use in the moving average
MOVING_AVG_WINDOW = 3


# ─── Main Prediction Function ─────────────────────────────────────────────────

def predict_next_month_savings(df: pd.DataFrame) -> dict:
    """
    Estimate next month's income, expenses, and savings based on history.

    Approach
    --------
    Step 1  — Build a monthly summary (income, expenses per month).
    Step 2  — Calculate a moving average of the last MOVING_AVG_WINDOW months.
    Step 3  — If ≥4 months of data exist, check for a linear trend and add it.
    Step 4  — Predicted savings = predicted income - predicted expenses.

    Parameters
    ----------
    df : pd.DataFrame — Full transactions DataFrame

    Returns
    -------
    dict with keys:
        predicted_income   : float
        predicted_expenses : float
        predicted_savings  : float
        method             : str  — Description of which method was used
        confidence         : str  — "Low" / "Medium" / "High"
        monthly_data       : pd.DataFrame — Underlying monthly figures used
        months_used        : int
    """
    monthly = monthly_summary(df)

    # ── Edge case: no data ─────────────────────────────────────────────────
    if monthly.empty:
        return _empty_prediction()

    n_months = len(monthly)

    # ── Edge case: only 1 month ────────────────────────────────────────────
    if n_months == 1:
        income = monthly["Income"].iloc[0]
        expenses = monthly["Expenses"].iloc[0]
        return _build_result(
            income, expenses,
            method="Single-month estimate (only 1 month of data available)",
            confidence="Low",
            monthly=monthly,
            months_used=1
        )

    # ── Choose window size ─────────────────────────────────────────────────
    window = min(MOVING_AVG_WINDOW, n_months)
    recent = monthly.tail(window)

    # Step 2 — Moving average
    avg_income = recent["Income"].mean()
    avg_expenses = recent["Expenses"].mean()

    # Step 3 — Linear trend correction (only if ≥4 months available)
    if n_months >= 4:
        income_trend = _linear_trend_increment(monthly["Income"].values)
        expense_trend = _linear_trend_increment(monthly["Expenses"].values)

        predicted_income = avg_income + income_trend
        predicted_expenses = avg_expenses + expense_trend

        method = (
            f"{window}-month moving average + linear trend correction "
            f"(based on {n_months} months of history)"
        )
        confidence = "High" if n_months >= 6 else "Medium"

    else:
        # Use plain moving average
        predicted_income = avg_income
        predicted_expenses = avg_expenses

        method = (
            f"{window}-month moving average "
            f"(based on {n_months} months of history)"
        )
        confidence = "Medium" if n_months == 3 else "Low"

    # Clamp to zero — predicted amounts should never be negative
    predicted_income = max(0, round(predicted_income, 2))
    predicted_expenses = max(0, round(predicted_expenses, 2))

    return _build_result(
        predicted_income, predicted_expenses,
        method=method,
        confidence=confidence,
        monthly=monthly,
        months_used=window
    )


# ─── Helper Functions ─────────────────────────────────────────────────────────

def _linear_trend_increment(values: np.ndarray) -> float:
    """
    Fit a simple linear regression (y = mx + b) to the array of values
    and return the slope 'm', which represents the expected change per month.

    A positive slope means the values are increasing each month.
    A negative slope means they are decreasing.

    Parameters
    ----------
    values : np.ndarray — Time-ordered monthly values

    Returns
    -------
    float — Slope of the trend line
    """
    x = np.arange(len(values))          # Month indices: 0, 1, 2, ...
    slope, _ = np.polyfit(x, values, 1) # Linear fit: slope and intercept
    return round(slope, 2)


def _build_result(income: float, expenses: float,
                  method: str, confidence: str,
                  monthly: pd.DataFrame, months_used: int) -> dict:
    """
    Build the prediction result dictionary.
    """
    savings = round(income - expenses, 2)
    savings_pct = round((savings / income * 100), 1) if income > 0 else 0.0

    return {
        "predicted_income": income,
        "predicted_expenses": expenses,
        "predicted_savings": savings,
        "predicted_savings_pct": savings_pct,
        "method": method,
        "confidence": confidence,
        "monthly_data": monthly,
        "months_used": months_used,
    }


def _empty_prediction() -> dict:
    """
    Return a zeroed-out prediction dictionary when no data is available.
    """
    return {
        "predicted_income": 0.0,
        "predicted_expenses": 0.0,
        "predicted_savings": 0.0,
        "predicted_savings_pct": 0.0,
        "method": "No data available — add transactions to generate a prediction.",
        "confidence": "N/A",
        "monthly_data": pd.DataFrame(),
        "months_used": 0,
    }


# ─── Savings Trend (for chart) ────────────────────────────────────────────────

def savings_trend_with_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame combining historical monthly savings with
    one forecast point for the next month.

    Columns: Month (str), Savings (float), Type ('Historical' or 'Forecast')
    """
    monthly = monthly_summary(df)

    if monthly.empty:
        return pd.DataFrame(columns=["Month", "Savings", "Type"])

    # Historical savings
    hist = monthly[["Month", "Savings"]].copy()
    hist["Type"] = "Historical"

    # Forecast for the next month
    prediction = predict_next_month_savings(df)
    if prediction["months_used"] == 0:
        return hist

    # Calculate next month label
    last_period = pd.Period(monthly["Month"].iloc[-1], freq="M")
    next_month = str(last_period + 1)

    forecast_row = pd.DataFrame([{
        "Month": next_month,
        "Savings": prediction["predicted_savings"],
        "Type": "Forecast"
    }])

    return pd.concat([hist, forecast_row], ignore_index=True)
