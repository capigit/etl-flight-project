"""
Configuration centralisée du projet ETL Flight
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ==================== PATHS ====================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Créer les répertoires s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ==================== API CONFIGURATION ====================
OPENSKY_API_URL = os.getenv(
    "OPENSKY_API_URL", "https://opensky-network.org/api/states/all"
)

# ==================== DATABASE CONFIGURATION ====================
DATABASE_PATH = os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "data" / "flights.db"))
DATABASE_TABLE = "flights"
DB_IF_EXISTS = os.getenv("DB_IF_EXISTS", "append")  # append, replace, fail

# ==================== GOOGLE SHEETS CONFIGURATION ====================
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CREDENTIALS_PATH", str(PROJECT_ROOT / "credentials.json")
)
GOOGLE_WORKSHEET_NAME = os.getenv("GOOGLE_WORKSHEET_NAME", "flights")

# ==================== PIPELINE CONFIGURATION ====================
CYCLE_INTERVAL_SECONDS = int(
    os.getenv("CYCLE_INTERVAL_SECONDS", "3600")
)  # 1h par défaut
CYCLE_INTERVAL_MINUTES = CYCLE_INTERVAL_SECONDS // 60

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "10"))

# ==================== LOGGING CONFIGURATION ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_FILE = LOGS_DIR / "etl_flights.log"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5

# ==================== FEATURE FLAGS ====================
ENABLE_GOOGLE_SHEETS_EXPORT = (
    os.getenv("ENABLE_GOOGLE_SHEETS_EXPORT", "false").lower() == "true"
)
ENABLE_HEALTH_CHECK = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
ENABLE_VALIDATION = os.getenv("ENABLE_VALIDATION", "true").lower() == "true"


# ==================== LOGGING SETUP ====================
def setup_logging():
    """Configure le système de logging du projet."""
    from logging.handlers import RotatingFileHandler

    # Logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Format
    formatter = logging.Formatter(LOG_FORMAT)

    # Handler console (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler fichier avec rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Reducer verbosity pour les libs externes
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("gspread").setLevel(logging.WARNING)

    root_logger.info("=" * 80)
    root_logger.info("🚀 ETL Flight Project - Pipeline démarré")
    root_logger.info(f"   Cycle: {CYCLE_INTERVAL_MINUTES} minute(s)")
    root_logger.info(f"   Base de données: {DATABASE_PATH}")
    root_logger.info(f"   Log level: {LOG_LEVEL}")
    root_logger.info("=" * 80)


# Afficher la configuration (pour débogage)
def print_config():
    """Affiche la configuration actuellement chargée."""
    config = {
        "OPENSKY_API_URL": OPENSKY_API_URL,
        "DATABASE_PATH": DATABASE_PATH,
        "GOOGLE_SHEET_ID": (
            GOOGLE_SHEET_ID[:10] + "..." if GOOGLE_SHEET_ID else "NOT SET"
        ),
        "CYCLE_INTERVAL_MINUTES": CYCLE_INTERVAL_MINUTES,
        "LOG_LEVEL": LOG_LEVEL,
        "ENABLE_GOOGLE_SHEETS": ENABLE_GOOGLE_SHEETS_EXPORT,
        "ENABLE_HEALTH_CHECK": ENABLE_HEALTH_CHECK,
    }

    logger = logging.getLogger(__name__)
    logger.info("📋 Configuration chargée:")
    for key, value in config.items():
        logger.info(f"   {key}: {value}")
