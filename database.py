"""Workspace-isolated SQLite persistence with stable identifiers."""
from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

from catalog import get_catalog

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "smartcard.db"
_active_path: Path | None = None


def configure_workspace(workspace_id: str) -> Path:
    global _active_path
    safe_id = "".join(c for c in workspace_id if c.isalnum() or c in "-_")[:80] or uuid4().hex
    root = Path(tempfile.gettempdir()) / "smartcard-benefit-workspaces"
    root.mkdir(parents=True, exist_ok=True)
    _active_path = root / f"{safe_id}.db"
    return _active_path


def get_connection() -> sqlite3.Connection:
    path = _active_path or DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with get_connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS catalog_cards (id TEXT PRIMARY KEY, payload TEXT NOT NULL, source_url TEXT NOT NULL, reviewed_on TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS user_cards (id TEXT PRIMARY KEY, catalog_card_id TEXT, nickname TEXT, credit_limit TEXT NOT NULL DEFAULT '0', current_balance TEXT NOT NULL DEFAULT '0', opened_on TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(catalog_card_id) REFERENCES catalog_cards(id));
        CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, amount TEXT NOT NULL, merchant TEXT NOT NULL, category TEXT NOT NULL, channel TEXT NOT NULL, transaction_date TEXT NOT NULL, used_card_id TEXT, recommended_card_id TEXT, estimated_reward TEXT NOT NULL, actual_reward TEXT, tags TEXT NOT NULL DEFAULT '[]', note TEXT NOT NULL DEFAULT '', is_refund INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(used_card_id) REFERENCES catalog_cards(id), FOREIGN KEY(recommended_card_id) REFERENCES catalog_cards(id));
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        for card in get_catalog():
            db.execute("INSERT OR REPLACE INTO catalog_cards(id,payload,source_url,reviewed_on,active) VALUES(?,?,?,?,1)", (card["id"], json.dumps(card), card["source"], "2026-10-16"))


def get_catalog_cards() -> list[dict[str, Any]]:
    with get_connection() as db:
        return [json.loads(r["payload"]) for r in db.execute("SELECT payload FROM catalog_cards WHERE active=1 ORDER BY id")]


def add_custom_catalog_card(card: dict[str, Any]) -> str:
    """Persist a user-defined card in the active anonymous workspace."""
    card_id = card.get("id") or f"custom-{uuid4().hex}"
    payload = {**card, "id": card_id, "custom": True, "source": ""}
    with get_connection() as db:
        db.execute(
            "INSERT INTO catalog_cards(id,payload,source_url,reviewed_on,active) VALUES(?,?,?,?,1)",
            (card_id, json.dumps(payload), "", payload.get("reviewed_on", "manual")),
        )
    return card_id


def get_user_cards() -> list[dict[str, Any]]:
    with get_connection() as db:
        return [dict(r) for r in db.execute("SELECT * FROM user_cards ORDER BY created_at")]


def add_user_card(catalog_card_id: str, nickname="", credit_limit="0", current_balance="0", opened_on=None) -> str:
    item_id = uuid4().hex
    with get_connection() as db:
        db.execute("INSERT INTO user_cards(id,catalog_card_id,nickname,credit_limit,current_balance,opened_on) VALUES(?,?,?,?,?,?)", (item_id, catalog_card_id, nickname.strip(), str(credit_limit), str(current_balance), opened_on))
    return item_id


def update_user_card(card_id: str, nickname: str, credit_limit, current_balance) -> None:
    with get_connection() as db:
        db.execute("UPDATE user_cards SET nickname=?,credit_limit=?,current_balance=? WHERE id=?", (nickname.strip(), str(credit_limit), str(current_balance), card_id))


def delete_user_card(card_id: str) -> None:
    with get_connection() as db:
        db.execute("DELETE FROM user_cards WHERE id=?", (card_id,))


def add_transaction(data: dict[str, Any]) -> str:
    item_id = data.get("id") or uuid4().hex
    values = (item_id, str(data["amount"]), data["merchant"].strip(), data["category"], data["channel"], str(data["transaction_date"]), data.get("used_card_id"), data.get("recommended_card_id"), str(data.get("estimated_reward", 0)), None if data.get("actual_reward") in (None, "") else str(data["actual_reward"]), json.dumps(data.get("tags", [])), data.get("note", "").strip(), int(bool(data.get("is_refund"))))
    with get_connection() as db:
        db.execute("INSERT INTO transactions(id,amount,merchant,category,channel,transaction_date,used_card_id,recommended_card_id,estimated_reward,actual_reward,tags,note,is_refund) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
    return item_id


def update_transaction(item_id: str, data: dict[str, Any]) -> None:
    with get_connection() as db:
        db.execute("UPDATE transactions SET amount=?,merchant=?,category=?,channel=?,transaction_date=?,used_card_id=?,actual_reward=?,note=?,is_refund=? WHERE id=?", (str(data["amount"]), data["merchant"].strip(), data["category"], data["channel"], str(data["transaction_date"]), data.get("used_card_id"), None if data.get("actual_reward") in (None, "") else str(data["actual_reward"]), data.get("note", "").strip(), int(bool(data.get("is_refund"))), item_id))


def delete_transaction(item_id: str) -> None:
    with get_connection() as db:
        db.execute("DELETE FROM transactions WHERE id=?", (item_id,))


def get_transactions() -> list[dict[str, Any]]:
    with get_connection() as db:
        rows = [dict(r) for r in db.execute("SELECT * FROM transactions ORDER BY transaction_date DESC,created_at DESC")]
    for row in rows:
        row["tags"] = json.loads(row["tags"])
    return rows


def set_setting(key: str, value: Any) -> None:
    with get_connection() as db:
        db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, json.dumps(value)))


def get_setting(key: str, default=None):
    with get_connection() as db:
        row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return default if not row else json.loads(row["value"])


def reset_database() -> None:
    with get_connection() as db:
        db.execute("DELETE FROM transactions")
        db.execute("DELETE FROM user_cards")
        db.execute("DELETE FROM settings")


def load_demo_data() -> None:
    reset_database()
    for card_id, limit in (("sbi-cashback", "120000"), ("amazon-pay-icici", "90000"), ("airtel-axis", "65000")):
        add_user_card(card_id, credit_limit=limit)
    from reward_engine import TransactionContext, rank
    cards = get_catalog_cards()
    samples = [("3299", "Amazon", "Online shopping", "Online", "sbi-cashback", "2026-10-03"), ("1198", "Swiggy", "Food delivery", "In-app", "airtel-axis", "2026-10-06"), ("2450", "BigBasket", "Groceries", "In-app", "airtel-axis", "2026-10-09"), ("1899", "IndiGo", "Travel", "Online", "amazon-pay-icici", "2026-09-21"), ("799", "Airtel Thanks", "Telecom", "In-app", "airtel-axis", "2026-09-18")]
    for amount, merchant, category, channel, used, day in samples:
        ranked = rank(cards, TransactionContext.create(amount, category, merchant, channel))
        actual = next(x for x in ranked if x["card_id"] == used)
        add_transaction({"amount": amount, "merchant": merchant, "category": category, "channel": channel, "transaction_date": day, "used_card_id": used, "recommended_card_id": ranked[0]["card_id"], "estimated_reward": actual["reward"]})


def get_cards():
    return get_catalog_cards()


def load_demo_cards(reset_existing=False):
    if reset_existing:
        reset_database()
    existing = {c["catalog_card_id"] for c in get_user_cards()}
    for card in get_catalog_cards():
        if card["id"] not in existing:
            add_user_card(card["id"])
    return len(get_user_cards()) - len(existing)
