"""
Tests unitaires pour le module de transformation
"""

import unittest
import pandas as pd
from datetime import datetime
from src.transformer import transform_flight_data, validate_data


class TestTransformer(unittest.TestCase):
    """Tests du module de transformation"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.sample_data = {
            "icao24": ["a", "b", "c"],
            "callsign": ["call1", "call2", "call3"],
            "origin_country": ["US", "FR", "DE"],
            "time_position": [1000, 2000, 3000],
            "last_contact": [1001, 2001, 3001],
            "longitude": [1.0, 2.0, 3.0],
            "latitude": [10.0, 20.0, 30.0],
            "baro_altitude": [100, 200, 300],
            "velocity": [100, 150, 200],
            "on_ground": [False, False, False],
        }

    def test_transform_flight_data_success(self):
        """Test transformation réussie"""
        df = pd.DataFrame(self.sample_data)

        result = transform_flight_data(df)

        self.assertEqual(len(result), 3)
        self.assertIn("altitude_feet", result.columns)
        self.assertIn("processed_at", result.columns)
        # 100 meters * 3.281 = 328.1 feet
        self.assertAlmostEqual(result.iloc[0]["altitude_feet"], 328.1, places=1)

    def test_transform_empty_dataframe(self):
        """Test avec DataFrame vide"""
        df = pd.DataFrame()

        result = transform_flight_data(df)

        self.assertTrue(result.empty)

    def test_transform_removes_rows_without_coordinates(self):
        """Test suppression des lignes sans coordonnées"""
        data = self.sample_data.copy()
        data["latitude"][1] = None
        data["longitude"][1] = None
        df = pd.DataFrame(data)

        result = transform_flight_data(df)

        # 1 ligne supprimée
        self.assertEqual(len(result), 2)

    def test_validate_data_success(self):
        """Test validation réussie"""
        df = pd.DataFrame(self.sample_data)

        is_valid = validate_data(df)

        self.assertTrue(is_valid)

    def test_validate_data_empty(self):
        """Test validation avec DataFrame vide"""
        df = pd.DataFrame()

        is_valid = validate_data(df)

        self.assertFalse(is_valid)

    def test_validate_data_missing_column(self):
        """Test validation avec colonne manquante"""
        df = pd.DataFrame(self.sample_data)
        del df["baro_altitude"]

        is_valid = validate_data(df)

        self.assertFalse(is_valid)

    def test_validate_data_too_many_nulls(self):
        """Test validation avec trop de valeurs manquantes"""
        data = self.sample_data.copy()
        # Ajouter des nulls pour dépasser 50%
        for i in range(10):
            data[f"col_{i}"] = [None] * 3
        df = pd.DataFrame(data)

        is_valid = validate_data(df)

        # Devrait être valide car les colonnes requises n'ont pas trop de nulls
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()
