"""Tests for reward calculation and card recommendations."""

import unittest

from recommender import calculate_reward, recommend_best_card


class RecommenderTests(unittest.TestCase):
    def test_calculate_reward(self) -> None:
        self.assertEqual(calculate_reward(5000, 5), 250)

    def test_recommend_best_card_and_handle_ties(self) -> None:
        cards = [
            {
                "id": card_id,
                "card_name": card_name,
                "bank_name": "Test Bank",
                "reward_type": "Cashback",
                "shopping_rate": rate,
            }
            for card_id, card_name, rate in (
                (1, "Card A", 5),
                (2, "Card B", 5),
                (3, "Card C", 2),
            )
        ]

        result = recommend_best_card(cards, 1000, "Shopping")

        self.assertEqual(result["highest_benefit"], 50)
        self.assertEqual(len(result["best_cards"]), 2)
        self.assertEqual(
            {card["card_name"] for card in result["best_cards"]},
            {"Card A", "Card B"},
        )

    def test_rejects_non_positive_amount(self) -> None:
        with self.assertRaises(ValueError):
            recommend_best_card([], 0, "Shopping")


if __name__ == "__main__":
    unittest.main()
