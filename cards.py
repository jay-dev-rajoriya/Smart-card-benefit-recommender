"""Card-related constants, demo data, and validation helpers."""

from __future__ import annotations

from typing import Any

from utils import clean_text


CATEGORIES = [
    "Shopping",
    "Dining",
    "Fuel",
    "Groceries",
    "Travel",
    "Entertainment",
    "Utilities",
    "Online Shopping",
    "Other",
]

CARD_TYPES = ["Credit Card", "Debit Card", "Prepaid Card", "Virtual Card"]
REWARD_TYPES = ["Cashback", "CashPoints", "Reward Points", "Miles", "Discount"]

CATEGORY_RATE_COLUMNS = {
    "Shopping": "shopping_rate",
    "Dining": "dining_rate",
    "Fuel": "fuel_rate",
    "Groceries": "grocery_rate",
    "Travel": "travel_rate",
    "Entertainment": "entertainment_rate",
    "Utilities": "utility_rate",
    "Online Shopping": "online_shopping_rate",
    "Other": "other_rate",
}


DEMO_CARDS = [
    {
        "card_name": "Demo Rewards Plus",
        "bank_name": "Demo Bank",
        "card_type": "Credit Card",
        "annual_fee": 999,
        "reward_type": "Cashback",
        "shopping_rate": 4.0,
        "dining_rate": 2.5,
        "fuel_rate": 1.0,
        "grocery_rate": 2.0,
        "travel_rate": 1.5,
        "entertainment_rate": 2.0,
        "utility_rate": 1.0,
        "online_shopping_rate": 5.0,
        "other_rate": 1.0,
    },
    {
        "card_name": "Demo Cashback Pro",
        "bank_name": "Sample Finance",
        "card_type": "Credit Card",
        "annual_fee": 499,
        "reward_type": "Cashback",
        "shopping_rate": 3.0,
        "dining_rate": 3.0,
        "fuel_rate": 1.0,
        "grocery_rate": 4.0,
        "travel_rate": 1.0,
        "entertainment_rate": 1.5,
        "utility_rate": 2.0,
        "online_shopping_rate": 4.0,
        "other_rate": 1.0,
    },
    {
        "card_name": "Demo Travel Card",
        "bank_name": "Journey Bank",
        "card_type": "Credit Card",
        "annual_fee": 1499,
        "reward_type": "Miles",
        "shopping_rate": 1.0,
        "dining_rate": 2.0,
        "fuel_rate": 0.5,
        "grocery_rate": 1.0,
        "travel_rate": 6.0,
        "entertainment_rate": 2.0,
        "utility_rate": 0.5,
        "online_shopping_rate": 2.0,
        "other_rate": 1.0,
    },
    {
        "card_name": "Demo Fuel Saver",
        "bank_name": "Highway Bank",
        "card_type": "Credit Card",
        "annual_fee": 299,
        "reward_type": "Discount",
        "shopping_rate": 1.0,
        "dining_rate": 1.0,
        "fuel_rate": 5.0,
        "grocery_rate": 1.0,
        "travel_rate": 1.0,
        "entertainment_rate": 1.0,
        "utility_rate": 1.0,
        "online_shopping_rate": 1.0,
        "other_rate": 0.5,
    },
    {
        "card_name": "Demo Lifestyle Card",
        "bank_name": "Urban Credit",
        "card_type": "Credit Card",
        "annual_fee": 799,
        "reward_type": "Reward Points",
        "shopping_rate": 2.0,
        "dining_rate": 5.0,
        "fuel_rate": 0.5,
        "grocery_rate": 2.0,
        "travel_rate": 2.0,
        "entertainment_rate": 5.0,
        "utility_rate": 1.0,
        "online_shopping_rate": 3.0,
        "other_rate": 1.0,
    },
]


DATASET_REVIEW_DATE = "20 September 2026"

# Simplified planning rates based on issuer-published headline benefits.
# Actual rewards depend on merchant codes, channels, caps, and exclusions.
REAL_WORLD_CARDS = [
    {"card_name": "CASHBACK SBI Card", "bank_name": "SBI Card", "card_type": "Credit Card", "annual_fee": 999, "reward_type": "Cashback", "shopping_rate": 1.5, "dining_rate": 2.0, "fuel_rate": 0.5, "grocery_rate": 1.5, "travel_rate": 1.0, "entertainment_rate": 5.5, "utility_rate": 0.5, "online_shopping_rate": 5.0, "other_rate": 3.0},
    {"card_name": "Amazon Pay ICICI Bank Credit Card", "bank_name": "ICICI Bank", "card_type": "Credit Card", "annual_fee": 0, "reward_type": "Cashback", "shopping_rate": 2.5, "dining_rate": 1.5, "fuel_rate": 0.75, "grocery_rate": 4.5, "travel_rate": 2.5, "entertainment_rate": 2.0, "utility_rate": 2.0, "online_shopping_rate": 5.5, "other_rate": 1.25},
    {"card_name": "HDFC Bank Millennia Credit Card", "bank_name": "HDFC Bank", "card_type": "Credit Card", "annual_fee": 1000, "reward_type": "CashPoints", "shopping_rate": 5.0, "dining_rate": 5.0, "fuel_rate": 1.0, "grocery_rate": 2.5, "travel_rate": 3.0, "entertainment_rate": 3.5, "utility_rate": 1.5, "online_shopping_rate": 4.5, "other_rate": 1.5},
    {"card_name": "Flipkart Axis Bank Credit Card", "bank_name": "Axis Bank", "card_type": "Credit Card", "annual_fee": 500, "reward_type": "Cashback", "shopping_rate": 4.0, "dining_rate": 2.5, "fuel_rate": 1.25, "grocery_rate": 2.0, "travel_rate": 5.0, "entertainment_rate": 2.5, "utility_rate": 1.0, "online_shopping_rate": 6.0, "other_rate": 1.75},
    {"card_name": "Axis Bank Freecharge Plus Credit Card", "bank_name": "Axis Bank", "card_type": "Credit Card", "annual_fee": 350, "reward_type": "Cashback", "shopping_rate": 2.0, "dining_rate": 4.0, "fuel_rate": 4.5, "grocery_rate": 3.5, "travel_rate": 2.0, "entertainment_rate": 4.0, "utility_rate": 5.0, "online_shopping_rate": 2.0, "other_rate": 2.0},
]

