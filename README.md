# ✈️ **ETL Flight Data Project**  

Ce projet a pour but d'extraire, transformer et charger (ETL) les données de vol en temps réel depuis l'API OpenSky Network, puis de les stocker dans une base de données **SQLite** et de les exporter vers **Google Sheets**. Enfin, les données sont visualisées avec **Tableau Public**.  

---

## 📥 **Installation & Téléchargement**  

### **1️⃣ Prérequis**  
Avant de commencer, assurez-vous d'avoir installé les outils suivants :  
- **Python 3.x** ✅  
- **pip** (gestionnaire de paquets Python) ✅  
- **SQLite** (déjà inclus avec Python) ✅  
- **Tableau Public** (pour la visualisation) ✅  

---

### **2️⃣ Cloner le projet**  
Ouvrez un terminal et exécutez la commande suivante :  
```sh
git clone https://github.com/capigit/etl-flight-project.git
cd etl-flight-project
```

---

### **3️⃣ Installer les dépendances**  
Dans le dossier du projet, installez les bibliothèques nécessaires avec :  
```sh
pip install -r requirements.txt
```
📦 **Les bibliothèques utilisées :**  
- `requests` → Récupération des données de l'API OpenSky  
- `pandas` → Transformation et manipulation des données  
- `sqlite3` → Stockage en base de données locale  
- `gspread` → Exportation vers Google Sheets  
- `google-auth` → Authentification Google  

---

## 🚀 **Exécution du pipeline ETL**  

### **1️⃣ Lancer le script ETL**  
Exécutez le script en local :  
```sh
python etl_flights.py
```
🔄 **Ce que fait le script :**  
✔️ **Extraction** → Récupère les données de l'API OpenSky Network  
✔️ **Transformation** → Nettoie et formate les données (altitude en pieds, suppression des valeurs nulles...)  
✔️ **Chargement** → Stocke les données dans une base **SQLite**  
✔️ **Exportation** → Envoie les données vers **Google Sheets**  

---

### **2️⃣ Vérifier la base de données SQLite**  
Vous pouvez interagir avec la base de données en exécutant :  
```sh
sqlite3 flights.db
```
Puis, dans l'invite SQLite :  
```sql
SELECT * FROM flights LIMIT 10;
```
Cela affichera les 10 premières lignes des vols enregistrés.

---

## 📊 **Visualisation avec Tableau Public**  

### **1️⃣ Ouvrir Tableau Public**  
- **Importer la base de données** (`flights.db`)  
- Sélectionner la table `flights`  
- **Créer des visualisations** :
  - **Carte des vols** → en utilisant `Latitude` et `Longitude`
  - **Évolution des altitudes** → `Horodateur` en colonnes et `Altitude` en lignes  
  - **Répartition par pays** → `Pays d'origine` en couleurs  

---

## 🔍 **Tests en local**  

### **1️⃣ Vérifier si les données sont bien récupérées**  
Lancez :  
```sh
python etl_flights.py
```
Si vous voyez **⚠️ Aucune donnée récupérée**, vérifiez votre connexion ou si l'API OpenSky est disponible.

### **2️⃣ Vérifier que la base SQLite fonctionne**  
```sh
sqlite3 flights.db
SELECT COUNT(*) FROM flights;
```
Si le nombre de lignes est `0`, cela signifie que le pipeline n’a pas stocké de données.

### **3️⃣ Vérifier l'exportation vers Google Sheets**  
- Allez sur **Google Sheets** et ouvrez votre feuille  
- Vérifiez si les nouvelles données sont bien ajoutées  

---

## 📌 **Améliorations possibles**  
✅ Automatiser l’exécution avec **cron jobs** sous Linux ou **Task Scheduler** sous Windows  
✅ Ajouter un dashboard interactif avec **Streamlit**  
✅ Stocker les données dans une base **PostgreSQL** au lieu de SQLite  

---

## ✉️ **Support**  
Si vous avez des questions ou rencontrez des problèmes, contactez-moi via **GitHub Issues** ou par email 📧.  

🎯 **Bon développement et bon vol !** 🚀