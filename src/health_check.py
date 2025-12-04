"""
Module de vérification de l'état du système
"""

import logging
import requests
import sqlite3
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def check_api_health(api_url: str, timeout: int = 5) -> bool:
    """
    Vérifie la disponibilité de l'API OpenSky.

    Args:
        api_url: URL de l'API
        timeout: Timeout en secondes

    Returns:
        True si API accessible, False sinon
    """
    try:
        response = requests.get(api_url, timeout=timeout)
        is_healthy = response.status_code == 200

        if is_healthy:
            logger.info(f"✅ API OpenSky est accessible")
        else:
            logger.warning(f"⚠️  API OpenSky retourne {response.status_code}")

        return is_healthy

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout - API OpenSky ne répond pas")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur API OpenSky: {e}")
        return False


def check_database_health(db_path: str) -> bool:
    """
    Vérifie la santé de la base de données SQLite.

    Args:
        db_path: Chemin vers le fichier SQLite

    Returns:
        True si BD accessible et valide, False sinon
    """
    try:
        if not Path(db_path).exists():
            logger.warning(f"⚠️  Base de données n'existe pas: {db_path}")
            return True  # Ce n'est pas une erreur, elle sera créée

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test de lecture simple
        cursor.execute("SELECT COUNT(*) FROM sqlite_master")
        conn.close()

        logger.info(f"✅ Base de données SQLite est accessible")
        return True

    except sqlite3.DatabaseError as e:
        logger.error(f"❌ Erreur base de données SQLite: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur vérification BD: {e}")
        return False


def check_credentials_file(credentials_path: str) -> bool:
    """
    Vérifie l'existence du fichier credentials Google.

    Args:
        credentials_path: Chemin vers credentials.json

    Returns:
        True si fichier existe, False sinon
    """
    if Path(credentials_path).exists():
        logger.info(f"✅ Fichier credentials trouvé")
        return True
    else:
        logger.warning(f"⚠️  Fichier credentials non trouvé: {credentials_path}")
        return False


def system_health_check(
    api_url: str, db_path: str, credentials_path: str = None
) -> Dict[str, bool]:
    """
    Effectue une vérification globale du système.

    Args:
        api_url: URL de l'API OpenSky
        db_path: Chemin vers la base SQLite
        credentials_path: Chemin vers credentials.json (optionnel)

    Returns:
        Dict avec état de chaque composant
    """
    logger.info("🔍 Démarrage du health check système")

    checks = {
        "api": check_api_health(api_url),
        "database": check_database_health(db_path),
    }

    if credentials_path:
        checks["credentials"] = check_credentials_file(credentials_path)

    all_healthy = all(checks.values())

    if all_healthy:
        logger.info("✅ Tous les systèmes sont fonctionnels")
    else:
        failed = [k for k, v in checks.items() if not v]
        logger.error(f"❌ Systèmes non fonctionnels: {', '.join(failed)}")

    return checks
