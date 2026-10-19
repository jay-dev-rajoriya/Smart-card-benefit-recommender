"""Curated Indian credit-card catalog and versioned reward rules.

Rates are modelling inputs, not financial advice. ``CARD_SOURCES.md`` records the
official product pages and the assumptions used where MCC classification matters.
"""

from __future__ import annotations

from copy import deepcopy


REVIEWED_ON = "2026-10-16"

CATEGORIES = [
    "Online shopping", "Dining", "Groceries", "Food delivery", "Travel",
    "Utilities", "Telecom", "Fuel", "Entertainment", "Other",
]
CHANNELS = ["Online", "Offline", "In-app"]
EXCLUDED = ["fuel", "rent", "wallet", "government", "education", "insurance", "jewellery", "emi"]


def rule(rule_id: str, rate: str, *, categories=None, merchants=None, channels=None,
         cap=None, cap_group=None, excludes=None, membership=None, priority=10,
         min_amount="0", note="") -> dict:
    return {
        "id": rule_id, "rate": rate, "categories": categories or [],
        "merchants": [m.lower() for m in (merchants or [])], "channels": channels or [],
        "cap": cap, "cap_group": cap_group, "excludes": excludes or [],
        "membership": membership, "priority": priority, "min_amount": min_amount,
        "effective_from": "2026-04-01", "note": note,
    }


