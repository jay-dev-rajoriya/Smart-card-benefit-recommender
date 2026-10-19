from decimal import Decimal
import unittest

from catalog import get_card, get_catalog
from reward_engine import TransactionContext, evaluate, rank


class RewardEngineTests(unittest.TestCase):
    def test_catalog_has_exactly_eight_unique_cards(self):
        cards = get_catalog()
        self.assertEqual(len(cards), 8)
        self.assertEqual(len({card["id"] for card in cards}), 8)

    def test_airtel_channel_and_merchant_rule(self):
        card = get_card("airtel-axis")
        eligible = evaluate(card, TransactionContext.create(1000, "Telecom", "Airtel", "In-app"))
        wrong_channel = evaluate(card, TransactionContext.create(1000, "Telecom", "Airtel", "Online"))
        self.assertEqual(eligible["reward"], Decimal("250.00"))
        self.assertEqual(wrong_channel["reward"], Decimal("10.00"))

    def test_cap_usage_reduces_reward(self):
        card = get_card("sbi-cashback")
        result = evaluate(card, TransactionContext.create(10000, "Online shopping", "Shop", "Online"), {"online": Decimal("1800")})
        self.assertEqual(result["reward"], Decimal("200.00"))

    def test_excluded_transaction_is_zero(self):
        card = get_card("sbi-cashback")
        result = evaluate(card, TransactionContext.create(5000, "Fuel", "Fuel station", "Offline", tags=["fuel"]))
        self.assertEqual(result["reward"], Decimal("0.00"))

    def test_amazon_membership_changes_rate(self):
        card = get_card("amazon-pay-icici")
        prime = evaluate(card, TransactionContext.create(1000, "Online shopping", "Amazon", membership="Prime"))
        other = evaluate(card, TransactionContext.create(1000, "Online shopping", "Amazon", membership="Non-Prime"))
        self.assertEqual(prime["reward"], Decimal("50.00"))
        self.assertEqual(other["reward"], Decimal("30.00"))

    def test_ranking_is_deterministic_for_ties(self):
        cards = get_catalog(); tx = TransactionContext.create(1000, "Fuel", "Station", "Offline", tags=["fuel"])
        self.assertEqual([x["card_id"] for x in rank(cards, tx)], [x["card_id"] for x in rank(cards, tx)])

    def test_non_positive_amount_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(get_card("sbi-cashback"), TransactionContext.create(0, "Other"))
