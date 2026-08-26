"""
visualizations.py
-----------------
All Matplotlib chart functions for the Personal Finance Tracker.

Each function returns a Matplotlib Figure that Streamlit can render
with st.pyplot(fig).

Charts included:
  1. Expense pie chart by category
  2. Monthly spending bar chart
  3. Income vs Expenses grouped bar chart
  4. Savings trend line chart (historical + forecast)
  5. Category spending horizontal bar chart
  6. Budget vs Actual bar chart

Author: Personal Finance Tracker Project
"""

import matplotlib
matplotlib.use("Agg")   # Non-interactive backend — required for Streamlit

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ── Neuro-bank dark palette ───────────────────────────────────────────────────
PALETTE = [
    "#6378FF", "#A78BFA", "#34D399", "#F87171",
    "#FBBF24", "#22D3EE", "#FB923C", "#94A3B8",
    "#F472B6", "#4ADE80"
]

# Style settings — deep navy neuro-bank theme
CHART_STYLE = {
    "figure.facecolor": "#080B14",
    "axes.facecolor": "#0F1426",
    "axes.edgecolor": "#1E2A45",
    "axes.labelcolor": "#6878A8",
    "xtick.color": "#4B5678",
    "ytick.color": "#4B5678",
    "text.color": "#C8D0E7",
    "grid.color": "#1A2140",
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
}


def _apply_style():
    """Apply the dark theme to Matplotlib before drawing a chart."""
    plt.rcParams.update(CHART_STYLE)
    plt.rcParams["font.family"] = "DejaVu Sans"


def _finish(fig: plt.Figure) -> plt.Figure:
    """Apply tight layout and return the figure."""
    fig.tight_layout()
    return fig


# ─── 1. Expense Pie Chart ─────────────────────────────────────────────────────

def pie_chart_by_category(df: pd.DataFrame) -> plt.Figure:
    """
    Donut-style pie chart showing expense distribution by category.
    """
    _apply_style()
    expenses = df[df["Type"] == "Expense"]

    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#0F172A")

    if expenses.empty:
        ax.text(0.5, 0.5, "No expense data available",
                ha="center", va="center", color="#94A3B8", fontsize=13)
        ax.axis("off")
        return _finish(fig)

    by_cat = expenses.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    colors = PALETTE[:len(by_cat)]

    wedges, texts, autotexts = ax.pie(
        by_cat.values,
        labels=by_cat.index,
        colors=colors,
        autopct="%1.1f%%",
        pctdistance=0.75,
        startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="#0F172A", linewidth=2),
    )

    for text in texts:
        text.set_color("#CBD5E1")
        text.set_fontsize(9)
    for at in autotexts:
        at.set_color("#FFFFFF")
        at.set_fontsize(8)
        at.set_fontweight("bold")

    ax.set_title("Expense Distribution by Category",
                 color="#E2E8F0", fontsize=14, fontweight="bold", pad=15)

    return _finish(fig)


# ─── 2. Monthly Spending Bar Chart ────────────────────────────────────────────

