import requests
import pandas as pd
import sqlite3
import time
import gspread
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
        gc = gspread.service_account()  # Pas besoin de fichier JSON ici !
        sheet = gc.open_by_key("157Hy-Mytfy_hFuwX9iPdpkSkZ2kh1eqh9NbCLKJuKDo").sheet1
        sheet.clear()  # Efface les anciennes données
        sheet.update([df.columns.values.tolist()] + df.values.tolist())  # Mise à jour
        print("✅ Données mises à jour sur Google Sheets")
    except Exception as e:
        print(f"❌ Erreur d'exportation vers Google Sheets : {e}")

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