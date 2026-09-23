"""Streamlit interface for the Smart Card Benefit Recommender."""

from __future__ import annotations

from datetime import date
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import (
    build_dashboard_metrics,
    missed_rewards_this_month,
    monthly_spending,
    most_used_card,
    most_valuable_card,
    rewards_by_card,
    spending_by_category,
    transactions_to_dataframe,
)
from calculators import calculate_annual_card_values, calculate_emi, calculate_utilisation
from cards import (
    CARD_PROFILES,
    CARD_TYPES,
    CATEGORIES,
    CATEGORY_RATE_COLUMNS,
    DATASET_REVIEW_DATE,
    REWARD_TYPES,
    validate_card_data,
)
from database import (
    add_card,
    add_transaction,
    delete_card,
    get_cards,
    get_transactions,
    initialize_database,
    load_demo_cards,
    reset_database,
    update_card,
)
from recommender import calculate_reward, get_card_reward_rate, recommend_best_card
from utils import clean_text, format_currency, format_percentage, get_custom_css


NAVIGATION_ITEMS = [
    "Overview",
    "Best Card",
    "Card Library",
    "Calculators",
    "Analytics",
    "History",
    "Add Card",
    "Settings",
]

VIOLET_SCALE = ["#dceeff", "#a9d1ff", "#7b9cff", "#635bff"]
PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}

def rerun_app() -> None:
    """Rerun the app after database-changing actions."""
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def safe_index(options: list[str], value: str) -> int:
    """Return the index of a value, falling back to the first option."""
    try:
        return options.index(value)
    except ValueError:
        return 0


