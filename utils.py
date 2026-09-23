"""Utility helpers used across the Smart Card Benefit Recommender app."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def format_currency(amount: float | int | None, show_zero: bool = True) -> str:
    """Format a number as Indian Rupees using Indian digit grouping.

    Examples:
        5000 -> ₹5,000
        125000 -> ₹1,25,000

    The helper is intentionally simple so it can be explained in a viva as
    string formatting rather than a finance library dependency.
    """
    if amount is None:
        return "₹0" if show_zero else "-"

    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError):
        return "₹0" if show_zero else "-"

    sign = "-" if numeric_amount < 0 else ""
    numeric_amount = abs(numeric_amount)

    if numeric_amount == int(numeric_amount):
        whole_part = str(int(numeric_amount))
        decimal_part = ""
    else:
        whole_part, decimal_part = f"{numeric_amount:.2f}".split(".")
        decimal_part = f".{decimal_part}"

    if len(whole_part) > 3:
        last_three = whole_part[-3:]
        leading_digits = whole_part[:-3]
        grouped_leading = []

        while len(leading_digits) > 2:
            grouped_leading.insert(0, leading_digits[-2:])
            leading_digits = leading_digits[:-2]

        if leading_digits:
            grouped_leading.insert(0, leading_digits)

        formatted_whole = ",".join(grouped_leading + [last_three])
    else:
        formatted_whole = whole_part

    return f"{sign}₹{formatted_whole}{decimal_part}"


def format_percentage(rate: float | int | None) -> str:
    """Display reward rates without noisy trailing zeros."""
    if rate is None:
        return "0%"

    value = float(rate)
    if value == int(value):
        return f"{int(value)}%"
    return f"{value:.2f}%"


def clean_text(value: Any) -> str:
    """Normalize text fields before saving them to SQLite."""
    return str(value or "").strip()


def today_iso() -> str:
    """Return today's date in ISO format for database defaults."""
    return date.today().isoformat()


