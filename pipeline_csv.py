import os
from dotenv import load_dotenv
from extract.opensky import extract_opensky
from transform.basic_transform import transform_basic
from load.csv_writer import write_csv
from pathlib import Path
from datetime import datetime

# Charger les variables d'environnement (sécurité)
load_dotenv()

# Dossier de sortie
OUTPUT_DIR = Path("csv_history")
OUTPUT_DIR.mkdir(exist_ok=True)

def run_pipeline():
    # 1. Extraction
    df_raw = extract_opensky()
    print(f"[INFO] Extraction terminée : {df_raw.shape[0]} lignes")

    # 2. Transformation
    df_transformed = transform_basic(df_raw)
    print(f"[INFO] Transformation terminée : {df_transformed.shape[0]} lignes")

    # 3. Générer nom de fichier horodaté
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = OUTPUT_DIR / f"opensky_flights_{timestamp}.csv"

    # 4. Export CSV
    write_csv(df_transformed, output_file)
    print(f"[INFO] CSV créé : {output_file} ({output_file.stat().st_size/1024:.2f} KB)")

if __name__ == "__main__":
    run_pipeline()