def render_header(title: str, subtitle: str) -> None:
    """Render a consistent page header."""
    st.markdown(
        f"""
        <div class="app-header">
            <span class="eyebrow">SMARTCARD INDIA</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str) -> None:
    """Render a polished empty-state box."""
    st.markdown(
        f"""<div class="empty-state">{message}</div>""",
        unsafe_allow_html=True,
    )


def style_chart(figure, height: int | None = None):
    """Apply the shared neumorphic chart treatment."""
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#44495b", family="Arial, sans-serif", size=11),
        hoverlabel=dict(bgcolor="#ffffff", font_color="#222536", bordercolor="#635bff"),
        margin=dict(l=14, r=14, t=24, b=14),
        height=height,
        autosize=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    figure.update_xaxes(gridcolor="rgba(99,91,255,0.08)", zeroline=False)
    figure.update_yaxes(gridcolor="rgba(99,91,255,0.08)", zeroline=False)
    return figure


def compact_card_name(card_name: str) -> str:
    """Return a short chart label that remains readable on mobile."""
    replacements = {
        "CASHBACK SBI Card": "SBI Cashback",
        "Amazon Pay ICICI Bank Credit Card": "Amazon ICICI",
        "HDFC Bank Millennia Credit Card": "HDFC Millennia",
        "Flipkart Axis Bank Credit Card": "Flipkart Axis",
        "Axis Bank Freecharge Plus Credit Card": "Axis Freecharge+",
    }
    return replacements.get(card_name, card_name[:22])


def collect_reward_rates(prefix: str, existing_card: dict | None = None) -> dict[str, float]:
    """Create category reward-rate inputs and return their values."""
    reward_rates: dict[str, float] = {}
    columns = st.columns(3)

    for index, (category, column_name) in enumerate(CATEGORY_RATE_COLUMNS.items()):
        with columns[index % 3]:
            default_value = 0.0
            if existing_card:
                default_value = float(existing_card.get(column_name) or 0)

            reward_rates[column_name] = st.number_input(
                f"{category} (%)",
                min_value=0.0,
                max_value=100.0,
                value=default_value,
                step=0.1,
                key=f"{prefix}_{column_name}",
            )

    return reward_rates


def build_card_form_payload(
    card_name: str,
    bank_name: str,
    card_type: str,
    annual_fee: float,
    reward_type: str,
    reward_rates: dict[str, float],
) -> dict:
    """Collect card form values into one dictionary."""
    payload = {
        "card_name": card_name,
        "bank_name": bank_name,
        "card_type": card_type,
        "annual_fee": annual_fee,
        "reward_type": reward_type,
    }
    payload.update(reward_rates)
    return payload


def get_card_summary_html(card: dict) -> str:
    """Build a small visual summary for one saved card."""
    reward_pills = []
    for category, column_name in CATEGORY_RATE_COLUMNS.items():
        reward_pills.append(
            f'<span class="pill">{category}: {format_percentage(card[column_name])}</span>'
        )

    profile = CARD_PROFILES.get(card["card_name"], {})
    accent = profile.get("accent", "#0f766e")
    return f"""
    <div class="card-shell" style="border-top-color: {accent};">
        <div class="card-kicker">{escape(profile.get("best_for", "CUSTOM CARD").upper())}</div>
        <div class="card-title">{escape(card["card_name"])}</div>
        <div class="card-subtitle">{escape(card["bank_name"])} · {escape(card["card_type"])} · {escape(card["reward_type"])}</div>
        <div>{"".join(reward_pills)}</div>
        <p class="card-fee">
            Annual Fee: <strong>{format_currency(card["annual_fee"])}</strong>
        </p>
        {f'<p class="card-note">Illustrative category model · {escape(profile.get("best_for", ""))}</p>' if profile else ''}
    </div>
    """


def prepare_transactions_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Format transaction rows for display."""
    if dataframe.empty:
        return pd.DataFrame()

    table = dataframe.copy()
    table["Date"] = table["transaction_date"].dt.strftime("%d %b %Y")
    table["Merchant"] = table["merchant"]
    table["Category"] = table["category"]
    table["Amount"] = table["amount"].apply(format_currency)
    table["Recommended Card"] = table["recommended_card"]
    table["Used Card"] = table["used_card"]
    table["Reward"] = table["actual_reward"].apply(format_currency)
    table["Missed Reward"] = table["missed_reward"].apply(format_currency)

    return table[
        [
            "Date",
            "Merchant",
            "Category",
            "Amount",
            "Recommended Card",
            "Used Card",
            "Reward",
            "Missed Reward",
        ]
    ]


def comparison_to_dataframe(comparison: list[dict]) -> pd.DataFrame:
    """Format recommender comparison rows for Streamlit tables."""
    rows = []
    for rank, row in enumerate(comparison, start=1):
        rows.append(
            {
                "Rank": rank,
                "Card": row["card_name"],
                "Bank": row["bank_name"],
                "Reward Type": row["reward_type"],
                "Reward Rate": format_percentage(row["reward_rate"]),
                "Expected Benefit": format_currency(row["expected_benefit"]),
            }
        )
    return pd.DataFrame(rows)


def render_metric_row(metrics: dict) -> None:
    """Show the main dashboard metric cards."""
    column_one, column_two, column_three, column_four = st.columns(4)

    column_one.metric("Total Spending", format_currency(metrics["total_spending"]))
    column_two.metric("Rewards Earned", format_currency(metrics["total_rewards"]))
    column_three.metric("Potential Savings Missed", format_currency(metrics["missed_rewards"]))
    column_four.metric("Cards in Wallet", metrics["cards_added"])


def render_dashboard() -> None:
    """Dashboard page with metrics, recent transactions, and charts."""
    render_header(
        "Smart Card Benefit Recommender",
        "Make every swipe deliberate. Compare rewards, fees, and long-term value across your Indian credit cards.",
    )

    cards = get_cards()
    transactions = get_transactions()
    dataframe = transactions_to_dataframe(transactions)
    metrics = build_dashboard_metrics(transactions, len(cards))
    st.markdown(
        f'<div class="trust-strip"><strong>Illustrative Indian card dataset</strong><span>Example reward rates</span><span>Editable in Card Library</span></div>',
        unsafe_allow_html=True,
    )
    render_metric_row(metrics)

    if cards and dataframe.empty:
        st.info("Start with Best Card for a purchase decision, or use Calculators to compare annual value after fees.")

    section_left, section_right = st.columns([1.65, 1])
    if cards:
        with section_left:
            st.subheader("Card Strength by Category")
            selected_category = st.selectbox(
                "Spending category",
                CATEGORIES,
                index=CATEGORIES.index("Online Shopping"),
                key="dashboard_category",
            )
            rate_column = CATEGORY_RATE_COLUMNS[selected_category]
            comparison_data = pd.DataFrame(
                [
                    {
                        "Card": compact_card_name(card["card_name"]),
                        "Reward rate": float(card.get(rate_column, 0) or 0),
                    }
                    for card in cards
                ]
            ).sort_values("Reward rate", ascending=True)
            reward_chart = px.bar(
                comparison_data,
                x="Reward rate",
                y="Card",
                orientation="h",
                text="Reward rate",
                color="Reward rate",
                color_continuous_scale=VIOLET_SCALE,
            )
            reward_chart.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                cliponaxis=False,
                hovertemplate="%{y}<br>Reward rate: %{x:.2f}%<extra></extra>",
            )
            reward_chart.update_layout(
                xaxis_title="Reward rate (%)",
                yaxis_title="",
                coloraxis_showscale=False,
                showlegend=False,
                margin=dict(l=10, r=28, t=18, b=12),
            )
            max_rate = float(comparison_data["Reward rate"].max())
            reward_chart.update_xaxes(range=[0, max(1, max_rate * 1.18)])
            st.plotly_chart(style_chart(reward_chart, 340), width="stretch", key="wallet_reward_chart", config=PLOTLY_CONFIG)

        with section_right:
            top_card = max(cards, key=lambda card: float(card.get(rate_column, 0) or 0))
            st.subheader("Wallet Snapshot")
            st.markdown(
                f"""
                <div class="soft-panel dashboard-insight">
                    <span class="eyebrow">TOP FOR {escape(selected_category)}</span>
                    <div class="card-title">{escape(top_card['card_name'])}</div>
                    <div class="insight-value">{format_percentage(top_card[rate_column])}</div>
                    <p>Highest configured example rate for this category.</p>
                </div>
                <div class="soft-panel dashboard-insight">
                    <span class="eyebrow">PORTFOLIO</span>
                    <div class="card-title">{len(cards)} active cards</div>
                    <p>{metrics['total_transactions']} saved transactions · Favourite category: {escape(metrics['favourite_category'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if not dataframe.empty:
        period = st.segmented_control(
            "Dashboard period",
            ["30 days", "90 days", "All time"],
            default="All time",
        )
        if period != "All time":
            days = 30 if period == "30 days" else 90
            cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)
            dataframe = dataframe[dataframe["transaction_date"] >= cutoff]

    st.subheader("Recent Transactions")
    if dataframe.empty:
        render_empty_state("No transactions yet. Use Find Best Card to save your first transaction.")
    else:
        recent = dataframe.sort_values("transaction_date", ascending=False).head(8)
        st.dataframe(prepare_transactions_table(recent), width="stretch", hide_index=True)

    chart_one, chart_two = st.columns(2)

    with chart_one:
        st.subheader("Spending by Category")
        category_data = spending_by_category(dataframe)
        if category_data.empty:
            render_empty_state("Category chart will appear after transactions are saved.")
        else:
            figure = px.pie(
                category_data,
                values="amount",
                names="category",
                hole=0.42,
                color_discrete_sequence=VIOLET_SCALE,
            )
            figure.update_layout(legend_title_text="")
            st.plotly_chart(style_chart(figure, 340), width="stretch", config=PLOTLY_CONFIG)

    with chart_two:
        st.subheader("Rewards by Card")
        rewards_data = rewards_by_card(dataframe)
        if rewards_data.empty:
            render_empty_state("Rewards chart will appear after transaction history exists.")
        else:
            figure = px.bar(
                rewards_data,
                x="used_card",
                y="actual_reward",
                color="used_card",
                color_discrete_sequence=VIOLET_SCALE,
            )
            figure.update_layout(
                xaxis_title="Card",
                yaxis_title="Reward",
                showlegend=False,
            )
            st.plotly_chart(style_chart(figure, 340), width="stretch", config=PLOTLY_CONFIG)


def render_add_card() -> None:
    """Add-card page."""
    render_header(
        "Add Credit Card",
        "Save a card and define category-wise reward percentages.",
    )

    with st.form("add_card_form", clear_on_submit=True):
        first_column, second_column = st.columns(2)
        with first_column:
            card_name = st.text_input("Card Name", placeholder="Example: HDFC Millennia")
            bank_name = st.text_input("Bank Name", placeholder="Example: HDFC Bank")
            card_type = st.selectbox("Card Type", CARD_TYPES)
        with second_column:
            annual_fee = st.number_input("Annual Fee", min_value=0.0, value=0.0, step=100.0)
            reward_type = st.selectbox("Reward Type", REWARD_TYPES)

        st.markdown("#### Reward Rates by Category")
        reward_rates = collect_reward_rates("add")
        submitted = st.form_submit_button("Save Card", type="primary")

    if submitted:
        payload = build_card_form_payload(
            card_name, bank_name, card_type, annual_fee, reward_type, reward_rates
        )
        errors = validate_card_data(payload)

        if errors:
            for error in errors:
                st.error(error)
        else:
            add_card(payload)
            st.success(f"{clean_text(card_name)} was added successfully.")


def render_my_cards() -> None:
    """My Cards page with view, edit, and delete actions."""
    render_header(
        "Card Library",
        "A working wallet of Indian cards with planning rates, issuer terms, and editable assumptions.",
    )

    cards = get_cards()
    if not cards:
        render_empty_state("You have not added any credit cards yet. Add at least one card before using the recommender.")
        return

    for card in cards:
        st.markdown(get_card_summary_html(card), unsafe_allow_html=True)

        profile = CARD_PROFILES.get(card["card_name"])
        if profile:
            st.caption(f"Example percentages only. Issuer context: {profile['fine_print']}")
            st.link_button("Open official issuer terms", profile["source_url"])

        with st.expander(f"Edit, delete, or view benefits for {card['card_name']}"):
            tab_view, tab_edit, tab_delete = st.tabs(["View Benefits", "Edit", "Delete"])

            with tab_view:
                rates_table = pd.DataFrame(
                    [
                        {
                            "Category": category,
                            "Reward Rate": format_percentage(card[column_name]),
                        }
                        for category, column_name in CATEGORY_RATE_COLUMNS.items()
                    ]
                )
                st.dataframe(rates_table, width="stretch", hide_index=True)

            with tab_edit:
                with st.form(f"edit_form_{card['id']}"):
                    first_column, second_column = st.columns(2)
                    with first_column:
                        card_name = st.text_input(
                            "Card Name",
                            value=card["card_name"],
                            key=f"edit_name_{card['id']}",
                        )
                        bank_name = st.text_input(
                            "Bank Name",
                            value=card["bank_name"],
                            key=f"edit_bank_{card['id']}",
                        )
                        card_type = st.selectbox(
                            "Card Type",
                            CARD_TYPES,
                            index=safe_index(CARD_TYPES, card["card_type"]),
                            key=f"edit_type_{card['id']}",
                        )
                    with second_column:
                        annual_fee = st.number_input(
                            "Annual Fee",
                            min_value=0.0,
                            value=float(card["annual_fee"] or 0),
                            step=100.0,
                            key=f"edit_fee_{card['id']}",
                        )
                        reward_type = st.selectbox(
                            "Reward Type",
                            REWARD_TYPES,
                            index=safe_index(REWARD_TYPES, card["reward_type"]),
                            key=f"edit_reward_{card['id']}",
                        )

                    st.markdown("#### Reward Rates by Category")
                    reward_rates = collect_reward_rates(f"edit_{card['id']}", card)
                    submitted = st.form_submit_button("Update Card", type="primary")

                if submitted:
                    payload = build_card_form_payload(
                        card_name,
                        bank_name,
                        card_type,
                        annual_fee,
                        reward_type,
                        reward_rates,
                    )
                    errors = validate_card_data(payload)

                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        update_card(card["id"], payload)
                        st.success(f"{clean_text(card_name)} was updated.")
                        rerun_app()

            with tab_delete:
                st.warning("Deleting a card removes it from future recommendations. Existing transaction history remains.")
                confirm_delete = st.checkbox(
                    f"I confirm that I want to delete {card['card_name']}.",
                    key=f"confirm_delete_{card['id']}",
                )
                if st.button("Delete Card", key=f"delete_{card['id']}"):
                    if confirm_delete:
                        delete_card(card["id"])
                        st.success(f"{card['card_name']} was deleted.")
                        rerun_app()
                    else:
                        st.error("Please tick the confirmation box before deleting.")


def render_recommendation_result(result: dict, amount: float, category: str, merchant: str) -> None:
    """Display the result from the recommendation engine."""
    best_cards = result["best_cards"]
    if not best_cards:
        return

    best_card_names = [row["card_name"] for row in best_cards]
    best_card_label = " / ".join(best_card_names)
    first_best_card = best_cards[0]

    title = "BEST CARDS FOR THIS TRANSACTION" if result["is_tie"] else "BEST CARD FOR THIS TRANSACTION"

    st.markdown(
        f"""
        <div class="recommendation-box">
            <h2>{title}</h2>
            <span class="eyebrow light">RECOMMENDED PAYMENT METHOD</span>
            <h2>{escape(best_card_label)}</h2>
            <p><strong>Merchant:</strong> {escape(merchant or "Not specified")}</p>
            <p><strong>Transaction:</strong> {format_currency(amount)} &nbsp; | &nbsp;
               <strong>Category:</strong> {category}</p>
            <p><strong>Reward Rate:</strong> {format_percentage(first_best_card["reward_rate"])} &nbsp; | &nbsp;
               <strong>Expected Benefit:</strong> {format_currency(result["highest_benefit"])}</p>
            <p class="result-reason">Highest estimated value among the cards in your wallet for this category.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result["is_tie"]:
        st.info(
            "Multiple cards give the same highest benefit. Any of the highlighted cards is equally beneficial for this transaction."
        )

    st.subheader("Benefit Visualisation")
    comparison = pd.DataFrame(result["comparison"]).sort_values(
        "expected_benefit", ascending=True
    )
    comparison["Chart label"] = comparison["card_name"].apply(compact_card_name)
    comparison["Result"] = comparison["card_name"].apply(
        lambda name: "Recommended" if name in best_card_names else "Other cards"
    )
    chart = px.bar(
        comparison,
        x="expected_benefit",
        y="Chart label",
        orientation="h",
        color="Result",
        text="expected_benefit",
        color_discrete_map={"Recommended": "#635bff", "Other cards": "#cbd5e1"},
        custom_data=["reward_rate", "bank_name"],
    )
    chart.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}<br>%{customdata[1]}<br>Rate: %{customdata[0]:.1f}%<br>Benefit: ₹%{x:,.2f}<extra></extra>",
    )
    chart.update_layout(
        xaxis_title="Estimated benefit (₹)",
        yaxis_title="",
        legend_title_text="",
        showlegend=True,
    )
    max_benefit = float(comparison["expected_benefit"].max())
    chart.update_xaxes(range=[0, max(1, max_benefit * 1.2)])
    st.plotly_chart(style_chart(chart, max(300, len(comparison) * 58)), width="stretch", config=PLOTLY_CONFIG)

    st.subheader("Detailed Comparison")
    st.dataframe(comparison_to_dataframe(result["comparison"]), width="stretch", hide_index=True)
    st.caption("Estimate only. Merchant codes, monthly caps, exclusions and statement-cycle rules can change the final reward.")