CARDS = [
    {
        "id": "sbi-cashback", "name": "CASHBACK SBI Card", "issuer": "SBI Card",
        "network": "Visa", "annual_fee": "999", "fee_waiver": "200000",
        "accent": "#2f6fed", "featured": "Online-first simplicity",
        "source": "https://www.sbicard.com/cashback-revised",
        "rules": [
            rule("sbi-online", "5", channels=["Online", "In-app"], cap="2000", cap_group="online", excludes=EXCLUDED + ["gaming", "tolls", "railways"], priority=20),
            rule("sbi-offline", "1", channels=["Offline"], cap="2000", cap_group="offline", excludes=EXCLUDED + ["gaming", "tolls", "railways"], priority=10),
        ],
    },
    {
        "id": "amazon-pay-icici", "name": "Amazon Pay ICICI Bank Credit Card", "issuer": "ICICI Bank",
        "network": "Visa", "annual_fee": "0", "fee_waiver": "0", "accent": "#ff9f1c",
        "featured": "Amazon and everyday cashback",
        "source": "https://www.icicibank.com/personal-banking/cards/credit-card/amazon-pay-credit-card/amazon-pay-faq",
        "rules": [
            rule("ap-prime", "5", merchants=["amazon"], membership="Prime", excludes=EXCLUDED, priority=40),
            rule("ap-standard", "3", merchants=["amazon"], membership="Non-Prime", excludes=EXCLUDED, priority=35),
            rule("ap-partner", "2", merchants=["amazon pay", "gift card"], excludes=EXCLUDED, priority=30),
            rule("ap-base", "1", excludes=EXCLUDED, priority=5),
        ],
    },
    {
        "id": "hdfc-millennia", "name": "HDFC Bank Millennia Credit Card", "issuer": "HDFC Bank",
        "network": "Visa", "annual_fee": "1000", "fee_waiver": "100000", "accent": "#00a67e",
        "featured": "Popular online brands",
        "source": "https://www.hdfc.bank.in/credit-cards/millennia-credit-card",
        "rules": [
            rule("millennia-select", "5", merchants=["amazon", "bookmyshow", "cult.fit", "flipkart", "myntra", "sony liv", "swiggy", "tata cliq", "uber", "zomato"], cap="1000", cap_group="select", excludes=EXCLUDED, priority=30),
            rule("millennia-base", "1", cap="1000", cap_group="base", excludes=EXCLUDED, priority=5),
        ],
    },
    {
        "id": "swiggy-hdfc", "name": "Swiggy HDFC Bank Credit Card", "issuer": "HDFC Bank",
        "network": "Mastercard", "annual_fee": "500", "fee_waiver": "200000", "accent": "#f06a35",
        "featured": "Food, grocery and dining",
        "source": "https://www.hdfc.bank.in/credit-cards/swiggy-hdfc-bank-credit-card",
        "rules": [
            rule("swiggy-app", "10", merchants=["swiggy"], channels=["In-app"], cap="1500", cap_group="swiggy", excludes=EXCLUDED, priority=40),
            rule("swiggy-online", "5", categories=["Online shopping", "Dining", "Groceries", "Food delivery", "Entertainment"], channels=["Online", "In-app"], cap="1500", cap_group="online", excludes=EXCLUDED, priority=20),
            rule("swiggy-base", "1", cap="500", cap_group="base", excludes=EXCLUDED, priority=5),
        ],
    },
    {
        "id": "flipkart-axis", "name": "Flipkart Axis Bank Credit Card", "issuer": "Axis Bank",
        "network": "Visa", "annual_fee": "500", "fee_waiver": "350000", "accent": "#5969e9",
        "featured": "Flipkart and Myntra shopping",
        "source": "https://www.axisbank.com/retail/cards/credit-card/flipkart-axisbank-credit-card/features-benefits",
        "rules": [
            rule("flipkart-myntra", "7.5", merchants=["myntra"], cap="4000", cap_group="myntra-quarter", excludes=EXCLUDED, priority=40),
            rule("flipkart-core", "5", merchants=["flipkart", "cleartrip"], cap="4000", cap_group="core-quarter", excludes=EXCLUDED, priority=30),
            rule("flipkart-base", "1", excludes=EXCLUDED, priority=5),
        ],
    },
    {
        "id": "airtel-axis", "name": "Airtel Axis Bank Credit Card", "issuer": "Axis Bank",
        "network": "Mastercard", "annual_fee": "500", "fee_waiver": "200000", "accent": "#e5484d",
        "featured": "Telecom, utilities and food",
        "source": "https://www.axisbank.com/docs/default-source/default-document-library/credit-cards/terms-and-conditions-for-cashback-for-airtel-axis-bank-credit-card.pdf/1000",
        "rules": [
            rule("airtel-bills", "25", categories=["Telecom"], merchants=["airtel"], channels=["In-app"], cap="250", cap_group="airtel", excludes=EXCLUDED, priority=50),
            rule("airtel-utility", "10", categories=["Utilities"], channels=["In-app"], cap="250", cap_group="utility", excludes=EXCLUDED, priority=40),
            rule("airtel-food", "10", merchants=["swiggy", "zomato", "bigbasket"], channels=["In-app"], cap="500", cap_group="preferred", excludes=EXCLUDED, priority=35),
            rule("airtel-base", "1", excludes=EXCLUDED, priority=5),
        ],
    },
    {
        "id": "hsbc-live-plus", "name": "HSBC Live+ Credit Card", "issuer": "HSBC India",
        "network": "Visa", "annual_fee": "999", "fee_waiver": "200000", "accent": "#db3340",
        "featured": "Dining and grocery cashback",
        "source": "https://www.hsbc.co.in/credit-cards/products/live-plus/",
        "rules": [
            rule("liveplus-accelerated", "10", categories=["Dining", "Groceries", "Food delivery"], cap="1000", cap_group="accelerated", excludes=EXCLUDED, priority=30),
            rule("liveplus-base", "1.5", excludes=EXCLUDED + ["tolls"], priority=5),
        ],
    },
    {
        "id": "axis-cashback", "name": "Axis Bank Cashback Credit Card", "issuer": "Axis Bank",
        "network": "Visa", "annual_fee": "1000", "fee_waiver": "400000", "accent": "#6856d6",
        "featured": "Tiered online cashback",
        "source": "https://www.axisbank.com/docs/default-source/ld/axis-bank-cashback-credit-card-tnc.pdf",
        "rules": [
            rule("axis-cb-online", "7", channels=["Online", "In-app"], cap="4000", cap_group="online", excludes=EXCLUDED, priority=20, note="Tier maximum; actual tier depends on cumulative monthly online spend."),
            rule("axis-cb-base", "0.75", channels=["Offline"], excludes=EXCLUDED, priority=5),
            rule("axis-cb-travel", "0.75", categories=["Travel"], excludes=EXCLUDED, priority=10),
        ],
    },
]


def get_catalog() -> list[dict]:
    return deepcopy(CARDS)


def get_card(card_id: str) -> dict | None:
    return next((deepcopy(card) for card in CARDS if card["id"] == card_id), None)
