import os
from dotenv import load_dotenv
from extract.opensky import extract_opensky
from transform.basic_transform import transform_basic
from load.csv_writer import write_csv
from pathlib import Path
from datetime import datetime
import pandas as pd

# Charger les variables d'environnement (sécurité)
load_dotenv()

# Dossier de sortie
OUTPUT_DIR = Path("csv_history")
OUTPUT_DIR.mkdir(exist_ok=True)

def clean_transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoyage avancé pour visualisation Tableau :
    - Sélection des colonnes utiles
    - Suppression des lignes sans latitude, longitude ou callsign
    """
    df = transform_basic(df)  # Transformation de base

    # Colonnes à conserver
    keep_columns = [
        "callsign",
        "origin_country",
        "latitude",
        "longitude",
        "velocity_kmh",
        "is_flying",
        "baro_altitude",
        "geo_altitude",
        "last_contact"
    ]
    df = df[keep_columns]

    # Supprimer les lignes sans callsign
    df = df[df["callsign"] != ""]

    return df

def run_pipeline():
    # 1. Extraction
    df_raw = extract_opensky()
    print(f"[INFO] Extraction terminée : {df_raw.shape[0]} lignes")

    # 2. Nettoyage + Transformation avancée
    df_clean = clean_transform(df_raw)
    print(f"[INFO] Nettoyage et transformation terminés : {df_clean.shape[0]} lignes")

    # 3. Générer nom de fichier horodaté
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = OUTPUT_DIR / f"opensky_flights_{timestamp}.csv"

    lines_removed = df_raw.shape[0] - df_clean.shape[0]
    print(f"[INFO] Lignes supprimées : {lines_removed}")

    # 4. Export CSV
    write_csv(df_clean, output_file)
    print(f"[INFO] CSV final créé : {output_file} ({output_file.stat().st_size/1024:.2f} KB)")

if __name__ == "__main__":
    run_pipeline()