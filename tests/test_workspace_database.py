import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class WorkspaceDatabaseTests(unittest.TestCase):
    def test_workspaces_are_isolated(self):
        with tempfile.TemporaryDirectory() as root, patch.object(database.tempfile, "gettempdir", return_value=root):
            database.configure_workspace("alpha"); database.initialize_database(); database.add_user_card("sbi-cashback")
            self.assertEqual(len(database.get_user_cards()), 1)
            database.configure_workspace("beta"); database.initialize_database()
            self.assertEqual(database.get_user_cards(), [])

    def test_demo_data_uses_stable_card_ids(self):
        with tempfile.TemporaryDirectory() as root, patch.object(database.tempfile, "gettempdir", return_value=root):
            database.configure_workspace("demo"); database.initialize_database(); database.load_demo_data()
            self.assertEqual(len(database.get_catalog_cards()), 8)
            self.assertEqual(len(database.get_user_cards()), 3)
            self.assertTrue(all(t["used_card_id"] for t in database.get_transactions()))

    def test_manual_card_is_added_to_active_catalog(self):
        with tempfile.TemporaryDirectory() as root, patch.object(database.tempfile, "gettempdir", return_value=root):
            database.configure_workspace("custom"); database.initialize_database()
            card_id = database.add_custom_catalog_card({
                "name": "My Card", "issuer": "My Bank", "network": "Visa",
                "annual_fee": "0", "fee_waiver": "0", "accent": "#6658d3",
                "featured": "Custom reward profile", "rules": [{"id": "manual-0", "rate": "3", "categories": ["Dining"], "merchants": [], "channels": [], "cap": None, "cap_group": None, "excludes": [], "membership": None, "priority": 20, "min_amount": "0", "effective_from": "2026-10-17", "note": "User-entered."}],
            })
            cards = database.get_catalog_cards()
            self.assertEqual(len(cards), 9)
            self.assertTrue(any(card["id"] == card_id and card["custom"] for card in cards))
