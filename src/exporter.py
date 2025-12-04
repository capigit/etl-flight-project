"""
Module d'exportation des données vers Google Sheets
"""

import logging
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def export_to_google_sheets(
    df: pd.DataFrame,
    sheet_id: str,
    credentials_path: str,
    worksheet_name: str = "Sheet1",
) -> bool:
    """
    Exporte les données vers Google Sheets.

    Args:
        df: DataFrame à exporter
        sheet_id: ID de la Google Sheet
        credentials_path: Chemin vers le fichier credentials.json
        worksheet_name: Nom de la feuille

    Returns:
        True si succès, False sinon
    """
    if df.empty:
        logger.warning("⚠️  Aucune donnée à exporter (DataFrame vide)")
        return False

    try:
        logger.info(f"📊 Connexion à Google Sheets {sheet_id}")

        # Authentification
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Ouvrir la feuille
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Convertir DataFrame en liste de listes
        data = [df.columns.tolist()] + df.values.tolist()

        logger.info(f"📤 Envoi de {len(df)} lignes vers Google Sheets")

        # Ajouter les données (append mode)
        worksheet.append_rows(data)

        logger.info("✅ Données exportées vers Google Sheets avec succès")
        return True

    except FileNotFoundError:
        logger.error(f"❌ Fichier credentials.json non trouvé: {credentials_path}")
        return False
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"❌ Google Sheet non trouvée: {sheet_id}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur exportation Google Sheets: {e}", exc_info=True)
        return False


def export_to_google_sheets_append_only(
    df: pd.DataFrame,
    sheet_id: str,
    credentials_path: str,
    worksheet_name: str = "Sheet1",
) -> bool:
    """
    Exporte les données en mode append uniquement (sans en-têtes).
    Utilisé pour les exécutions répétées.

    Args:
        df: DataFrame à exporter
        sheet_id: ID de la Google Sheet
        credentials_path: Chemin vers le fichier credentials.json
        worksheet_name: Nom de la feuille

    Returns:
        True si succès, False sinon
    """
    if df.empty:
        logger.warning("⚠️  Aucune donnée à exporter (DataFrame vide)")
        return False

    try:
        logger.info(f"📊 Connexion à Google Sheets {sheet_id}")

        # Authentification
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Ouvrir la feuille
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Convertir DataFrame en liste de listes (sans en-têtes)
        data = df.values.tolist()

        logger.info(f"📤 Ajout de {len(df)} lignes à Google Sheets")

        # Ajouter les données
        worksheet.append_rows(data)

        logger.info("✅ Données ajoutées à Google Sheets avec succès")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur exportation Google Sheets: {e}", exc_info=True)
        return False
