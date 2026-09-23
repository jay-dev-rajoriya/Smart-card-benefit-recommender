"""Tests for the SQLite storage layer."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class DatabaseTests(unittest.TestCase):
    def test_database_initialization_and_demo_cards(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_directory = Path(temporary_directory) / "database"
            database_path = database_directory / "smartcard.db"

            with (
                patch.object(database, "DATABASE_DIR", database_directory),
                patch.object(database, "DATABASE_PATH", database_path),
            ):
                database.initialize_database()
                database.load_demo_cards(reset_existing=True)

                self.assertTrue(database_path.exists())
                self.assertEqual(len(database.get_cards()), 5)
                self.assertEqual(database.get_transactions(), [])


if __name__ == "__main__":
    unittest.main()
