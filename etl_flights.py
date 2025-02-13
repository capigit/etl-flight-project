import requests
import pandas as pd
import sqlite3
import time
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 🟢 EXTRACTION : Récupérer les données de vol
def extract_flight_data():
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)
    data = response.json()

    # Vérifie si "states" contient des données
    if "states" in data and data["states"]:
        flights = pd.DataFrame(data["states"])  # Charge toutes les colonnes dynamiquement

        # Nommer les colonnes correctement (d'après la doc OpenSky)
        flights.columns = [
            "icao24", "callsign", "origin_country", "time_position", "last_contact",
            "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
            "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
            "spi", "position_source"
        ]
        return flights
    else:
        print("⚠️ Aucune donnée récupérée depuis l'API OpenSky")
        return pd.DataFrame()  # Retourne un DataFrame vide si l'API ne renvoie rien

# 🔧 TRANSFORMATION : Nettoyer et formater les données
def transform_flight_data(df):
    df = df.dropna()
    df["time_position"] = df["time_position"].apply(lambda x: datetime.utcfromtimestamp(x) if x > 0 else None)
    df["altitude_feet"] = df["baro_altitude"] * 3.281  # Conversion mètres → pieds
    return df

# 💾 CHARGEMENT : Stocker dans SQLite
def load_to_sqlite(df, db_name="flights.db"):
    conn = sqlite3.connect(db_name)
    df.to_sql("flights", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Données chargées dans SQLite")
    

# 📤 EXPORTATION : Envoyer les données vers Google Sheets
def export_to_google_sheets(df):
    try:
        # 🔹 URL de soumission du formulaire (remplace par la tienne)
        google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeLHPzL4U5fdEU_tHkmqwxpTxdb82MauFSXYGhUKkNcysMcwQ/formResponse"

        # 🔹 Transformer le DataFrame en un texte lisible pour Google Forms
        data_text = df.to_string(index=False)  # ✅ Format lisible sans sauts de ligne CSV

        # 🔹 Remplace ENTRY_ID par l'ID du champ dans Google Forms
        form_data = {
            "entry.XXXXXXXXX": data_text  # ⚠️ Remplace "XXXXXXXXX" par l'ID exact du champ "Données"
        }

        # 🔹 Envoyer la requête POST
        response = requests.post(google_form_url, data=form_data)

        if response.status_code == 200:
            print("✅ Données envoyées avec succès via Google Form !")
        else:
            print(f"❌ Erreur lors de l'envoi au Google Form : {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erreur d'exportation vers Google Form : {e}")

# 🚀 PIPELINE AUTOMATIQUE (Exécution continue toutes les heures)
if __name__ == "__main__":
    while True:
        print("🔄 Exécution du pipeline ETL...")
        
        # 1️⃣ Extraction
        df = extract_flight_data()
        
        # 2️⃣ Transformation
        df_clean = transform_flight_data(df)
        
        # 3️⃣ Chargement en base SQLite
        load_to_sqlite(df_clean)
        
        # 4️⃣ Export vers Google Sheets
        export_to_google_sheets(df_clean)

        print("✅ Pipeline exécuté avec succès ! Attente 1 heure...")
        time.sleep(3600)  # Exécuter toutes les heures