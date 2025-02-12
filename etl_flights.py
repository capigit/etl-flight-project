import requests
import pandas as pd
import sqlite3
import time
from datetime import datetime

# 🟢 EXTRACTION : Récupérer les données de vol
def extract_flight_data():
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)
    data = response.json()
    
    columns = ["icao24", "callsign", "origin_country", "time_position", "last_contact", 
               "longitude", "latitude", "baro_altitude", "on_ground", "velocity"]
    flights = pd.DataFrame(data["states"], columns=columns)
    return flights

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

# 🚀 PIPELINE AUTOMATIQUE (Exécution continue toutes les heures)
if __name__ == "__main__":
    while True:
        print("🔄 Exécution du pipeline ETL...")
        df = extract_flight_data()
        df_clean = transform_flight_data(df)
        load_to_sqlite(df_clean)
        print("✅ Pipeline exécuté avec succès ! Attente 1 heure...")
        time.sleep(3600)  # Exécuter toutes les heures