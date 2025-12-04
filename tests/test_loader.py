"""
Tests unitaires pour le module de chargement
"""

import unittest
import pandas as pd
import sqlite3
import tempfile
import os
from pathlib import Path
from src.loader import load_to_sqlite, get_db_stats


class TestLoader(unittest.TestCase):
    """Tests du module de chargement"""

    def setUp(self):
        """Préparation avant chaque test"""
        # Créer une base de données temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")

        self.sample_data = pd.DataFrame(
            {
                "icao24": ["a", "b", "c"],
                "callsign": ["call1", "call2", "call3"],
                "origin_country": ["US", "FR", "DE"],
                "latitude": [10.0, 20.0, 30.0],
                "longitude": [1.0, 2.0, 3.0],
                "baro_altitude": [100, 200, 300],
            }
        )

    def tearDown(self):
        """Nettoyage après chaque test"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_load_to_sqlite_success(self):
        """Test chargement réussi"""
        success = load_to_sqlite(self.sample_data, self.db_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.db_path))

        # Vérifier que les données sont bien chargées
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM flights")
        count = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(count, 3)

    def test_load_to_sqlite_empty_dataframe(self):
        """Test avec DataFrame vide"""
        empty_df = pd.DataFrame()

        success = load_to_sqlite(empty_df, self.db_path)

        self.assertFalse(success)

    def test_load_to_sqlite_append_mode(self):
        """Test mode append"""
        # Premier chargement
        load_to_sqlite(self.sample_data, self.db_path, if_exists="replace")

        # Deuxième chargement en append
        load_to_sqlite(self.sample_data, self.db_path, if_exists="append")

        # Vérifier le nombre de lignes
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM flights")
        count = cursor.fetchone()[0]
        conn.close()

        # 3 + 3 = 6 lignes
        self.assertEqual(count, 6)

    def test_get_db_stats_success(self):
        """Test récupération des stats"""
        load_to_sqlite(self.sample_data, self.db_path)

        stats = get_db_stats(self.db_path)

        self.assertIsNotNone(stats)
        self.assertEqual(stats["row_count"], 3)
        self.assertEqual(stats["table"], "flights")

    def test_get_db_stats_nonexistent_db(self):
        """Test stats avec BD inexistante"""
        stats = get_db_stats("/nonexistent/path/db.db")

        self.assertIsNone(stats)


if __name__ == "__main__":
    unittest.main()
