"""
app.py
------
Main entry point for the Personal Finance Tracker Dashboard.

Run with:  streamlit run app.py

Navigation pages:
  1. 🏠 Dashboard         — KPI cards and current month summary
  2. ➕ Add Transaction   — Form to add income / expense entries
  3. 📋 Transactions      — Searchable, filterable transaction history
  4. 📊 Spending Analysis — Charts and category breakdown
  5. 💰 Budget            — Set and track monthly budgets per category
  6. 🔮 Savings Prediction — Moving average + trend forecast

Author: Personal Finance Tracker Project
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

# ── Local module imports ───────────────────────────────────────────────────────
from modules.data_manager import (
    load_transactions, save_transaction, delete_transaction,
    EXPENSE_CATEGORIES, INCOME_CATEGORIES, get_date_range
)
from modules.analytics import (
    get_summary, get_current_month_summary,
    spending_by_category, spending_percentage_by_category,
    monthly_summary, income_vs_expense_monthly,
    average_monthly_income, average_monthly_expenses,
    highest_and_lowest_categories, category_month_over_month_change,
)
from modules.predictions import predict_next_month_savings, savings_trend_with_forecast
from modules.insights import generate_insights
from charts.visualizations import (
    pie_chart_by_category, bar_chart_monthly_expenses,
    grouped_bar_income_vs_expense, line_chart_savings_trend,
    horizontal_bar_by_category, budget_vs_actual_chart
)

# ─── Page Configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="FinTrack — Personal Finance",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS — Neuro-Bank Premium Dark Theme ───────────────────────────────

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App background with subtle dot grid ── */
.stApp {
    background-color: #080B14;
    background-image: radial-gradient(circle, #1a2040 1px, transparent 1px);
    background-size: 28px 28px;
    color: #C8D0E7;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0B0E1A !important;
    border-right: 1px solid rgba(99, 120, 255, 0.15) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* ── Sidebar header brand ── */
.brand-header {
    background: linear-gradient(135deg, #1a1f3c 0%, #0d1126 100%);
    border-bottom: 1px solid rgba(99,120,255,0.2);
    padding: 24px 20px 20px 20px;
    margin: -1rem -1rem 1rem -1rem;
}
.brand-logo {
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(135deg, #6378FF, #A78BFA, #22D3EE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}
.brand-sub {
    font-size: 11px;
    color: #4B5678;
    margin-top: 2px;
    font-weight: 500;
    letter-spacing: 0.05em;
}

/* ── Sidebar nav items ── */
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px !important;
}
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    color: #6878A8 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(99,120,255,0.08) !important;
    color: #A0AECF !important;
    border-color: rgba(99,120,255,0.2) !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 13px !important;
}

/* ── Page title bar ── */
.page-title {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(99,120,255,0.12);
}
.page-title-text {
    font-size: 24px;
    font-weight: 800;
    color: #E8EEFF;
    letter-spacing: -0.5px;
}
.page-title-badge {
    background: rgba(99,120,255,0.12);
    border: 1px solid rgba(99,120,255,0.25);
    color: #8B9FFF;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Section label ── */
.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3D4F7A;
    margin: 20px 0 12px 0;
}

/* ── KPI Card — neuro-bank style ── */
.kpi-card {
    background: linear-gradient(145deg, #0F1426, #0B0E1C);
    border: 1px solid rgba(99,120,255,0.15);
    border-radius: 18px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
    height: 100%;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6378FF, #A78BFA, #22D3EE);
    opacity: 0;
    transition: opacity 0.25s ease;
}
.kpi-card:hover {
    border-color: rgba(99,120,255,0.35);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(99,120,255,0.12);
}
.kpi-card:hover::before { opacity: 1; }

.kpi-icon {
    font-size: 20px;
    margin-bottom: 12px;
    display: block;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #3D4F7A;
    margin-bottom: 6px;
}
.kpi-amount {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #E8EEFF;
    margin-bottom: 6px;
}
.kpi-change {
    font-size: 12px;
    font-weight: 500;
    color: #4B5678;
}
.kpi-change.positive { color: #34D399; }
.kpi-change.negative { color: #F87171; }
.kpi-change.warning  { color: #FBBF24; }

/* ── Insight card ── */
.insight-card {
    background: linear-gradient(135deg, #0F1426, #0B0E1C);
    border: 1px solid rgba(99,120,255,0.12);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 8px;
    font-size: 13.5px;
    color: #8B9FC8;
    line-height: 1.65;
    transition: border-color 0.2s;
}
.insight-card:hover {
    border-color: rgba(99,120,255,0.28);
}

/* ── Summary row card ── */
.month-card {
    background: linear-gradient(135deg, #0D1020 0%, #111527 100%);
    border: 1px solid rgba(99,120,255,0.12);
    border-radius: 14px;
    padding: 18px 22px;
    text-align: center;
}
.month-card .label {
    font-size: 11px; color: #3D4F7A;
    text-transform: uppercase; letter-spacing: 0.08em;
    font-weight: 600; margin-bottom: 6px;
}
.month-card .value {
    font-size: 20px; font-weight: 800;
    letter-spacing: -0.5px;
}

/* ── Form styling ── */
.form-card {
    background: linear-gradient(145deg, #0F1426, #0B0E1C);
    border: 1px solid rgba(99,120,255,0.15);
    border-radius: 18px;
    padding: 28px 32px;
}

/* ── Table styling ── */
.stDataFrame {
    border: 1px solid rgba(99,120,255,0.12) !important;
    border-radius: 14px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4F52D9, #6B5CE7);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.02em;
    width: 100%;
    transition: all 0.2s ease;
    box-shadow: 0 4px 20px rgba(79,82,217,0.35);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #5F62E9, #7B6CF7);
    box-shadow: 0 6px 28px rgba(79,82,217,0.5);
    transform: translateY(-1px);
}

/* ── Progress bars ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #4F52D9, #A78BFA) !important;
    border-radius: 99px !important;
}
.stProgress > div {
    background: rgba(99,120,255,0.08) !important;
    border-radius: 99px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(99,120,255,0.04) !important;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(99,120,255,0.1);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: #4B5678 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: none !important;
    padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4F52D9, #6B5CE7) !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(79,82,217,0.35) !important;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input {
    background: #0B0E1C !important;
    border: 1px solid rgba(99,120,255,0.2) !important;
    border-radius: 10px !important;
    color: #C8D0E7 !important;
}
.stSelectbox > div > div {
    background: #0B0E1C !important;
    border: 1px solid rgba(99,120,255,0.2) !important;
    border-radius: 10px !important;
    color: #C8D0E7 !important;
}

/* ── Info / Success / Warning banners ── */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid rgba(99,120,255,0.2) !important;
}

/* ── Horizontal rule ── */
hr {
    border-color: rgba(99,120,255,0.1) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(99,120,255,0.05) !important;
    border-radius: 10px !important;
    color: #6878A8 !important;
    font-weight: 600 !important;
}

/* ── Budget category bar ── */
.budget-row {
    background: linear-gradient(135deg, #0F1426, #0B0E1C);
    border: 1px solid rgba(99,120,255,0.12);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.budget-row:hover { border-color: rgba(99,120,255,0.28); }
.budget-cat { font-size: 13px; font-weight: 700; color: #C8D0E7; }
.budget-nums { font-size: 12px; color: #4B5678; margin-top: 4px; }
.budget-status { font-size: 11px; font-weight: 700; margin-top: 3px; }

/* ── Stat mini-table ── */
table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar Navigation ───────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">💸 FinTrack</div>
        <div class="brand-sub">PERSONAL FINANCE DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["🏠  Dashboard", "➕  Add Transaction", "📋  Transactions",
         "📊  Spending Analysis", "💰  Budget", "🔮  Savings Prediction"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # ── Quick Stats in sidebar ─────────────────────────────────────────────
    st.markdown('<div class="section-label">Quick Stats</div>', unsafe_allow_html=True)

    @st.cache_data(ttl=5)
    def _sidebar_stats():
        from modules.data_manager import load_transactions
        from modules.analytics import get_summary
        df = load_transactions()
        return get_summary(df)

    s = _sidebar_stats()
    st.markdown(f"""
    <div style="padding:0 4px;">
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 12px;background:rgba(99,120,255,0.06);
                    border-radius:10px;margin-bottom:6px;">
            <span style="font-size:12px;color:#4B5678;font-weight:600;">Balance</span>
            <span style="font-size:13px;font-weight:800;
                         color:{'#34D399' if s['balance']>=0 else '#F87171'};">
                ₹{s['balance']:,.0f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 12px;background:rgba(99,120,255,0.06);
                    border-radius:10px;margin-bottom:6px;">
            <span style="font-size:12px;color:#4B5678;font-weight:600;">Savings Rate</span>
            <span style="font-size:13px;font-weight:800;
                         color:{'#34D399' if s['savings_pct']>=20 else '#FBBF24'};">
                {s['savings_pct']}%</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 12px;background:rgba(99,120,255,0.06);
                    border-radius:10px;">
            <span style="font-size:12px;color:#4B5678;font-weight:600;">Top Spend</span>
            <span style="font-size:13px;font-weight:800;color:#A78BFA;">
                {s['highest_category']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:24px;text-align:center;">
        <div style="font-size:10px;color:#1E2A45;font-weight:600;letter-spacing:0.05em;">
        FINTRACK v1.0 · COLLEGE PROJECT</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Load Data ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=5)
def get_data():
    return load_transactions()


def refresh():
    st.cache_data.clear()


# ─── Helper: color_type for pandas Styler (pandas >= 2.1 uses .map not .applymap) ──

def _color_type_style(val):
    """Style function for Income/Expense column coloring."""
    color = "#34D399" if val == "Income" else "#F87171"
    return f"color: {color}; font-weight: 700;"


def _safe_style(df, col="Type"):
    """Apply color styling — compatible with both old and new pandas."""
    try:
        return df.style.map(_color_type_style, subset=[col])
    except AttributeError:
        return df.style.applymap(_color_type_style, subset=[col])


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 1 — DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown("""
    <div class="page-title">
        <span class="page-title-text">Dashboard</span>
        <span class="page-title-badge">Overview</span>
    </div>
    """, unsafe_allow_html=True)

    df = get_data()
    summary = get_summary(df)
    month_summary = get_current_month_summary(df)
    now = datetime.now()

    # ── KPI Row 1 ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">All-Time Summary</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    def kpi(col, icon, label, amount, change_text, change_class):
        col.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-label">{label}</div>
            <div class="kpi-amount">{amount}</div>
            <div class="kpi-change {change_class}">{change_text}</div>
        </div>
        """, unsafe_allow_html=True)

    kpi(c1, "💵", "Total Income",
        f"₹{summary['total_income']:,.0f}",
        "All recorded income", "")

    kpi(c2, "💸", "Total Expenses",
        f"₹{summary['total_expenses']:,.0f}",
        "All recorded expenses", "")

    kpi(c3, "🏦", "Net Balance",
        f"₹{summary['balance']:,.0f}",
        "Income minus expenses",
        "positive" if summary["balance"] >= 0 else "negative")

    kpi(c4, "📈", "Savings Rate",
        f"{summary['savings_pct']}%",
        "Of total income saved",
        "positive" if summary["savings_pct"] >= 20 else "warning")

    st.markdown("<br>", unsafe_allow_html=True)

    c5, c6, c7 = st.columns(3)
    kpi(c5, "📅", "Avg Daily Spend",
        f"₹{summary['avg_daily_spending']:,.0f}",
        "Across all tracked days", "")

    kpi(c6, "🏆", "Top Category",
        summary["highest_category"],
        "Highest expense category", "warning")

    kpi(c7, "💰", "Total Savings",
        f"₹{summary['total_savings']:,.0f}",
        "Accumulated net savings",
        "positive" if summary["total_savings"] >= 0 else "negative")

    st.markdown("---")

    # ── Current Month ──────────────────────────────────────────────────────
    st.markdown(f'<div class="section-label">{now.strftime("%B %Y")} — This Month</div>',
                unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    def month_kpi(col, label, value, color):
        col.markdown(f"""
        <div class="month-card">
            <div class="label">{label}</div>
            <div class="value" style="color:{color};">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    month_kpi(m1, "Income", f"₹{month_summary['total_income']:,.0f}", "#34D399")
    month_kpi(m2, "Expenses", f"₹{month_summary['total_expenses']:,.0f}", "#F87171")
    month_kpi(m3, "Balance",
              f"₹{month_summary['balance']:,.0f}",
              "#34D399" if month_summary["balance"] >= 0 else "#F87171")
    month_kpi(m4, "Saved",
              f"{month_summary['savings_pct']}%",
              "#34D399" if month_summary["savings_pct"] >= 20 else "#FBBF24")

    st.markdown("---")

    # ── Charts ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Visual Breakdown</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.pyplot(pie_chart_by_category(df))
    with chart_col2:
        monthly = monthly_summary(df)
        st.pyplot(grouped_bar_income_vs_expense(monthly))

    # ── Insights ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">AI-Style Insights</div>', unsafe_allow_html=True)

    insights = generate_insights(df)
    cols = st.columns(2)
    for i, (emoji, msg) in enumerate(insights):
        with cols[i % 2]:
            st.markdown(
                f'<div class="insight-card">{emoji}&nbsp;&nbsp;{msg}</div>',
                unsafe_allow_html=True
            )


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 2 — ADD TRANSACTION
# ──────────────────────────────────────────────────────────────────────────────

def page_add_transaction():
    st.markdown("""
    <div class="page-title">
        <span class="page-title-text">Add Transaction</span>
        <span class="page-title-badge">New Entry</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Transaction Details</div>', unsafe_allow_html=True)

    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            txn_date = st.date_input(
                "📅 Date",
                value=date.today(),
                max_value=date.today(),
            )
            txn_type = st.selectbox("💳 Type", ["Expense", "Income"])

        with col2:
            category_options = EXPENSE_CATEGORIES if txn_type == "Expense" else INCOME_CATEGORIES
            category = st.selectbox("🏷️ Category", category_options)
            amount = st.number_input(
                "💰 Amount (₹)",
                min_value=0.01, max_value=10_000_000.0,
                step=1.0, format="%.2f",
            )

        description = st.text_input(
            "📝 Description",
            placeholder="e.g. Monthly grocery run, Freelance project...",
            max_chars=100,
        )

        submitted = st.form_submit_button("💾 Save Transaction")

    if submitted:
        success, message = save_transaction(
            date=str(txn_date),
            txn_type=txn_type,
            category=category,
            amount=amount,
            description=description
        )
        if success:
            st.success(message)
            refresh()
        else:
            st.error(f"❌ {message}")

    # ── Recent Transactions ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">Recent Transactions</div>', unsafe_allow_html=True)

    df = get_data()

    if df.empty:
        st.info("No transactions yet. Add one above to get started!")
    else:
        recent = df.tail(5).copy()
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
        recent = recent.iloc[::-1].reset_index(drop=True)
        recent["Amount"] = recent["Amount"].apply(lambda x: f"₹{x:,.2f}")

        # ✅ FIX: use .map() instead of deprecated .applymap() (pandas >= 2.1)
        styled = _safe_style(recent, col="Type")
        st.dataframe(styled, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 3 — TRANSACTIONS
# ──────────────────────────────────────────────────────────────────────────────

def page_transactions():
    st.markdown("""
    <div class="page-title">
        <span class="page-title-text">Transaction History</span>
        <span class="page-title-badge">All Records</span>
    </div>
    """, unsafe_allow_html=True)

    df = get_data()

    if df.empty:
        st.info("ℹ️ No transactions found. Use 'Add Transaction' to get started.")
        return

    # ── Filters ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Filter & Search</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)

    with f1:
        min_date, max_date = get_date_range()
        date_from = st.date_input("From Date", value=min_date, key="txn_from")
        date_to = st.date_input("To Date", value=max_date, key="txn_to")

    with f2:
        all_types = ["All"] + df["Type"].unique().tolist()
        selected_type = st.selectbox("Transaction Type", all_types)

        all_cats = ["All"] + sorted(df["Category"].unique().tolist())
        selected_cat = st.selectbox("Category", all_cats)

    with f3:
        sort_by = st.selectbox("Sort By", [
            "Date (Newest)", "Date (Oldest)",
            "Amount (High→Low)", "Amount (Low→High)"
        ])
        search_term = st.text_input("🔍 Search Description",
                                    placeholder="e.g. grocery...")

    # ── Apply Filters ──────────────────────────────────────────────────────
    filtered = df.copy()
    filtered = filtered[
        (filtered["Date"].dt.date >= date_from) &
        (filtered["Date"].dt.date <= date_to)
    ]

    if selected_type != "All":
        filtered = filtered[filtered["Type"] == selected_type]

    if selected_cat != "All":
        filtered = filtered[filtered["Category"] == selected_cat]

    if search_term:
        filtered = filtered[
            filtered["Description"].str.contains(search_term, case=False, na=False)
        ]

    sort_map = {
        "Date (Newest)": ("Date", False),
        "Date (Oldest)": ("Date", True),
        "Amount (High→Low)": ("Amount", False),
        "Amount (Low→High)": ("Amount", True),
    }
    sort_col, ascending = sort_map[sort_by]
    filtered = filtered.sort_values(sort_col, ascending=ascending).reset_index(drop=True)

    # ── Results ────────────────────────────────────────────────────────────
    st.markdown(f'<div class="section-label">{len(filtered)} Transactions Found</div>',
                unsafe_allow_html=True)

    if filtered.empty:
        st.warning("No transactions match your filters.")
        return

    display = filtered.copy()
    display["Date"] = display["Date"].dt.strftime("%Y-%m-%d")
    display["Amount"] = display["Amount"].apply(lambda x: f"₹{x:,.2f}")

    # ✅ FIX: use .map() instead of deprecated .applymap() (pandas >= 2.1)
    styled = _safe_style(display, col="Type")
    st.dataframe(styled, use_container_width=True, hide_index=True, height=420)

    # ── Delete ─────────────────────────────────────────────────────────────
    with st.expander("🗑️ Delete a Transaction"):
        st.warning("Deletion is permanent. Use row number from the table above (1-indexed).")
        row_num = st.number_input("Row number to delete", min_value=1,
                                   max_value=len(filtered), step=1)
        if st.button("Delete Transaction", key="del_btn"):
            original_idx = filtered.index[row_num - 1]
            ok, msg = delete_transaction(original_idx)
            if ok:
                st.success(msg)
                refresh()
                st.rerun()
            else:
                st.error(msg)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 4 — SPENDING ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def page_spending_analysis():
    st.markdown("""
    <div class="page-title">
        <span class="page-title-text">Spending Analysis</span>
        <span class="page-title-badge">Analytics</span>
    </div>
    """, unsafe_allow_html=True)

    df = get_data()

    if df.empty:
        st.info("ℹ️ No data to analyse yet. Add some transactions first.")
        return

    # ── Category Stats ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Spending by Category</div>', unsafe_allow_html=True)

    cat_df = spending_percentage_by_category(df)
    if not cat_df.empty:
        cat_display = cat_df.copy()
        cat_display["Amount"] = cat_display["Amount"].apply(lambda x: f"₹{x:,.2f}")
        cat_display["Percentage"] = cat_display["Percentage"].apply(lambda x: f"{x}%")
        st.dataframe(cat_display, use_container_width=True, hide_index=True)

    high_cat, low_cat = highest_and_lowest_categories(df)
    h, l = st.columns(2)
    h.metric("🔴 Highest Spending", high_cat)
    l.metric("🟢 Lowest Spending", low_cat)

    st.markdown("---")

    # ── Chart Tabs ─────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🥧 Category Breakdown",
        "📅 Monthly Expenses",
        "💹 Income vs Expenses",
        "📈 Category Trends"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.pyplot(pie_chart_by_category(df))
        with c2:
            st.pyplot(horizontal_bar_by_category(df))

    with tab2:
        monthly = monthly_summary(df)
        st.pyplot(bar_chart_monthly_expenses(monthly))

        if not monthly.empty:
            d = monthly.copy()
            for col in ["Income", "Expenses", "Savings"]:
                d[col] = d[col].apply(lambda x: f"₹{x:,.2f}")
            d["Savings_Pct"] = d["Savings_Pct"].apply(lambda x: f"{x}%")
            st.dataframe(d, use_container_width=True, hide_index=True)

    with tab3:
        monthly = monthly_summary(df)
        st.pyplot(grouped_bar_income_vs_expense(monthly))

        avg_inc = average_monthly_income(df)
        avg_exp = average_monthly_expenses(df)
        st.markdown(f"""
        | Metric | Value |
        |---|---|
        | Average Monthly Income | ₹{avg_inc:,.2f} |
        | Average Monthly Expenses | ₹{avg_exp:,.2f} |
        | Average Monthly Net | ₹{avg_inc - avg_exp:,.2f} |
        """)

    with tab4:
        mom = category_month_over_month_change(df)
        if mom.empty:
            st.info("Need at least 2 months of data for trend analysis.")
        else:
            st.markdown("**Month-over-Month Change by Category**")

            def color_change(val):
                try:
                    num = float(str(val).replace("%", "").replace("₹", "").replace(",", ""))
                    if num > 0:
                        return "color: #F87171; font-weight: 600;"
                    elif num < 0:
                        return "color: #34D399; font-weight: 600;"
                except Exception:
                    pass
                return ""

            d_mom = mom.copy()
            for col in ["Last_Month", "This_Month", "Change"]:
                d_mom[col] = d_mom[col].apply(lambda x: f"₹{x:,.2f}")
            d_mom["Change_Pct"] = d_mom["Change_Pct"].apply(lambda x: f"{x}%")

            # ✅ FIX: use .map() for pandas >= 2.1
            try:
                styled_mom = d_mom.style.map(color_change, subset=["Change", "Change_Pct"])
            except AttributeError:
                styled_mom = d_mom.style.applymap(color_change, subset=["Change", "Change_Pct"])

            st.dataframe(styled_mom, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 5 — BUDGET
# ──────────────────────────────────────────────────────────────────────────────

def page_budget():
    st.markdown("""
    <div class="page-title">
        <span class="page-title-text">Budget Tracker</span>
        <span class="page-title-badge">Monthly Goals</span>
    </div>
    """, unsafe_allow_html=True)

    df = get_data()

    if "budgets" not in st.session_state:
        st.session_state.budgets = {
            "Food": 3000, "Transport": 1000, "Education": 2000,
            "Shopping": 2000, "Entertainment": 1500, "Bills": 1500,
            "Healthcare": 1000, "Other": 500,
        }

    # ── Budget Editor ──────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Set Monthly Budgets (₹)</div>', unsafe_allow_html=True)

    with st.expander("⚙️ Edit Budgets", expanded=False):
        cols = st.columns(4)
        new_budgets = {}
        for i, (cat, default_val) in enumerate(st.session_state.budgets.items()):
            with cols[i % 4]:
                new_budgets[cat] = st.number_input(
                    cat, min_value=0, max_value=100_000,
                    value=int(default_val), step=100, key=f"budget_{cat}"
                )
        if st.button("💾 Save Budgets"):
            st.session_state.budgets = new_budgets
            st.success("Budgets updated!")

    # ── Actual spending this month ─────────────────────────────────────────
    now = datetime.now()
    monthly_expenses = df[
        (df["Type"] == "Expense") &
        (df["Date"].dt.year == now.year) &
        (df["Date"].dt.month == now.month)
    ]
    actual_by_cat = monthly_expenses.groupby("Category")["Amount"].sum()

    budget_rows = []
    for cat, budget_amt in st.session_state.budgets.items():
        actual = actual_by_cat.get(cat, 0.0)
        remaining = budget_amt - actual
        pct_used = round((actual / budget_amt * 100), 1) if budget_amt > 0 else 0.0
        budget_rows.append({
            "Category": cat, "Budget": budget_amt,
            "Actual": actual, "Remaining": remaining, "% Used": pct_used,
        })

    budget_df = pd.DataFrame(budget_rows)

    # ── Budget Chart ───────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Budget vs Actual Chart</div>', unsafe_allow_html=True)
    st.pyplot(budget_vs_actual_chart(budget_df))

    # ── Per-category rows ──────────────────────────────────────────────────
    st.markdown(f'<div class="section-label">{now.strftime("%B %Y")} — Category Breakdown</div>',
                unsafe_allow_html=True)

    for _, row in budget_df.iterrows():
        pct = row["% Used"]
        if pct >= 100:
            status, status_color = "🔴 Over Budget", "#F87171"
        elif pct >= 80:
            status, status_color = "🟡 Near Limit", "#FBBF24"
        else:
            status, status_color = "🟢 On Track", "#34D399"

        col_cat, col_prog = st.columns([1, 3])

        with col_cat:
            st.markdown(f"""
            <div class="budget-row">
                <div class="budget-cat">{row['Category']}</div>
                <div class="budget-nums">
                    ₹{row['Actual']:,.0f} of ₹{row['Budget']:,.0f}
                    &nbsp;·&nbsp; Remaining: ₹{row['Remaining']:,.0f}
                </div>
                <div class="budget-status" style="color:{status_color};">
                    {status} — {pct}% used
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_prog:
            st.markdown("<br>", unsafe_allow_html=True)
            st.progress(min(pct / 100, 1.0))


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 6 — SAVINGS PREDICTION
# ──────────────────────────────────────────────────────────────────────────────

def page_savings_prediction():
    st.markdown("""
    <div class="page-title">
        <span class="page-title-text">Savings Prediction</span>
        <span class="page-title-badge">Forecast</span>
    </div>
    """, unsafe_allow_html=True)

    df = get_data()

    st.info(
        "📢 **Disclaimer:** This is a statistical *estimate* based on your historical data. "
        "It is **not** financial advice. Actual results may vary."
    )

    prediction = predict_next_month_savings(df)

    if prediction["months_used"] == 0:
        st.warning("Not enough data. Add at least 1 month of transactions to generate a forecast.")
        return

    # ── Method Explainer ───────────────────────────────────────────────────
    with st.expander("🧠 How does this prediction work?", expanded=False):
        st.markdown(f"""
        ### Prediction Method

        **Formula:** `Predicted Savings = Predicted Income − Predicted Expenses`

        **Method used:** `{prediction['method']}`

        **Steps:**
        1. **Monthly aggregation** — Transactions grouped by calendar month
        2. **Moving average** — Average of the last {prediction['months_used']} month(s) to smooth spikes
        3. **Linear trend** _(if ≥ 4 months)_ — `np.polyfit()` slope added as monthly adjustment
        4. **Savings estimate** — Predicted income minus predicted expenses

        **Confidence level:** `{prediction['confidence']}`
        - *Low* → < 3 months of data
        - *Medium* → 3–5 months
        - *High* → 6+ months

        > This uses **simple statistics, not machine learning** — making it fully explainable
        > and ideal for a college project demonstration.
        """)

    # ── Prediction KPIs ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Next Month Forecast</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)

    def pred_kpi(col, icon, label, value, color):
        col.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-label">{label}</div>
            <div class="kpi-amount" style="color:{color};">{value}</div>
            <div class="kpi-change">Estimated — next month</div>
        </div>
        """, unsafe_allow_html=True)

    pred_kpi(p1, "💵", "Predicted Income",
             f"₹{prediction['predicted_income']:,.0f}", "#34D399")
    pred_kpi(p2, "💸", "Predicted Expenses",
             f"₹{prediction['predicted_expenses']:,.0f}", "#F87171")
    pred_kpi(p3, "📈", "Predicted Savings",
             f"₹{prediction['predicted_savings']:,.0f}",
             "#34D399" if prediction["predicted_savings"] >= 0 else "#F87171")
    pred_kpi(p4, "🎯", "Savings Rate",
             f"{prediction['predicted_savings_pct']}%",
             "#34D399" if prediction["predicted_savings_pct"] >= 20 else "#FBBF24")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Savings Trend Chart ─────────────────────────────────────────────────
    st.markdown('<div class="section-label">Savings Trend + Forecast</div>', unsafe_allow_html=True)
    trend_df = savings_trend_with_forecast(df)
    st.pyplot(line_chart_savings_trend(trend_df))

    # ── Historical Table ───────────────────────────────────────────────────
    st.markdown('<div class="section-label">Historical Monthly Data</div>', unsafe_allow_html=True)
    monthly = prediction["monthly_data"]
    if not monthly.empty:
        d = monthly.copy()
        for col in ["Income", "Expenses", "Savings"]:
            d[col] = d[col].apply(lambda x: f"₹{x:,.2f}")
        d["Savings_Pct"] = d["Savings_Pct"].apply(lambda x: f"{x}%")
        st.dataframe(d, use_container_width=True, hide_index=True)


# ─── Router ───────────────────────────────────────────────────────────────────

if page == "🏠  Dashboard":
    page_dashboard()
elif page == "➕  Add Transaction":
    page_add_transaction()
elif page == "📋  Transactions":
    page_transactions()
elif page == "📊  Spending Analysis":
    page_spending_analysis()
elif page == "💰  Budget":
    page_budget()
elif page == "🔮  Savings Prediction":
    page_savings_prediction()
