"""Financial calculators used by the planning workspace."""

from __future__ import annotations

from math import pow
from typing import Any

from cards import CATEGORY_RATE_COLUMNS


def calculate_annual_card_values(
    cards: list[dict[str, Any]], monthly_spend: dict[str, float]
) -> list[dict[str, Any]]:
    """Estimate annual gross rewards and value after the annual fee."""
    results = []
    for card in cards:
        annual_spend = 0.0
        gross_reward = 0.0
        for category, rate_column in CATEGORY_RATE_COLUMNS.items():
            spend = max(0.0, float(monthly_spend.get(category, 0))) * 12
            annual_spend += spend
            gross_reward += spend * float(card.get(rate_column, 0) or 0) / 100

        annual_fee = max(0.0, float(card.get("annual_fee", 0) or 0))
        net_value = gross_reward - annual_fee
        results.append(
            {
                "card_name": card["card_name"],
                "bank_name": card["bank_name"],
                "annual_spend": round(annual_spend, 2),
                "gross_reward": round(gross_reward, 2),
                "annual_fee": annual_fee,
                "net_value": round(net_value, 2),
                "effective_return": round(net_value / annual_spend * 100, 2)
                if annual_spend
                else 0.0,
            }
        )
    return sorted(results, key=lambda row: row["net_value"], reverse=True)


def calculate_emi(
    principal: float, annual_rate: float, months: int, processing_fee_rate: float = 0
) -> dict[str, float]:
    """Return reducing-balance EMI, interest, fees, and total repayment."""
    principal = max(0.0, float(principal))
    annual_rate = max(0.0, float(annual_rate))
    months = max(1, int(months))
    monthly_rate = annual_rate / 1200

    if monthly_rate == 0:
        emi = principal / months
    else:
        growth = pow(1 + monthly_rate, months)
        emi = principal * monthly_rate * growth / (growth - 1)

    repayment = emi * months
    processing_fee = principal * max(0.0, processing_fee_rate) / 100
    return {
        "monthly_emi": round(emi, 2),
        "interest": round(repayment - principal, 2),
        "processing_fee": round(processing_fee, 2),
        "total_cost": round(repayment + processing_fee, 2),
    }


def calculate_utilisation(balance: float, credit_limit: float) -> dict[str, float | str]:
    """Calculate utilisation and a plain-language planning band."""
    if credit_limit <= 0:
        raise ValueError("Credit limit must be greater than zero.")
    ratio = max(0.0, balance) / credit_limit * 100
    if ratio <= 10:
        band = "Low"
    elif ratio <= 30:
        band = "Moderate"
    elif ratio <= 50:
        band = "High"
    else:
        band = "Very high"
    return {"percentage": round(ratio, 1), "band": band}