def render_find_best_card() -> None:
    """Main recommendation page."""
    render_header(
        "Best Card for This Purchase",
        "Compare the cards you already hold before you pay.",
    )

    cards = get_cards()
    if not cards:
        render_empty_state("You have not added any credit cards yet. Add at least one card before using the recommender.")
        return

    with st.form("recommendation_form"):
        first_column, second_column = st.columns(2)
        with first_column:
            amount = st.number_input("Transaction Amount", min_value=0.0, value=5000.0, step=100.0)
            category = st.selectbox("Category", CATEGORIES)
        with second_column:
            merchant = st.text_input("Merchant Name", placeholder="Example: Amazon")
            transaction_date = st.date_input("Transaction Date", value=date.today())

        submitted = st.form_submit_button("Find Best Card", type="primary")

    if submitted:
        if amount <= 0:
            st.error("Transaction amount must be greater than zero.")
        else:
            recommendation = recommend_best_card(cards, amount, category)
            st.session_state["last_recommendation"] = {
                "amount": amount,
                "category": category,
                "merchant": clean_text(merchant) or "Unknown Merchant",
                "transaction_date": transaction_date.isoformat(),
                "result": recommendation,
            }

    saved_result = st.session_state.get("last_recommendation")
    if not saved_result:
        return

    result = saved_result["result"]
    render_recommendation_result(
        result,
        saved_result["amount"],
        saved_result["category"],
        saved_result["merchant"],
    )

    st.subheader("Save Transaction")
    card_options = {
        f"{card['card_name']} ({card['bank_name']})": card
        for card in cards
    }

    with st.form("save_transaction_form"):
        used_card_label = st.selectbox("Which card did you actually use?", list(card_options.keys()))
        used_card = card_options[used_card_label]
        actual_reward = calculate_reward(
            saved_result["amount"],
            get_card_reward_rate(used_card, saved_result["category"]),
        )
        recommended_reward = float(result["highest_benefit"])
        missed_reward = max(0.0, round(recommended_reward - actual_reward, 2))

        st.write(f"Actual reward with selected card: **{format_currency(actual_reward)}**")
        st.write(f"Potential reward missed: **{format_currency(missed_reward)}**")

        save_transaction = st.form_submit_button("Save Transaction", type="primary")

    if save_transaction:
        recommended_card_names = " / ".join([row["card_name"] for row in result["best_cards"]])
        add_transaction(
            {
                "amount": saved_result["amount"],
                "merchant": saved_result["merchant"],
                "category": saved_result["category"],
                "recommended_card": recommended_card_names,
                "used_card": used_card["card_name"],
                "recommended_reward": recommended_reward,
                "actual_reward": actual_reward,
                "missed_reward": missed_reward,
                "transaction_date": saved_result["transaction_date"],
            }
        )
        st.success("Transaction saved successfully.")
        del st.session_state["last_recommendation"]
        rerun_app()


