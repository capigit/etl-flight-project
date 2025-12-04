"""
Module de chargement des données dans SQLite
"""

import logging
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def load_to_sqlite(
    df: pd.DataFrame,
    db_path: str,
    table_name: str = "flights",
    if_exists: str = "append",
) -> bool:
    """
    Charge les données dans une base SQLite.

    Args:
        df: DataFrame à charger
        db_path: Chemin vers la base SQLite
        table_name: Nom de la table
        if_exists: Action si table existe ('append', 'replace', 'fail')

    Returns:
        True si succès, False sinon
    """
    if df.empty:
        logger.warning(f"⚠️  Aucune donnée à charger dans {db_path}")
        return False

    try:
        # Créer le dossier s'il n'existe pas
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"💾 Chargement de {len(df)} lignes dans {db_path}")

        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        conn.close()

        logger.info(f"✅ Données chargées dans {table_name} ({if_exists} mode)")
        return True

    except sqlite3.DatabaseError as e:
        logger.error(f"❌ Erreur base de données: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement SQLite: {e}", exc_info=True)
        return False


def get_db_stats(db_path: str, table_name: str = "flights") -> Optional[dict]:
    """
    Récupère les statistiques de la base de données.

    Args:
        db_path: Chemin vers la base SQLite
        table_name: Nom de la table

    Returns:
        Dict avec statistiques ou None si erreur
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]

        cursor.execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        schema = cursor.fetchone()

        conn.close()

        return {
            "table": table_name,
            "row_count": row_count,
            "schema": schema[0] if schema else None,
        }

    except Exception as e:
        logger.error(f"❌ Erreur lecture stats DB: {e}")
        return None
