"""SQLite database functions for the Smart Card Benefit Recommender."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from cards import CATEGORY_RATE_COLUMNS, REAL_WORLD_CARDS, normalize_card_data


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "smartcard.db"


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with rows accessible like dictionaries."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create database tables if they do not already exist."""
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                card_type TEXT NOT NULL,
                annual_fee REAL NOT NULL DEFAULT 0,
                reward_type TEXT NOT NULL,
                shopping_rate REAL NOT NULL DEFAULT 0,
                dining_rate REAL NOT NULL DEFAULT 0,
                fuel_rate REAL NOT NULL DEFAULT 0,
                grocery_rate REAL NOT NULL DEFAULT 0,
                travel_rate REAL NOT NULL DEFAULT 0,
                entertainment_rate REAL NOT NULL DEFAULT 0,
                utility_rate REAL NOT NULL DEFAULT 0,
                online_shopping_rate REAL NOT NULL DEFAULT 0,
                other_rate REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                merchant TEXT NOT NULL,
                category TEXT NOT NULL,
                recommended_card TEXT NOT NULL,
                used_card TEXT NOT NULL,
                recommended_reward REAL NOT NULL DEFAULT 0,
                actual_reward REAL NOT NULL DEFAULT 0,
                missed_reward REAL NOT NULL DEFAULT 0,
                transaction_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        for category_name in CATEGORY_RATE_COLUMNS:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                (category_name,),
            )

        connection.commit()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """Convert a SQLite row into a normal dictionary."""
    if row is None:
        return None
    return dict(row)


def add_card(card_data: dict[str, Any]) -> int:
    """Insert a credit card and return its new database id."""
    normalized = normalize_card_data(card_data)
    columns = list(normalized.keys())
    placeholders = ", ".join(["?"] * len(columns))

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO cards ({', '.join(columns)}) VALUES ({placeholders})",
            tuple(normalized[column] for column in columns),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_cards() -> list[dict[str, Any]]:
    """Return all saved cards ordered by newest first."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM cards ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_card(card_id: int) -> dict[str, Any] | None:
    """Return a single card by id."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        return row_to_dict(cursor.fetchone())


def update_card(card_id: int, card_data: dict[str, Any]) -> None:
    """Update an existing card."""
    normalized = normalize_card_data(card_data)
    assignments = ", ".join([f"{column} = ?" for column in normalized])
    values = [normalized[column] for column in normalized]
    values.append(card_id)

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE cards SET {assignments} WHERE id = ?",
            tuple(values),
        )
        connection.commit()


def delete_card(card_id: int) -> None:
    """Delete a card from the database."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        connection.commit()


def add_transaction(transaction_data: dict[str, Any]) -> int:
    """Insert a transaction recommendation result into history."""
    fields = [
        "amount",
        "merchant",
        "category",
        "recommended_card",
        "used_card",
        "recommended_reward",
        "actual_reward",
        "missed_reward",
        "transaction_date",
    ]

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (
                amount,
                merchant,
                category,
                recommended_card,
                used_card,
                recommended_reward,
                actual_reward,
                missed_reward,
                transaction_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(transaction_data[field] for field in fields),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_transactions() -> list[dict[str, Any]]:
    """Return all transaction history, newest first."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC")
        return [dict(row) for row in cursor.fetchall()]


def clear_transactions() -> None:
    """Remove all transactions. Used by the demo reset option."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM transactions")
        connection.commit()


def clear_cards() -> None:
    """Remove all cards. Used by the demo reset option."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM cards")
        connection.commit()


def load_demo_cards(reset_existing: bool = False) -> int:
    """Load the curated real-world card starter set.

    Args:
        reset_existing: When True, all existing cards and transactions are
            removed first so the starter set begins from a clean state.
    """
    if reset_existing:
        clear_transactions()
        clear_cards()

    existing_names = {card["card_name"] for card in get_cards()}
    cards_added = 0

    for card in REAL_WORLD_CARDS:
        if card["card_name"] not in existing_names:
            add_card(card)
            cards_added += 1

    return cards_added


def reset_database() -> None:
    """Clear project data while keeping the database structure intact."""
    clear_transactions()
    clear_cards()
