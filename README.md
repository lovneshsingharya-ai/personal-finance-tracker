# 💸 Personal Finance Tracker Dashboard

A complete, interactive **Personal Finance Analytics Application** built with Python, Pandas, Matplotlib, and Streamlit — designed as a college data-science project.

---

## 📋 Project Overview

Managing personal finances is a critical life skill, especially for college students on tight budgets. This application provides a real-world tool to:

- Record daily income and expenses
- Visualise spending patterns
- Track budget goals
- Predict future savings using statistical methods

---

## ❓ Problem Statement

College students often lack visibility into their spending habits. Without a clear picture of where money goes, saving consistently is nearly impossible. This project solves that by providing an intuitive dashboard that turns raw transaction data into actionable financial insights.

---

## 🎯 Objectives

1. Provide an easy way to log daily transactions
2. Analyse spending patterns by category and over time
3. Visualise income vs. expenses with meaningful charts
4. Predict next month's savings using historical data
5. Generate automatic insights from actual calculations
6. Track budgets per category with visual feedback

---

## ✨ Features

| Feature | Description |
|---|---|
| 🏠 Dashboard | KPI cards for income, expenses, balance, savings |
| ➕ Add Transaction | Form with validation to record income/expenses |
| 📋 Transactions | Filterable, searchable transaction history |
| 📊 Spending Analysis | Category breakdown, monthly trends, charts |
| 💰 Budget Tracker | Set budgets per category and track usage |
| 🔮 Savings Prediction | Moving average + linear trend forecasting |
| 💡 Auto Insights | Computed tips and observations from real data |

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core programming language |
| Pandas | Data loading, cleaning, grouping, aggregation |
| Matplotlib | Chart rendering (pie, bar, line, horizontal bar) |
| Streamlit | Interactive web dashboard |
| NumPy | Numerical calculations, linear regression |
| CSV | Simple local data storage |
| Datetime | Date parsing and validation |

---

## 📁 Project Structure

```
personal-finance-tracker/
│
├── app.py                    ← Main Streamlit application (entry point)
│
├── data/
│   └── transactions.csv      ← Transaction data (auto-created if missing)
│
├── modules/
│   ├── data_manager.py       ← CSV read/write, validation
│   ├── analytics.py          ← Pandas analysis (summaries, trends, stats)
│   ├── predictions.py        ← Moving average + trend savings forecast
│   └── insights.py           ← Auto-generated financial insights
│
├── charts/
│   └── visualizations.py     ← All Matplotlib chart functions
│
├── requirements.txt          ← Python package dependencies
└── README.md                 ← This file
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.10 or later
- pip (Python package manager)

### Steps

1. **Clone or download** this project folder.

2. **Open a terminal** and navigate to the project directory:
   ```bash
   cd path/to/personal-finance-tracker
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ How to Run

```bash
streamlit run app.py
```

Streamlit will open the dashboard automatically in your default browser at:
```
http://localhost:8501
```

---

## 📊 How Each Component Works

### `data_manager.py` — Data Layer
- Loads `transactions.csv` using `pd.read_csv()`
- Parses dates with `pd.to_datetime()` and coerces errors
- Validates every new transaction before saving (date, amount, type, category)
- Appends new rows to the CSV without overwriting existing data
- Auto-creates the CSV file with headers if it does not exist

### `analytics.py` — Analysis Layer
- **`get_summary()`** — Aggregates totals using `df.groupby()` and `sum()`
- **`monthly_summary()`** — Groups by `dt.to_period("M")` for month-level views
- **`spending_by_category()`** — Filters expenses and groups by category
- **`consecutive_increase_categories()`** — Detects 3-month upward trends
- **`category_month_over_month_change()`** — Pivot table diff between last two months

### `predictions.py` — Prediction Layer
- **Moving average** — `df.tail(N).mean()` over the last N months
- **Linear trend** — `np.polyfit(x, y, 1)` to get the slope (expected monthly change)
- **Confidence levels** — Based on the number of months available
- **Forecast row** — Added as a separate data point on the savings chart

### `insights.py` — Insights Layer
- Each insight is computed from real aggregations (no hard-coded strings)
- Checks savings rate, month-over-month changes, consecutive trends
- Returns `(emoji, message)` tuples rendered as styled cards in the dashboard

### `visualizations.py` — Chart Layer
- All charts use Matplotlib with a custom dark theme
- `matplotlib.use("Agg")` ensures compatibility with Streamlit (no display window)
- Each function accepts a DataFrame and returns a `plt.Figure` object

### `app.py` — Presentation Layer
- Streamlit sidebar navigation using `st.radio()`
- Custom CSS injected via `st.markdown(unsafe_allow_html=True)` for dark theme
- `@st.cache_data(ttl=5)` caches data reads to avoid re-reading the CSV every second
- Session state (`st.session_state`) stores budget values between reruns

---

## 🖼️ Screenshots

> _Add your own screenshots here after running the application._

| Dashboard | Spending Analysis |
|---|---|
| _(screenshot)_ | _(screenshot)_ |

| Budget Tracker | Savings Prediction |
|---|---|
| _(screenshot)_ | _(screenshot)_ |

---

## 🎓 Demonstrating at a College Viva

### Suggested Demo Flow

1. **Open the Dashboard** — Show the KPI cards and explain the key metrics.
2. **Add a Transaction** — Live demo of adding an expense with validation (try entering a negative amount to show error handling).
3. **Transactions page** — Filter by category, search by description, sort by amount.
4. **Spending Analysis** — Walk through all 4 tabs: pie chart, monthly bar, income vs expenses, MoM trends.
5. **Budget Tracker** — Set a budget, show a category that is over budget (red bar).
6. **Savings Prediction** — Expand the "How it works" section and explain the method step-by-step.

### Key Talking Points for Viva

- **Why CSV instead of a database?** Simple, human-readable, no setup required for a demo. Easily upgradeable to SQLite.
- **Why not machine learning?** Statistical methods are transparent, explainable, and appropriate for a small dataset. ML requires far more data to be reliable.
- **How is data validated?** All inputs pass through `save_transaction()` which checks types, ranges, and formats before writing to disk.
- **How are insights generated?** From real Pandas calculations, not template strings. Show the `insights.py` file.
- **What does `@st.cache_data` do?** Prevents re-reading the CSV file on every widget interaction, improving performance.

---

## 🚀 Future Improvements

| Improvement | Description |
|---|---|
| 🗄️ SQLite Database | Replace CSV with a relational database for better performance |
| 🔐 User Authentication | Multi-user support with login/logout |
| 🤖 ML Forecasting | Use scikit-learn or Prophet for time-series prediction |
| 🏦 Bank Statement Import | Parse PDF/CSV bank statements automatically |
| 📄 PDF Reports | Export monthly financial reports as PDF |
| ☁️ Cloud Deployment | Deploy to Streamlit Cloud, Heroku, or AWS |
| 📱 Mobile-Friendly UI | Responsive layout for phone screens |
| 🎯 Smart Recommendations | Personalised savings goals and alerts |
| 📧 Email Alerts | Notify when spending exceeds budget thresholds |
| 🌍 Multi-Currency Support | Handle international transactions |

---

## 📄 License

This project is created for educational purposes as a college minor project.

---

*Built with ❤️ using Python, Pandas, Matplotlib, and Streamlit.*
