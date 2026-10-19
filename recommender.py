"""Rule-based recommendation logic for choosing the best card."""

from __future__ import annotations

from typing import Any

from cards import get_rate_column


def calculate_reward(amount: float, reward_rate: float) -> float:
    """Calculate the expected monetary reward for a transaction.

    Formula:
        benefit = transaction_amount * reward_percentage / 100
    """
    if amount <= 0 or reward_rate < 0:
        return 0.0
    return round(amount * reward_rate / 100, 2)


def get_card_reward_rate(card: dict[str, Any], category: str) -> float:
    """Read the correct reward percentage from a card for the selected category."""
    rate_column = get_rate_column(category)
    return float(card.get(rate_column) or 0)


def compare_cards(cards: list[dict[str, Any]], amount: float, category: str) -> list[dict[str, Any]]:
    """Compare every available card and sort by benefit, highest first."""
    comparison = []

    for card in cards:
        reward_rate = get_card_reward_rate(card, category)
        expected_benefit = calculate_reward(amount, reward_rate)

        comparison.append(
            {
                "card_id": card["id"],
                "card_name": card["card_name"],
                "bank_name": card["bank_name"],
                "reward_type": card["reward_type"],
                "reward_rate": reward_rate,
                "expected_benefit": expected_benefit,
            }
        )

    return sorted(
        comparison,
        key=lambda row: (row["expected_benefit"], row["reward_rate"], row["card_name"]),
        reverse=True,
    )


def recommend_best_card(cards: list[dict[str, Any]], amount: float, category: str) -> dict[str, Any]:
    """Return the top recommendation plus all cards compared.

    Ties are kept as a list of best cards instead of hiding one of the equally
    useful options.
    """
    if amount <= 0:
        raise ValueError("Transaction amount must be greater than zero.")

    if not cards:
        return {
            "best_cards": [],
            "comparison": [],
            "highest_benefit": 0.0,
            "is_tie": False,
        }

    comparison = compare_cards(cards, amount, category)
    highest_benefit = comparison[0]["expected_benefit"] if comparison else 0.0
    best_cards = [
        row for row in comparison if row["expected_benefit"] == highest_benefit
    ]

    return {
        "best_cards": best_cards,
        "comparison": comparison,
        "highest_benefit": highest_benefit,
        "is_tie": len(best_cards) > 1,
    }

