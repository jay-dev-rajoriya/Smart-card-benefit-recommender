"""Pandas-based analytics for dashboard and reports."""

from __future__ import annotations

from typing import Any

import pandas as pd


def transactions_to_dataframe(transactions: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert transaction dictionaries into a prepared DataFrame."""
    dataframe = pd.DataFrame(transactions)

    if dataframe.empty:
        return dataframe

    dataframe["transaction_date"] = pd.to_datetime(dataframe["transaction_date"])
    dataframe["amount"] = pd.to_numeric(dataframe["amount"], errors="coerce").fillna(0)
    dataframe["recommended_reward"] = pd.to_numeric(
        dataframe["recommended_reward"], errors="coerce"
    ).fillna(0)
    dataframe["actual_reward"] = pd.to_numeric(
        dataframe["actual_reward"], errors="coerce"
    ).fillna(0)
    dataframe["missed_reward"] = pd.to_numeric(
        dataframe["missed_reward"], errors="coerce"
    ).fillna(0)
    dataframe["month"] = dataframe["transaction_date"].dt.strftime("%Y-%m")

    return dataframe


def build_dashboard_metrics(
    transactions: list[dict[str, Any]], cards_count: int
) -> dict[str, Any]:
    """Calculate top-level numbers shown on the dashboard."""
    dataframe = transactions_to_dataframe(transactions)

    if dataframe.empty:
        return {
            "total_spending": 0,
            "total_rewards": 0,
            "total_transactions": 0,
            "cards_added": cards_count,
            "missed_rewards": 0,
            "favourite_category": "No transactions yet",
        }

    favourite_category = dataframe.groupby("category")["amount"].sum().idxmax()

    return {
        "total_spending": float(dataframe["amount"].sum()),
        "total_rewards": float(dataframe["actual_reward"].sum()),
        "total_transactions": int(len(dataframe)),
        "cards_added": cards_count,
        "missed_rewards": float(dataframe["missed_reward"].sum()),
        "favourite_category": favourite_category,
    }


def spending_by_category(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Summarize spending for each category."""
    if dataframe.empty:
        return pd.DataFrame(columns=["category", "amount"])

    return (
        dataframe.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )


def monthly_spending(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Summarize total spending by month."""
    if dataframe.empty:
        return pd.DataFrame(columns=["month", "amount"])

    return dataframe.groupby("month", as_index=False)["amount"].sum().sort_values("month")


def rewards_by_card(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Summarize actual rewards by the card the user really used."""
    if dataframe.empty:
        return pd.DataFrame(columns=["used_card", "actual_reward"])

    return (
        dataframe.groupby("used_card", as_index=False)["actual_reward"]
        .sum()
        .sort_values("actual_reward", ascending=False)
    )


def most_used_card(dataframe: pd.DataFrame) -> str:
    """Find the card used in the largest number of transactions."""
    if dataframe.empty:
        return "No transactions yet"

    return str(dataframe["used_card"].value_counts().idxmax())


def most_valuable_card(dataframe: pd.DataFrame) -> tuple[str, float]:
    """Find the card that generated the highest total actual reward."""
    if dataframe.empty:
        return "No transactions yet", 0.0

    summary = rewards_by_card(dataframe)
    top_row = summary.iloc[0]
    return str(top_row["used_card"]), float(top_row["actual_reward"])


def missed_rewards_this_month(dataframe: pd.DataFrame) -> float:
    """Calculate potential savings missed in the current calendar month."""
    if dataframe.empty:
        return 0.0

    current_month = pd.Timestamp.today().strftime("%Y-%m")
    current_month_data = dataframe[dataframe["month"] == current_month]

    if current_month_data.empty:
        return 0.0

    return float(current_month_data["missed_reward"].sum())

