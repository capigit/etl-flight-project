"""
Module de transformation et nettoyage des données
"""

import logging
import pandas as pd
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Constantes de conversion
FEET_PER_METER = 3.281


def transform_flight_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme et nettoie les données de vol.

    Operations:
    - Supprime les lignes totalement vides
    - Convertit les timestamps UNIX en datetime
    - Ajoute une colonne altitude en pieds
    - Supprime les valeurs NaN critiques

    Args:
        df: DataFrame brut depuis l'API

    Returns:
        DataFrame nettoyé et transformé
    """
    if df.empty:
        logger.warning("⚠️  DataFrame vide, retour direct")
        return df

    try:
        logger.info("🔧 Début de la transformation")
        original_size = len(df)

        # 1️⃣ Supprimer les lignes totalement vides
        df = df.dropna(how="all")
        logger.info(f"   → {len(df)} lignes après suppression des lignes vides")

        # 2️⃣ Vérifier les colonnes critiques
        if "baro_altitude" in df.columns and df["baro_altitude"].isnull().all():
            logger.error("❌ Toutes les valeurs de 'baro_altitude' sont manquantes !")
            return pd.DataFrame()

        # 3️⃣ Convertir les timestamps UNIX en format lisible
        if "time_position" in df.columns:
            df["time_position"] = df["time_position"].apply(
                lambda x: (
                    datetime.fromtimestamp(x, timezone.utc)
                    if pd.notnull(x) and x > 0
                    else None
                )
            )
            logger.info("   → Timestamps convertis")

        if "last_contact" in df.columns:
            df["last_contact"] = df["last_contact"].apply(
                lambda x: (
                    datetime.fromtimestamp(x, timezone.utc)
                    if pd.notnull(x) and x > 0
                    else None
                )
            )

        # 4️⃣ Ajouter altitude en pieds
        df["altitude_feet"] = df["baro_altitude"].fillna(0) * FEET_PER_METER
        logger.info("   → Altitude en pieds calculée")

        # 5️⃣ Ajouter timestamp de traitement (timezone-aware UTC)
        df["processed_at"] = datetime.now(timezone.utc)

        # 6️⃣ Supprimer lignes avec coordonnées manquantes (critiques pour Tableau)
        df_before = len(df)
        df = df.dropna(subset=["latitude", "longitude"])
        removed = df_before - len(df)
        if removed > 0:
            logger.info(f"   → {removed} lignes sans coordonnées supprimées")

        logger.info(f"✅ Transformation complétée: {original_size} → {len(df)} lignes")
        return df

    except Exception as e:
        logger.error(f"❌ Erreur de transformation: {e}", exc_info=True)
        return pd.DataFrame()


def validate_data(df: pd.DataFrame) -> bool:
    """
    Valide la qualité des données avant chargement.

    Args:
        df: DataFrame à valider

    Returns:
        True si les données sont valides, False sinon
    """
    if df.empty:
        logger.warning("⚠️  DataFrame vide - validation échouée")
        return False

    required_columns = ["icao24", "latitude", "longitude", "baro_altitude"]

    for col in required_columns:
        if col not in df.columns:
            logger.error(f"❌ Colonne requise manquante: {col}")
            return False

    # Vérifier qu'au moins 50% des données sont non-null pour les colonnes critiques
    for col in required_columns:
        null_pct = df[col].isnull().sum() / len(df) * 100
        if null_pct > 50:
            logger.error(f"❌ {col}: {null_pct:.1f}% de valeurs manquantes")
            return False

    logger.info("✅ Validation des données réussie")
    return True