def render_transaction_history() -> None:
    """Transaction history page with filters and sorting."""
    render_header(
        "Transaction History",
        "Review saved recommendations, actual rewards, and missed rewards.",
    )

    dataframe = transactions_to_dataframe(get_transactions())
    if dataframe.empty:
        render_empty_state("No transactions have been saved yet.")
        return

    with st.expander("Filters", expanded=True):
        first_column, second_column, third_column = st.columns(3)
        with first_column:
            date_range = st.date_input(
                "Date Range",
                value=(
                    dataframe["transaction_date"].min().date(),
                    dataframe["transaction_date"].max().date(),
                ),
            )
            category_filter = st.selectbox("Category", ["All"] + sorted(dataframe["category"].unique()))
        with second_column:
            card_names = sorted(
                set(dataframe["used_card"].unique()).union(set(dataframe["recommended_card"].unique()))
            )
            card_filter = st.selectbox("Card", ["All"] + card_names)
            merchant_filter = st.text_input("Merchant contains")
        with third_column:
            sort_option = st.selectbox(
                "Sort By",
                [
                    "Date newest first",
                    "Date oldest first",
                    "Amount highest first",
                    "Amount lowest first",
                    "Reward highest first",
                    "Missed reward highest first",
                ],
            )

    filtered = dataframe.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered["transaction_date"].dt.date >= start_date)
            & (filtered["transaction_date"].dt.date <= end_date)
        ]

    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]

    if card_filter != "All":
        filtered = filtered[
            (filtered["used_card"] == card_filter)
            | (filtered["recommended_card"].str.contains(card_filter, regex=False))
        ]

    if merchant_filter.strip():
        filtered = filtered[
            filtered["merchant"].str.contains(merchant_filter.strip(), case=False, na=False)
        ]

    sort_map = {
        "Date newest first": ("transaction_date", False),
        "Date oldest first": ("transaction_date", True),
        "Amount highest first": ("amount", False),
        "Amount lowest first": ("amount", True),
        "Reward highest first": ("actual_reward", False),
        "Missed reward highest first": ("missed_reward", False),
    }
    sort_column, ascending = sort_map[sort_option]
    filtered = filtered.sort_values(sort_column, ascending=ascending)

    st.dataframe(prepare_transactions_table(filtered), width="stretch", hide_index=True)