CARD_PROFILES = {
    "CASHBACK SBI Card": {"accent": "#2563eb", "best_for": "Broad online spending", "headline": "5% online; 1% eligible offline spends", "fine_print": "Utilities, insurance, fuel, rent, wallets, education, jewellery and railways are among excluded categories. From 1 April 2026, online and offline cashback are separately capped at ₹2,000 per statement cycle.", "source_url": "https://www.sbicard.com/en/personal/credit-cards/cashback-sbi-card.html"},
    "Amazon Pay ICICI Bank Credit Card": {"accent": "#f59e0b", "best_for": "Amazon Prime purchases", "headline": "5% on Amazon for Prime members; 3% for non-Prime", "fine_print": "The 5% planning rate assumes an eligible Amazon.in purchase by a Prime member. Amazon Pay partner payments can earn 2%; other eligible spends earn 1%. Fuel, rent, precious metals and certain other transactions are excluded.", "source_url": "https://www.icicibank.com/personal-banking/cards/credit-card/amazon-pay-credit-card/amazon-pay-faq"},
    "HDFC Bank Millennia Credit Card": {"accent": "#dc2626", "best_for": "Selected online brands", "headline": "5% CashPoints at selected online merchants", "fine_print": "The 5% rate applies only to listed merchants such as Amazon, Flipkart, Myntra, Swiggy, Uber and Zomato, with a ₹1,000 cycle cap. Other eligible spends earn 1%; fuel, EMI, wallet, rent and government transactions are excluded.", "source_url": "https://www.hdfcbank.com/content/api/contentstream-id/723fb80a-2dde-42a3-9793-7ae1be57c87f/5d94cc09-80b7-4073-8c9f-22fad88054f0"},
    "Flipkart Axis Bank Credit Card": {"accent": "#7c3aed", "best_for": "Flipkart and Cleartrip", "headline": "5% on Flipkart and Cleartrip; 7.5% on Myntra", "fine_print": "The general Online Shopping rate uses the 5% Flipkart/Cleartrip assumption. Quarterly caps and merchant-specific terms apply. Fuel, utilities, rent, wallet, EMI, jewellery, insurance and education are among excluded categories.", "source_url": "https://www.axisbank.com/docs/default-source/default-document-library/credit-card-tnc/terms-and-conditions-for-flipkart-credit-card.pdf"},
    "Axis Bank Freecharge Plus Credit Card": {"accent": "#0891b2", "best_for": "Freecharge bills and commute", "headline": "5% on Freecharge; 2% local commute", "fine_print": "The utility planning rate assumes payment through Freecharge. Local commute earns 2% and other eligible spends earn 1%. Verify current caps, exclusions and fee with Axis Bank before applying.", "source_url": "https://www.axisbank.com/retail/cards/credit-card/axis-bank-freecharge-plus-credit-card/features-benefits"},
}


def get_rate_column(category: str) -> str:
    """Return the database column that stores a category's reward rate."""
    return CATEGORY_RATE_COLUMNS.get(category, "other_rate")


def validate_card_data(card_data: dict[str, Any]) -> list[str]:
    """Return a list of human-readable validation errors for a card form."""
    errors = []

    if not clean_text(card_data.get("card_name")):
        errors.append("Card name is required.")

    if not clean_text(card_data.get("bank_name")):
        errors.append("Bank name is required.")

    annual_fee = card_data.get("annual_fee", 0)
    try:
        if float(annual_fee) < 0:
            errors.append("Annual fee cannot be negative.")
    except (TypeError, ValueError):
        errors.append("Annual fee must be a valid number.")

    for category, column_name in CATEGORY_RATE_COLUMNS.items():
        reward_rate = card_data.get(column_name, 0)
        try:
            numeric_rate = float(reward_rate)
        except (TypeError, ValueError):
            errors.append(f"{category} reward rate must be a valid number.")
            continue

        if numeric_rate < 0:
            errors.append(f"{category} reward rate cannot be negative.")
        elif numeric_rate > 100:
            errors.append(f"{category} reward rate cannot be more than 100%.")

    return errors


def normalize_card_data(card_data: dict[str, Any]) -> dict[str, Any]:
    """Convert user input into clean values ready for SQLite."""
    normalized = {
        "card_name": clean_text(card_data.get("card_name")),
        "bank_name": clean_text(card_data.get("bank_name")),
        "card_type": clean_text(card_data.get("card_type")) or CARD_TYPES[0],
        "annual_fee": float(card_data.get("annual_fee") or 0),
        "reward_type": clean_text(card_data.get("reward_type")) or REWARD_TYPES[0],
    }

    for column_name in CATEGORY_RATE_COLUMNS.values():
        normalized[column_name] = float(card_data.get(column_name) or 0)

    return normalized
