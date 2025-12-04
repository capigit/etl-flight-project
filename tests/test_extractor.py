"""
Tests unitaires pour le module d'extraction
"""

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.extractor import extract_flight_data


class TestExtractor(unittest.TestCase):
    """Tests du module d'extraction"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.api_url = "https://opensky-network.org/api/states/all"

    @patch("requests.get")
    def test_extract_flight_data_success(self, mock_get):
        """Test extraction réussie"""
        # Mock de la réponse API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "states": [
                [
                    "icao1",
                    "call1",
                    "country1",
                    123,
                    456,
                    1.0,
                    2.0,
                    1000,
                    False,
                    100,
                    45,
                    0,
                    None,
                    900,
                    "0000",
                    False,
                    0,
                ],
                [
                    "icao2",
                    "call2",
                    "country2",
                    124,
                    457,
                    1.1,
                    2.1,
                    1100,
                    False,
                    110,
                    50,
                    1,
                    None,
                    1000,
                    "0001",
                    False,
                    1,
                ],
            ]
        }
        mock_get.return_value = mock_response

        # Exécution
        df = extract_flight_data(self.api_url)

        # Vérification
        self.assertEqual(len(df), 2)
        self.assertIn("icao24", df.columns)
        self.assertIn("latitude", df.columns)
        self.assertEqual(df.iloc[0]["icao24"], "icao1")

    @patch("requests.get")
    def test_extract_flight_data_empty_response(self, mock_get):
        """Test avec réponse vide"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"states": None}
        mock_get.return_value = mock_response

        df = extract_flight_data(self.api_url)

        self.assertTrue(df.empty)

    @patch("requests.get")
    def test_extract_flight_data_timeout(self, mock_get):
        """Test avec timeout"""
        import requests

        mock_get.side_effect = requests.Timeout()

        with self.assertRaises(requests.Timeout):
            extract_flight_data(self.api_url)

    @patch("requests.get")
    def test_extract_flight_data_retry(self, mock_get):
        """Test du mécanisme de retry"""
        import requests

        # Échoue 2 fois, puis réussit
        mock_get.side_effect = [
            requests.ConnectionError(),
            requests.ConnectionError(),
            MagicMock(json=MagicMock(return_value={"states": []})),
        ]

        # Devrait réussir à la 3e tentative
        df = extract_flight_data(self.api_url)
        self.assertTrue(df.empty or isinstance(df, pd.DataFrame))


if __name__ == "__main__":
    unittest.main()