def parse_iso_date(value: str | date | datetime | None) -> date | None:
    """Convert supported date values into a date object."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def get_custom_css() -> str:
    """Central place for the Streamlit visual polish."""
    return """
    <style>
        :root {
            --accent: #635bff;
            --accent-strong: #4f46e5;
            --accent-soft: #eef0ff;
            --blue-soft: #dceeff;
            --canvas: #f6f7fb;
            --panel: #ffffff;
            --ink: #171a27;
            --muted: #727789;
            --line: #e8eaf0;
            --shadow: 0 8px 24px rgba(31, 38, 65, 0.06);
        }

        .stApp { background: var(--canvas); }
        .main .block-container {
            padding: 1.55rem 2rem 4rem;
            max-width: 1320px;
        }

        h1, h2, h3, p { letter-spacing: 0; }
        h1, h2, h3 { color: var(--ink); }
        h1 { font-size: 1.85rem !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1rem !important; }

        section[data-testid="stSidebar"] {
            background: var(--panel);
            border-right: 1px solid var(--line);
            box-shadow: none;
        }
        section[data-testid="stSidebar"] * { color: var(--ink); }
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            padding: 0.58rem 0.72rem;
            margin-bottom: 0.18rem;
            border-radius: 8px;
            transition: 140ms ease;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: #f5f6fa;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: var(--accent-soft);
            color: var(--accent-strong);
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 38px;
            height: 38px;
            margin: 0.15rem 0 1rem;
            border-radius: 10px;
            background: var(--accent);
            color: white !important;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.04em !important;
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            box-shadow: var(--shadow);
            min-height: 104px;
        }
        div[data-testid="stMetric"] label {
            color: var(--muted);
            font-size: 0.82rem;
        }
        div[data-testid="stMetricValue"] {
            color: var(--ink);
            font-weight: 750;
            font-size: 1.45rem;
            white-space: normal;
            overflow-wrap: anywhere;
        }

        .app-header {
            background: transparent;
            border: 0;
            padding: 0.2rem 0 1.15rem;
            margin-bottom: 1rem;
            box-shadow: none;
        }
        .app-header h1 { margin: 0.25rem 0 0; line-height: 1.15; }
        .app-header p {
            color: var(--muted);
            margin: 0.35rem 0 0;
            font-size: 0.94rem;
        }

        .soft-panel, .card-shell {
            background: var(--panel);
            border: 1px solid var(--line) !important;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: var(--shadow);
            margin: 1rem 0;
        }

        .recommendation-box {
            background: #20233a;
            color: white;
            border-radius: 14px;
            padding: 1.4rem;
            margin: 1.25rem 0;
            box-shadow: var(--shadow);
            border-left: 5px solid #8ea7ff;
        }
        .recommendation-box h2,
        .recommendation-box h3,
        .recommendation-box p {
            color: white;
            margin-top: 0;
        }

        .card-title {
            color: var(--ink);
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.15rem;
        }
        .card-subtitle {
            color: var(--muted);
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
        }
        .pill {
            display: inline-block;
            background: var(--accent-soft);
            color: var(--accent-strong);
            border: 1px solid #dfe2ff;
            border-radius: 7px;
            padding: 0.25rem 0.55rem;
            font-size: 0.82rem;
            margin: 0.12rem 0.12rem 0.12rem 0;
        }

        .empty-state {
            background: var(--panel);
            border: 1px dashed #d6d9e2;
            border-radius: 12px;
            color: var(--muted);
            padding: 1.4rem;
            text-align: center;
        }

        .stButton > button {
            border-radius: 9px;
            border: 1px solid var(--line);
            font-weight: 600;
            background: var(--panel);
            color: var(--ink);
            box-shadow: none;
            transition: 140ms ease;
        }
        .stButton > button:hover {
            color: var(--accent-strong);
            border-color: #cfd3ff;
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
            background: var(--accent);
            color: white;
            border: 0;
            box-shadow: 0 6px 14px rgba(99, 91, 255, 0.22);
        }
        div[data-testid="stLinkButton"] a {
            background: var(--panel) !important;
            border: 1px solid var(--line) !important;
            border-radius: 9px !important;
            color: var(--accent-strong) !important;
            min-height: 2.35rem;
        }
        div[data-testid="stLinkButton"] a p { color: var(--accent-strong) !important; }

        .eyebrow, .card-kicker {
            color: var(--accent-strong);
            font-size: 0.72rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.08em !important;
        }
        .eyebrow.light { color: #cdd6ff; }

        .trust-strip {
            display: flex;
            gap: 1.2rem;
            align-items: center;
            flex-wrap: wrap;
            padding: 0.72rem 0.9rem;
            margin-bottom: 1rem;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 10px;
            color: var(--muted);
            font-size: 0.84rem;
        }
        .trust-strip strong { color: var(--accent-strong); }
        .card-fee { margin: 0.8rem 0 0; color: #475569; }
        .card-note { margin: 0.65rem 0 0; color: #334155; font-size: 0.9rem; }
        .result-reason { margin-bottom: 0 !important; color: #dbe2ff !important; }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 12px;
            overflow: hidden;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.2rem;
            padding: 0.25rem;
            border-radius: 10px;
            background: #eceef5;
        }
        div[data-baseweb="tab"] { border-radius: 8px; padding: 0.48rem 0.9rem; }
        div[data-baseweb="tab"][aria-selected="true"] {
            background: var(--panel);
            color: var(--accent-strong);
            box-shadow: 0 2px 8px rgba(31, 38, 65, 0.08);
        }

        .dashboard-insight { min-height: 135px; }
        .dashboard-insight p { color: var(--muted); margin: 0.45rem 0 0; font-size: 0.88rem; }
        .insight-value { color: var(--accent-strong); font-size: 2rem; font-weight: 760; margin-top: 0.35rem; }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-testid="stDateInput"] div[data-baseweb="input"] > div {
            background: #f9fafe !important;
            border: 1px solid var(--line) !important;
            border-radius: 9px !important;
            box-shadow: none;
        }

        div[data-testid="stPlotlyChart"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 0.4rem;
            box-shadow: var(--shadow);
            width: 100% !important;
            overflow: hidden;
        }
        div[data-testid="stPlotlyChart"] > div,
        div[data-testid="stPlotlyChart"] .js-plotly-plot,
        div[data-testid="stPlotlyChart"] .plot-container { width: 100% !important; }

        div[data-testid="stExpander"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            box-shadow: none;
            overflow: hidden;
        }

        div[data-testid="stForm"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: var(--shadow);
        }

        div[data-testid="stAlert"] { border-radius: 10px; border: 0; }
        hr { border-color: rgba(113, 119, 139, 0.15); }

        @media (max-width: 768px) {
            .main .block-container { padding: 0.85rem 0.72rem 3rem; }
            .trust-strip { align-items: flex-start; flex-direction: column; gap: 0.25rem; }
            .app-header { padding: 0.1rem 0 0.8rem; }
            .app-header h1 { font-size: 1.45rem !important; }
            .app-header p { font-size: 0.86rem; }
            div[data-testid="stMetric"] { min-height: 88px; padding: 0.75rem; }
            div[data-testid="stMetricValue"] { font-size: 1.18rem; }
            .recommendation-box { border-radius: 12px; padding: 1rem; }
            .recommendation-box h2 { font-size: 1.08rem !important; overflow-wrap: anywhere; }
            div[data-baseweb="tab-list"] { overflow-x: auto; white-space: nowrap; }
            div[data-baseweb="tab"] { padding: 0.42rem 0.55rem; font-size: 0.76rem; }
            div[data-testid="stPlotlyChart"] { padding: 0.1rem; box-shadow: none; }
            div[data-testid="stPlotlyChart"] .modebar { display: none !important; }
            .card-shell { padding: 0.85rem; }
            .pill { font-size: 0.74rem; padding: 0.2rem 0.42rem; }
        }

        @media (max-width: 480px) {
            h2 { font-size: 1.12rem !important; }
            h3 { font-size: 0.95rem !important; }
            .main .block-container { padding-left: 0.58rem; padding-right: 0.58rem; }
            div[data-testid="stForm"] { padding: 0.72rem; }
        }
    </style>
    """
