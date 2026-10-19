"""Tests for financial planning calculators."""

import unittest

from calculators import calculate_annual_card_values, calculate_emi, calculate_utilisation


class CalculatorTests(unittest.TestCase):
    def test_zero_interest_emi(self) -> None:
        result = calculate_emi(12000, 0, 12, 1)
        self.assertEqual(result["monthly_emi"], 1000)
        self.assertEqual(result["interest"], 0)
        self.assertEqual(result["total_cost"], 12120)

    def test_utilisation_bands(self) -> None:
        self.assertEqual(calculate_utilisation(25000, 100000)["band"], "Moderate")
        self.assertEqual(calculate_utilisation(60000, 100000)["band"], "Very high")

    def test_annual_value_subtracts_fee(self) -> None:
        card = {
            "card_name": "Test Card",
            "bank_name": "Test Bank",
            "annual_fee": 500,
            "shopping_rate": 5,
        }
        result = calculate_annual_card_values([card], {"Shopping": 1000})[0]
        self.assertEqual(result["gross_reward"], 600)
        self.assertEqual(result["net_value"], 100)


if __name__ == "__main__":
    unittest.main()