def bar_chart_monthly_expenses(monthly_df: pd.DataFrame) -> plt.Figure:
    """
    Bar chart of total expenses per month.
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#0F172A")
    ax.set_facecolor("#1E293B")

    if monthly_df.empty:
        ax.text(0.5, 0.5, "No monthly data available",
                ha="center", va="center", color="#94A3B8", fontsize=13)
        ax.axis("off")
        return _finish(fig)

    x = np.arange(len(monthly_df))
    bars = ax.bar(x, monthly_df["Expenses"],
                  color=PALETTE[0], alpha=0.85,
                  width=0.5, edgecolor="#1E293B")

    # Add value labels on top of each bar
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 50,
                f"₹{h:,.0f}", ha="center", va="bottom",
                color="#CBD5E1", fontsize=8, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(monthly_df["Month"], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Total Expenses (₹)", color="#CBD5E1")
    ax.set_title("Monthly Expenses", color="#E2E8F0", fontsize=14, fontweight="bold")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    return _finish(fig)


# ─── 3. Income vs Expenses Grouped Bar Chart ──────────────────────────────────

def grouped_bar_income_vs_expense(monthly_df: pd.DataFrame) -> plt.Figure:
    """
    Grouped bar chart comparing income and expenses per month.
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#0F172A")
    ax.set_facecolor("#1E293B")

    if monthly_df.empty:
        ax.text(0.5, 0.5, "No data available",
                ha="center", va="center", color="#94A3B8", fontsize=13)
        ax.axis("off")
        return _finish(fig)

    x = np.arange(len(monthly_df))
    width = 0.35

    bars_inc = ax.bar(x - width / 2, monthly_df["Income"],
                      width=width, label="Income",
                      color="#34D399", alpha=0.85, edgecolor="#080B14")
    bars_exp = ax.bar(x + width / 2, monthly_df["Expenses"],
                      width=width, label="Expenses",
                      color="#F87171", alpha=0.85, edgecolor="#080B14")

    ax.set_xticks(x)
    ax.set_xticklabels(monthly_df["Month"], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Amount (₹)", color="#CBD5E1")
    ax.set_title("Income vs Expenses — Monthly Comparison",
                 color="#E2E8F0", fontsize=14, fontweight="bold")
    ax.legend(facecolor="#1E293B", edgecolor="#334155",
              labelcolor="#CBD5E1", fontsize=10)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    return _finish(fig)


# ─── 4. Savings Trend Line Chart ─────────────────────────────────────────────

def line_chart_savings_trend(trend_df: pd.DataFrame) -> plt.Figure:
    """
    Line chart showing historical savings and a forecast point.

    trend_df columns: Month, Savings, Type ('Historical' or 'Forecast')
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#0F172A")
    ax.set_facecolor("#1E293B")

    if trend_df.empty:
        ax.text(0.5, 0.5, "No savings data available",
                ha="center", va="center", color="#94A3B8", fontsize=13)
        ax.axis("off")
        return _finish(fig)

    hist = trend_df[trend_df["Type"] == "Historical"]
    fore = trend_df[trend_df["Type"] == "Forecast"]

    x_hist = list(range(len(hist)))
    ax.plot(x_hist, hist["Savings"], color="#6378FF",
            marker="o", linewidth=2.5, markersize=7, label="Historical Savings")

    # Shade area under the savings line
    ax.fill_between(x_hist, hist["Savings"], alpha=0.18, color="#6378FF")

    # If there is a forecast point, connect it with a dashed line
    if not fore.empty:
        all_months = list(hist["Month"]) + list(fore["Month"])
        x_fore = len(hist)
        # Dashed connector from last historical to forecast
        ax.plot([len(hist) - 1, x_fore],
                [hist["Savings"].iloc[-1], fore["Savings"].iloc[0]],
                color="#FBBF24", linewidth=2, linestyle="--")
        ax.scatter([x_fore], fore["Savings"], color="#FBBF24",
                   s=120, zorder=5, label="Forecast (next month)")
        ax.annotate(f"₹{fore['Savings'].iloc[0]:,.0f}",
                    (x_fore, fore["Savings"].iloc[0]),
                    textcoords="offset points", xytext=(8, 6),
                    color="#FBBF24", fontsize=9, fontweight="bold")
    else:
        all_months = list(hist["Month"])

    # Zero reference line
    ax.axhline(0, color="#EF4444", linewidth=1, linestyle=":", alpha=0.7)

    ax.set_xticks(range(len(all_months)))
    ax.set_xticklabels(all_months, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Savings (₹)", color="#CBD5E1")
    ax.set_title("Monthly Savings Trend + Next-Month Forecast",
                 color="#E2E8F0", fontsize=14, fontweight="bold")
    ax.legend(facecolor="#1E293B", edgecolor="#334155", labelcolor="#CBD5E1", fontsize=10)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    return _finish(fig)


# ─── 5. Horizontal Category Bar Chart ────────────────────────────────────────

def horizontal_bar_by_category(df: pd.DataFrame) -> plt.Figure:
    """
    Horizontal bar chart showing total spending per category.
    """
    _apply_style()
    expenses = df[df["Type"] == "Expense"]

    fig, ax = plt.subplots(figsize=(8, 5), facecolor="#0F172A")
    ax.set_facecolor("#1E293B")

    if expenses.empty:
        ax.text(0.5, 0.5, "No expense data available",
                ha="center", va="center", color="#94A3B8", fontsize=13)
        ax.axis("off")
        return _finish(fig)

    by_cat = expenses.groupby("Category")["Amount"].sum().sort_values()
    colors = PALETTE[:len(by_cat)]

    bars = ax.barh(by_cat.index, by_cat.values, color=colors,
                   alpha=0.85, edgecolor="#1E293B", height=0.6)

    # Add value labels inside bars
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 50, bar.get_y() + bar.get_height() / 2,
                f"₹{w:,.0f}", va="center", color="#CBD5E1",
                fontsize=9, fontweight="bold")

    ax.set_xlabel("Total Amount Spent (₹)", color="#CBD5E1")
    ax.set_title("Total Spending by Category",
                 color="#E2E8F0", fontsize=14, fontweight="bold")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)

    return _finish(fig)


# ─── 6. Budget vs Actual Chart ────────────────────────────────────────────────

def budget_vs_actual_chart(budget_df: pd.DataFrame) -> plt.Figure:
    """
    Horizontal grouped bar chart comparing budgeted vs. actual spending.

    budget_df columns: Category, Budget, Actual
    """
    _apply_style()

    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#0F172A")
    ax.set_facecolor("#1E293B")

    if budget_df.empty:
        ax.text(0.5, 0.5, "No budget data available",
                ha="center", va="center", color="#94A3B8", fontsize=13)
        ax.axis("off")
        return _finish(fig)

    cats = budget_df["Category"].tolist()
    y = np.arange(len(cats))
    height = 0.35

    ax.barh(y + height / 2, budget_df["Budget"], height=height,
            label="Budget", color="#6378FF", alpha=0.8, edgecolor="#080B14")
    ax.barh(y - height / 2, budget_df["Actual"], height=height,
            label="Actual Spent",
            color=["#F87171" if a > b else "#34D399"
                   for a, b in zip(budget_df["Actual"], budget_df["Budget"])],
            alpha=0.85, edgecolor="#080B14")

    ax.set_yticks(y)
    ax.set_yticklabels(cats, fontsize=10)
    ax.set_xlabel("Amount (₹)", color="#CBD5E1")
    ax.set_title("Budget vs Actual Spending",
                 color="#E2E8F0", fontsize=14, fontweight="bold")

    budget_patch = mpatches.Patch(color="#6378FF", label="Budget")
    actual_under = mpatches.Patch(color="#34D399", label="Actual (under budget)")
    actual_over = mpatches.Patch(color="#F87171", label="Actual (over budget)")
    ax.legend(handles=[budget_patch, actual_under, actual_over],
              facecolor="#1E293B", edgecolor="#334155",
              labelcolor="#CBD5E1", fontsize=9)

    ax.xaxis.grid(True)
    ax.set_axisbelow(True)

    return _finish(fig)
