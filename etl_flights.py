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

    # Vérifier si "states" contient des données
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
    if df.empty:
        return df  # Retourner directement si df est vide

    # 🔹 Supprimer uniquement les lignes totalement vides
    df = df.dropna(how='all')

    # 🔹 Vérifier si les colonnes critiques contiennent des valeurs
    if 'baro_altitude' in df.columns and df['baro_altitude'].isnull().all():
        print("⚠️ Toutes les valeurs de 'baro_altitude' sont manquantes !")
        return pd.DataFrame()  # Retourner un DataFrame vide pour éviter des erreurs

    # 🔹 Convertir les timestamps UNIX en format lisible
    if 'time_position' in df.columns:
        df['time_position'] = df['time_position'].apply(
            lambda x: datetime.utcfromtimestamp(x) if pd.notnull(x) and x > 0 else None
        )

    # 🔹 Ajouter une colonne altitude en pieds
    df["altitude_feet"] = df["baro_altitude"].fillna(0) * 3.281  

    return df

# 💾 CHARGEMENT : Stocker dans SQLite
def load_to_sqlite(df, db_name="flights.db"):
    if df.empty:
        print("⚠️ Aucune donnée à charger dans SQLite.")
        return  

    conn = sqlite3.connect(db_name)
    df.to_sql("flights", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Données chargées dans SQLite")

# 📤 EXPORTATION : Envoyer une seule ligne vers Google Forms
def export_to_google_sheets(df):
    try:
        if df.empty:
            print("⚠️ Aucune donnée à envoyer (DataFrame vide).")
            return  

        # 🔹 URL de soumission du formulaire
        google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeLHPzL4U5fdEU_tHkmqwxpTxdb82MauFSXYGhUKkNcysMcwQ/formResponse"

        # 🔹 ID du champ "Données" trouvé dans DevTools
        form_entry_id = "entry.1319407633"  # ⚠️ Remplace par l'ID réel du champ

        # 🔹 Prendre uniquement la première ligne du DataFrame et la convertir en texte
        first_row = df.iloc[0].to_string(index=False)

        # 🔹 Envoyer sous forme de dictionnaire
        form_data = { form_entry_id: first_row }

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

        # Vérifier si l'extraction a bien fonctionné
        if df.empty:
            print("⚠️ Aucune donnée récupérée depuis l'API OpenSky. Attente avant la prochaine exécution...")
            time.sleep(3600)
            continue  

        # 🔹 Afficher les 5 premières lignes avant transformation
        print("📊 Données brutes extraites :")
        print(df.head())

        # 2️⃣ Transformation
        df_clean = transform_flight_data(df)

        # 🔹 Vérifier si des données ont été supprimées pendant la transformation
        print("📊 Données après transformation :")
        print(df_clean.head())

        # Vérifier si les données transformées sont vides
        if df_clean.empty:
            print("⚠️ Les données transformées sont vides. Vérifiez la logique de transformation.")
            time.sleep(3600)
            continue  

        # 3️⃣ Chargement en base SQLite
        load_to_sqlite(df_clean)

        # 🔹 Debug : Afficher les premières lignes avant l'envoi
        print("📊 Données envoyées à Google Forms :")
        print(df_clean.head())

        # 4️⃣ Export vers Google Sheets
        export_to_google_sheets(df_clean)

        print("✅ Pipeline exécuté avec succès ! Attente 1 heure...")
        time.sleep(3600)  # Exécuter toutes les heures