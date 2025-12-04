"""
Script principal du pipeline ETL Flight
Gère l'exécution, les signaux d'interruption et la boucle de pipeline
"""

import logging
import signal
import time
import sys
from typing import Optional
import argparse
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import (
    setup_logging,
    print_config,
    OPENSKY_API_URL,
    DATABASE_PATH,
    GOOGLE_SHEET_ID,
    GOOGLE_CREDENTIALS_PATH,
    CYCLE_INTERVAL_SECONDS,
    ENABLE_GOOGLE_SHEETS_EXPORT,
    ENABLE_HEALTH_CHECK,
    ENABLE_VALIDATION,
    DATABASE_TABLE,
    DB_IF_EXISTS,
    GOOGLE_WORKSHEET_NAME,
)

from src.extractor import extract_flight_data
from src.transformer import transform_flight_data, validate_data
from src.loader import load_to_sqlite, get_db_stats
from src.health_check import system_health_check

# Import optionnel pour l'export Google Sheets
try:
    from src.exporter import export_to_google_sheets

    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

logger = logging.getLogger(__name__)

# Variables globales pour la gestion du cycle
should_stop = False
current_iteration = 0


def signal_handler(sig, frame):
    """
    Gestionnaire de signaux pour arrêt gracieux (CTRL+C, SIGTERM).

    Args:
        sig: Signal reçu
        frame: Frame courant
    """
    global should_stop

    if sig == signal.SIGINT:
        logger.warning("⚠️  Signal SIGINT (CTRL+C) reçu")
    elif sig == signal.SIGTERM:
        logger.warning("⚠️  Signal SIGTERM reçu")

    should_stop = True
    logger.info("🛑 Arrêt gracieux du pipeline en cours...")
    logger.info("   (une dernière itération peut être en cours)")


def setup_signal_handlers():
    """Configure les gestionnaires de signaux pour l'arrêt gracieux."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal_handler)

    logger.info("✅ Gestionnaires de signaux configurés (CTRL+C pour arrêter)")


def run_pipeline_iteration(dry_run: bool = False) -> bool:
    """
    Exécute une itération complète du pipeline ETL.

    Returns:
        True si succès, False sinon
    """
    global current_iteration
    current_iteration += 1

    try:
        logger.info("=" * 80)
        logger.info(f"🔄 Itération #{current_iteration} du pipeline ETL")
        logger.info("=" * 80)

        # ========== EXTRACTION ==========
        logger.info("📥 [1/4] EXTRACTION des données")
        df_raw = extract_flight_data(OPENSKY_API_URL)

        if df_raw.empty:
            logger.warning("⚠️  Aucune donnée extraite, passage de cette itération")
            return False

        logger.info(f"   → {len(df_raw)} vols extraits")

        # ========== TRANSFORMATION ==========
        logger.info("🔧 [2/4] TRANSFORMATION des données")
        df_clean = transform_flight_data(df_raw)

        if df_clean.empty:
            logger.warning("Les données transformées sont vides")
            return False

        logger.info(f"   → {len(df_clean)} vols après nettoyage")

        # ========== VALIDATION ==========
        if ENABLE_VALIDATION:
            logger.info("✔️  [3/4] VALIDATION des données")
            if not validate_data(df_clean):
                logger.error("❌ Validation échouée, arrêt du pipeline")
                return False
        else:
            logger.info("⏭️  [3/4] VALIDATION désactivée (skipped)")

        # ========== CHARGEMENT SQLite ==========
        if dry_run:
            logger.info("🔎 Dry-run mode: skipping load and export steps")
        else:
            logger.info("💾 [4/4] CHARGEMENT dans SQLite")
            success_load = load_to_sqlite(
                df_clean, DATABASE_PATH, table_name=DATABASE_TABLE, if_exists=DB_IF_EXISTS
            )

            if not success_load:
                logger.error("❌ Chargement SQLite échoué")
                return False

            # Afficher les stats DB
            stats = get_db_stats(DATABASE_PATH, DATABASE_TABLE)
            if stats:
                logger.info(f"   → Total en BD: {stats['row_count']} vols")

            # ========== EXPORT GOOGLE SHEETS (OPTIONNEL) ==========
            if ENABLE_GOOGLE_SHEETS_EXPORT:
                if not GSPREAD_AVAILABLE:
                    logger.warning("⚠️  gspread non disponible, export Google Sheets ignoré")
                elif GOOGLE_SHEET_ID:
                    logger.info("📊 EXPORT vers Google Sheets")
                    export_to_google_sheets(
                        df_clean,
                        GOOGLE_SHEET_ID,
                        GOOGLE_CREDENTIALS_PATH,
                        GOOGLE_WORKSHEET_NAME,
                    )
                else:
                    logger.warning("⚠️  GOOGLE_SHEET_ID non configuré, export ignoré")
            else:
                logger.info("⏭️  Export Google Sheets désactivé (skipped)")

        logger.info("=" * 80)
        logger.info("✅ Itération complétée avec succès")
        logger.info("=" * 80)
        return True

    except KeyboardInterrupt:
        logger.info("⛔ Pipeline interrompu par utilisateur")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur critique du pipeline: {e}", exc_info=True)
        return False


def run_pipeline(once: bool = False, dry_run: bool = False):
    """
    Boucle principale du pipeline avec cycle répétitif.
    Arrêt gracieux possible via CTRL+C.
    """
    logger.info(f"🚀 Pipeline démarré - Cycle toutes les {CYCLE_INTERVAL_SECONDS}s")

    try:
        while not should_stop:
            try:
                # Exécuter une itération
                run_pipeline_iteration(dry_run=dry_run)

                if should_stop:
                    break

                # Si mode once, sortir après la première itération
                if once:
                    logger.info("Mode --once activé: sortie après une itération")
                    break

                # Attendre avant la prochaine itération
                logger.info(
                    f"⏳ Attente {CYCLE_INTERVAL_SECONDS}s avant prochaine exécution..."
                )
                time.sleep(CYCLE_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("⛔ Interruption détectée")
                break

    except Exception as e:
        logger.error(f"❌ Erreur non gérée: {e}", exc_info=True)
        raise
    finally:
        logger.info("🛑 Pipeline arrêté")
        logger.info(f"📊 Statistiques: {current_iteration} itération(s) exécutée(s)")


def main():
    """Point d'entrée principal."""
    try:
        parser = argparse.ArgumentParser(description="ETL Flight pipeline runner")
        parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")
        parser.add_argument("--dry-run", action="store_true", help="Run pipeline without loading/exporting data")
        args = parser.parse_args()

        # Configuration du logging
        setup_logging()

        # Afficher la configuration
        print_config()

        # Health check initial (optionnel)
        if ENABLE_HEALTH_CHECK:
            logger.info("🔍 Health check initial...")
            credentials_path = (
                GOOGLE_CREDENTIALS_PATH if ENABLE_GOOGLE_SHEETS_EXPORT else None
            )
            health = system_health_check(
                OPENSKY_API_URL, DATABASE_PATH, credentials_path
            )

            if not health.get("api") or not health.get("database"):
                logger.error(
                    "❌ Health check échoué - certains systèmes ne sont pas disponibles"
                )
                logger.info("   Continuant malgré tout...")

        # Configuration des signaux
        setup_signal_handlers()

        # Lancer le pipeline
        run_pipeline(once=args.once, dry_run=args.dry_run)

    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