def render_analytics() -> None:
    """Analytics page with charts and explanatory totals."""
    render_header(
        "Analytics",
        "Understand spending behavior, rewards earned, and reward opportunities missed.",
    )

    dataframe = transactions_to_dataframe(get_transactions())
    if dataframe.empty:
        render_empty_state("Analytics will appear after you save transactions.")
        return

    metric_one, metric_two, metric_three = st.columns(3)
    valuable_card, valuable_reward = most_valuable_card(dataframe)

    metric_one.metric("Most Used Card", most_used_card(dataframe))
    metric_two.metric("Most Valuable Card", valuable_card)
    metric_three.metric("Value Generated", format_currency(valuable_reward))

    missed_current_month = missed_rewards_this_month(dataframe)
    st.info(f"Potential savings missed this month: {format_currency(missed_current_month)}")

    first_column, second_column = st.columns(2)

    with first_column:
        st.subheader("Spending by Category")
        category_data = spending_by_category(dataframe)
        figure = px.bar(
            category_data,
            x="category",
            y="amount",
            color="category",
            color_discrete_sequence=VIOLET_SCALE,
        )
        figure.update_layout(
            xaxis_title="Category",
            yaxis_title="Amount Spent",
            showlegend=False,
        )
        st.plotly_chart(style_chart(figure, 360), width="stretch", config=PLOTLY_CONFIG)

    with second_column:
        st.subheader("Rewards by Credit Card")
        rewards_data = rewards_by_card(dataframe)
        figure = px.bar(
            rewards_data,
            x="used_card",
            y="actual_reward",
            color="used_card",
            color_discrete_sequence=VIOLET_SCALE,
        )
        figure.update_layout(
            xaxis_title="Card",
            yaxis_title="Rewards Earned",
            showlegend=False,
        )
        st.plotly_chart(style_chart(figure, 360), width="stretch", config=PLOTLY_CONFIG)

    st.subheader("Monthly Spending")
    monthly_data = monthly_spending(dataframe)
    figure = px.line(monthly_data, x="month", y="amount", markers=True)
    figure.update_traces(line_color="#7657e8", fill="tozeroy", fillcolor="rgba(118,87,232,0.10)")
    figure.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount Spent",
    )
    st.plotly_chart(style_chart(figure, 340), width="stretch", config=PLOTLY_CONFIG)

    st.subheader("Most Valuable Existing Card")
    st.markdown(
        f"""
        <div class="soft-panel">
            <div class="card-title">{valuable_card}</div>
            <p style="color: #475569; margin-bottom: 0;">
                This card has generated the highest total actual reward in your saved transaction
                history: <strong>{format_currency(valuable_reward)}</strong>. The calculation adds
                the stored actual reward from every transaction where this card was used.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_calculators() -> None:
    """Decision calculators for annual value, EMI cost, and utilisation."""
    render_header(
        "Financial Calculators",
        "Pressure-test rewards against fees and borrowing costs before making a decision.",
    )

    annual_tab, emi_tab, utilisation_tab = st.tabs(
        ["Annual value", "EMI cost", "Credit utilisation"]
    )

    with annual_tab:
        st.subheader("Annual wallet value")
        st.caption("Enter an average month. The model annualises spend, estimates rewards, and subtracts each card's annual fee.")
        cards = get_cards()
        if not cards:
            render_empty_state("Add cards to compare annual value.")
        else:
            monthly_spend = {}
            defaults = {
                "Shopping": 5000.0,
                "Dining": 3000.0,
                "Fuel": 3000.0,
                "Groceries": 6000.0,
                "Travel": 4000.0,
                "Entertainment": 1500.0,
                "Utilities": 4000.0,
                "Online Shopping": 6000.0,
                "Other": 3000.0,
            }
            with st.expander("Edit monthly spending profile", expanded=False):
                columns = st.columns(3)
                for index, category in enumerate(CATEGORIES):
                    with columns[index % 3]:
                        monthly_spend[category] = st.number_input(
                            category,
                            min_value=0.0,
                            value=defaults[category],
                            step=500.0,
                            key=f"annual_{category}",
                        )

            for category in CATEGORIES:
                monthly_spend.setdefault(category, defaults[category])

            values = calculate_annual_card_values(cards, monthly_spend)
            if values:
                winner = values[0]
                total_monthly = sum(monthly_spend.values())
                metric_one, metric_two, metric_three = st.columns(3)
                metric_one.metric("Monthly spend modelled", format_currency(total_monthly))
                metric_two.metric("Best net annual value", format_currency(winner["net_value"]))
                metric_three.metric("Best-fit card", compact_card_name(winner["card_name"]))

                table = pd.DataFrame(values)
                table["Chart label"] = table["card_name"].apply(compact_card_name)
                chart_table = table.sort_values("net_value", ascending=True)
                chart = px.bar(
                    chart_table,
                    x="net_value",
                    y="Chart label",
                    orientation="h",
                    color="net_value",
                    text="net_value",
                    color_continuous_scale=VIOLET_SCALE,
                )
                chart.update_traces(
                    texttemplate="₹%{text:,.0f}",
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="%{y}<br>Net annual value: ₹%{x:,.2f}<extra></extra>",
                )
                chart.update_layout(
                    xaxis_title="Net annual value (₹)",
                    yaxis_title="",
                    coloraxis_showscale=False,
                    margin=dict(l=8, r=36, t=18, b=12),
                )
                max_net_value = float(chart_table["net_value"].max())
                chart.update_xaxes(range=[min(0, float(chart_table["net_value"].min())), max(1, max_net_value * 1.2)])
                st.plotly_chart(style_chart(chart, 350), width="stretch", config=PLOTLY_CONFIG)
                display = table.rename(
                    columns={
                        "card_name": "Card",
                        "bank_name": "Issuer",
                        "annual_spend": "Annual spend",
                        "gross_reward": "Gross rewards",
                        "annual_fee": "Annual fee",
                        "net_value": "Net annual value",
                        "effective_return": "Net return (%)",
                    }
                )
                for column in ["Annual spend", "Gross rewards", "Annual fee", "Net annual value"]:
                    display[column] = display[column].apply(format_currency)
                st.dataframe(display, width="stretch", hide_index=True)
                st.caption("Planning estimate before caps, fee waivers, taxes, redemption ratios, merchant-code exclusions, and limited-period offers.")

    with emi_tab:
        st.subheader("True EMI cost")
        st.caption("Uses the standard reducing-balance EMI formula and includes the processing fee in total cost.")
        first, second = st.columns(2)
        with first:
            principal = st.number_input("Purchase amount", min_value=0.0, value=50000.0, step=1000.0)
            annual_rate = st.number_input("Annual interest rate (%)", min_value=0.0, value=18.0, step=0.5)
        with second:
            months = st.slider("Tenure (months)", min_value=3, max_value=36, value=12, step=3)
            processing_fee = st.number_input("Processing fee (%)", min_value=0.0, value=1.0, step=0.1)
        emi = calculate_emi(principal, annual_rate, months, processing_fee)
        col_one, col_two, col_three, col_four = st.columns(4)
        col_one.metric("Monthly EMI", format_currency(emi["monthly_emi"]))
        col_two.metric("Total interest", format_currency(emi["interest"]))
        col_three.metric("Processing fee", format_currency(emi["processing_fee"]))
        col_four.metric("Total outflow", format_currency(emi["total_cost"]))
        cost_chart = go.Figure(
            data=[
                go.Pie(
                    labels=["Principal", "Interest", "Processing fee"],
                    values=[principal, emi["interest"], emi["processing_fee"]],
                    hole=0.68,
                    marker=dict(colors=["#635bff", "#8ea7ff", "#dceeff"]),
                    textinfo="percent",
                    hovertemplate="%{label}: ₹%{value:,.2f}<extra></extra>",
                )
            ]
        )
        cost_chart.update_layout(showlegend=False, annotations=[dict(text="Total cost", x=0.5, y=0.5, showarrow=False)])
        st.plotly_chart(style_chart(cost_chart, 330), width="stretch", config=PLOTLY_CONFIG)
        if emi["interest"] > 0:
            st.warning("Rewards rarely offset revolving credit or EMI interest. Compare the total outflow, not only the monthly instalment.")

    with utilisation_tab:
        st.subheader("Credit utilisation check")
        first, second = st.columns(2)
        with first:
            balance = st.number_input("Current card balance", min_value=0.0, value=25000.0, step=1000.0)
        with second:
            credit_limit = st.number_input("Total credit limit", min_value=1.0, value=100000.0, step=5000.0)
        utilisation = calculate_utilisation(balance, credit_limit)
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=float(utilisation["percentage"]),
                number={"suffix": "%", "font": {"color": "#202438", "size": 38}},
                title={"text": "Current utilisation"},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 0},
                    "bar": {"color": "#7657e8", "thickness": 0.28},
                    "bgcolor": "#dfe2eb",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 30], "color": "#e7e2ff"},
                        {"range": [30, 50], "color": "#d4caff"},
                        {"range": [50, 100], "color": "#b8a8fa"},
                    ],
                    "threshold": {"line": {"color": "#5134c7", "width": 3}, "thickness": 0.75, "value": 30},
                },
            )
        )
        st.plotly_chart(style_chart(gauge, 310), width="stretch", config=PLOTLY_CONFIG)
        st.info(f'Planning band: **{utilisation["band"]}**. Lower reported utilisation generally leaves more available credit, but scoring models consider many factors.')


def render_settings_about() -> None:
    """Settings and About page."""
    render_header(
        "Settings / About",
        "Manage the starter library, local data, and methodology.",
    )

    st.subheader("Indian card starter library")
    st.write(
        "Load five Indian credit-card examples with intentionally varied reward rates for demonstrating recommendations. These percentages are illustrative and editable."
    )

    demo_column, reset_column = st.columns(2)

    with demo_column:
        if st.button("Load Starter Cards", type="primary"):
            cards_added = load_demo_cards(reset_existing=False)
            if cards_added:
                st.success(f"{cards_added} starter cards were loaded.")
            else:
                st.info("Starter cards are already available.")
            rerun_app()

    with reset_column:
        confirm_reset = st.checkbox("Reset cards and transactions before loading the starter library.")
        if st.button("Reset to Starter Library"):
            if confirm_reset:
                load_demo_cards(reset_existing=True)
                st.success("Database was reset and the starter library was loaded.")
                rerun_app()
            else:
                st.error("Please tick the confirmation box before resetting data.")

    st.subheader("Clear All Project Data")
    confirm_clear = st.checkbox("I understand this will delete all cards and transactions.")
    if st.button("Clear All Data"):
        if confirm_clear:
            reset_database()
            st.success("All project data has been cleared.")
            rerun_app()
        else:
            st.error("Please tick the confirmation box before clearing data.")

    st.subheader("About")
    st.markdown(
        """
        **Smart Card Benefit Recommender** is a Python-based recommendation system
        developed to help credit card users determine the most rewarding card for
        individual transactions.

        The recommendation engine compares estimated monetary value. It does not
        evaluate eligibility, credit approval, taxes, credit score impact, issuer
        discretion, or every merchant category code. This is an educational planning
        tool, not financial advice.

        Built with Python, Streamlit, SQLite, Pandas, and Plotly.
        """
    )


def main() -> None:
    """Application entry point."""
    st.set_page_config(
        page_title="Smart Card Benefit Recommender",
        page_icon="₹",
        layout="wide",
    )
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    initialize_database()

    st.sidebar.markdown('<div class="brand-mark">SC</div>', unsafe_allow_html=True)
    st.sidebar.markdown("## SmartCard India")
    st.sidebar.caption("Rewards intelligence workspace")
    selected_page = st.sidebar.radio("Navigation", NAVIGATION_ITEMS)

    if selected_page == "Overview":
        render_dashboard()
    elif selected_page == "Best Card":
        render_find_best_card()
    elif selected_page == "Card Library":
        render_my_cards()
    elif selected_page == "Calculators":
        render_calculators()
    elif selected_page == "Add Card":
        render_add_card()
    elif selected_page == "Analytics":
        render_analytics()
    elif selected_page == "History":
        render_transaction_history()
    elif selected_page == "Settings":
        render_settings_about()


if __name__ == "__main__":
    main()
