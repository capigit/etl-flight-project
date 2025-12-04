"""
Module d'extraction des données depuis l'API OpenSky Network
"""

import logging
import pandas as pd
import requests
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def extract_flight_data(api_url: str) -> pd.DataFrame:
    """
    Extrait les données de vol depuis l'API OpenSky Network.

    Args:
        api_url: URL de l'API OpenSky

    Returns:
        DataFrame avec les données brutes des vols

    Raises:
        requests.RequestException: En cas d'erreur lors de la requête
    """
    try:
        logger.info(f"📡 Extraction depuis {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "states" not in data or not data["states"]:
            logger.warning("⚠️  Aucune donnée récupérée depuis l'API OpenSky")
            return pd.DataFrame()

        flights = pd.DataFrame(data["states"])

        # Nommer les colonnes selon la documentation OpenSky
        flights.columns = [
            "icao24",
            "callsign",
            "origin_country",
            "time_position",
            "last_contact",
            "longitude",
            "latitude",
            "baro_altitude",
            "on_ground",
            "velocity",
            "true_track",
            "vertical_rate",
            "sensors",
            "geo_altitude",
            "squawk",
            "spi",
            "position_source",
        ]

        logger.info(f"✅ {len(flights)} vols extraits")
        return flights

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout lors de la connexion à l'API OpenSky")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur API OpenSky: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Erreur d'extraction: {e}", exc_info=True)
        raise
