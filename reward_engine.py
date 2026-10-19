"""Deterministic Decimal reward evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


MONEY = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class TransactionContext:
    amount: Decimal
    category: str
    merchant: str = ""
    channel: str = "Online"
    membership: str = "Prime"
    tags: tuple[str, ...] = ()

    @classmethod
    def create(cls, amount, category, merchant="", channel="Online", membership="Prime", tags=()):
        return cls(money(amount), category, merchant.strip().lower(), channel, membership, tuple(t.lower() for t in tags))


def _matches(rule: dict, tx: TransactionContext) -> bool:
    if tx.amount < Decimal(str(rule.get("min_amount", 0))):
        return False
    if rule.get("membership") and rule["membership"] != tx.membership:
        return False
    if rule.get("categories") and tx.category not in rule["categories"]:
        return False
    if rule.get("channels") and tx.channel not in rule["channels"]:
        return False
    merchants = rule.get("merchants", [])
    if merchants and not any(name in tx.merchant for name in merchants):
        return False
    if set(rule.get("excludes", [])) & set(tx.tags):
        return False
    return True


def evaluate(card: dict, tx: TransactionContext, cap_usage: dict[str, Decimal] | None = None) -> dict:
    """Return a transparent reward result for one card and transaction."""
    if tx.amount <= 0:
        raise ValueError("Amount must be greater than zero")
    cap_usage = cap_usage or {}
    matches = sorted((r for r in card["rules"] if _matches(r, tx)), key=lambda r: r["priority"], reverse=True)
    if not matches:
        return {"card_id": card["id"], "card_name": card["name"], "reward": money(0), "rate": Decimal("0"), "rule": None, "reason": "No eligible reward rule"}
    selected = matches[0]
    rate = Decimal(selected["rate"])
    raw = tx.amount * rate / Decimal("100")
    remaining = None
    if selected.get("cap"):
        used = money(cap_usage.get(selected["cap_group"], 0))
        remaining = max(Decimal("0"), Decimal(selected["cap"]) - used)
        raw = min(raw, remaining)
    reward = money(raw)
    reason = f"{rate.normalize()}% via {selected['id']}"
    if remaining is not None:
        reason += f"; cap remaining ₹{money(remaining)}"
    return {"card_id": card["id"], "card_name": card["name"], "reward": reward, "rate": rate, "rule": selected, "reason": reason}


def rank(cards: Iterable[dict], tx: TransactionContext, cap_usage_by_card: dict | None = None) -> list[dict]:
    usage = cap_usage_by_card or {}
    results = [evaluate(card, tx, usage.get(card["id"], {})) for card in cards]
    return sorted(results, key=lambda item: (-item["reward"], item["card_name"], item["card_id"]))
