# ✈️ **ETL Flight Data Project**

Pipeline de données en temps réel pour les vols aériens avec extraction depuis OpenSky Network, transformation, stockage SQLite et export Google Sheets.

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Tests](#tests)
- [Dépannage](#dépannage)
- [Structure du projet](#structure-du-projet)

---

## 🎯 Vue d'ensemble

Ce projet implémente un **pipeline ETL (Extract-Transform-Load)** complet pour traiter les données de vol en temps réel :

| Étape | Description | Technologie |
|-------|-------------|-------------|
| **Extraction** 📥 | Récupère les données depuis l'API OpenSky Network | `requests` + retry automatique |
| **Transformation** 🔧 | Nettoie, formate et enrichit les données | `pandas` |
| **Validation** ✔️ | Vérifie la qualité des données | Custom validation |
| **Chargement** 💾 | Stocke les données en base SQLite | `sqlite3` |
| **Export** 📊 | Envoie vers Google Sheets (optionnel) | `gspread` |

### **Fonctionnalités principales**

✅ Extraction avec **retry automatique** (3 tentatives avec backoff exponentiel)
✅ Transformation robuste avec gestion des erreurs
✅ **Logging professionnel** avec rotation de fichiers
✅ **Arrêt gracieux** (CTRL+C) sans perdre de données
✅ **Health checks** au démarrage
✅ **Tests unitaires** complets
✅ Gestion centralisée via fichier `.env`
✅ Boucle continue configurble (par défaut 1h)

---

## 🏗️ Architecture

### Diagramme du flux de données

```
API OpenSky Network (HTTP)
         ↓ (requests)
   Extraction
   (extractor.py)
         ↓
   Transformation
   (transformer.py)
         ↓
   Validation
         ↓
   ┌─────┴─────────┐
   ↓               ↓
SQLite         Google Sheets
(loader.py)    (exporter.py)
   ↓
Tableau Public
(Visualisation)
```

### Structure modulaire

```
src/
├── extractor.py      # Extraction API OpenSky + retry
├── transformer.py    # Nettoyage et enrichissement des données
├── loader.py         # Chargement SQLite avec stats
├── exporter.py       # Export Google Sheets
└── health_check.py   # Vérifications de santé du système

config/
├── config.py         # Configuration centralisée + logging
└── __init__.py

tests/
├── test_extractor.py   # Tests du module extraction
├── test_transformer.py # Tests du module transformation
└── test_loader.py      # Tests du module chargement

main.py              # Point d'entrée avec boucle principale
.env                 # Variables d'environnement (à créer)
requirements.txt     # Dépendances Python
```

---

## 📦 Installation

### **Prérequis**

- **Python 3.8+**
- **pip** (gestionnaire de paquets)
- **Git** (optionnel, pour cloner le repo)

### **1️⃣ Cloner ou télécharger le projet**

```bash
git clone https://github.com/capigit/etl-flight-project.git
cd etl-flight-project
```

### **2️⃣ Créer un environnement virtuel**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **3️⃣ Installer les dépendances**

```bash
pip install -r requirements.txt
```

### **4️⃣ Configurer les variables d'environnement**

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos paramètres
# (voir section Configuration)
```

---

## ⚙️ Configuration

### **Variables d'environnement (.env)**

Créez un fichier `.env` à la racine du projet (copié depuis `.env.example`) :

```env
# ========== API ==========
OPENSKY_API_URL=https://opensky-network.org/api/states/all

# ========== DATABASE ==========
DATABASE_PATH=./data/flights.db
DB_IF_EXISTS=append  # append, replace, ou fail

# ========== GOOGLE SHEETS (Optionnel) ==========
ENABLE_GOOGLE_SHEETS_EXPORT=false
GOOGLE_SHEET_ID=  # Obtenir depuis l'URL de votre feuille
GOOGLE_CREDENTIALS_PATH=./credentials.json
GOOGLE_WORKSHEET_NAME=flights

# ========== PIPELINE ==========
CYCLE_INTERVAL_SECONDS=3600  # 1 heure par défaut
MAX_RETRIES=3
TIMEOUT_SECONDS=10

# ========== LOGGING ==========
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ========== FEATURES ==========
ENABLE_HEALTH_CHECK=true
ENABLE_VALIDATION=true
```

### **Configuration Google Sheets (Optionnel)**

Si vous voulez exporter vers Google Sheets :

1. **Créer un projet Google Cloud** : https://console.cloud.google.com/
2. **Activer l'API Google Sheets** et **Google Drive API**
3. **Créer une clé de service** :
   - Type de compte : Service Account
   - Télécharger le JSON → `credentials.json` (à la racine du projet)
4. **Partager votre Google Sheet** avec l'email du service account
5. **Obtenir l'ID de la feuille** : depuis l'URL
   ```
   https://docs.google.com/spreadsheets/d/{ID_ICI}/edit
   ```
6. **Mettre à jour `.env`** :
   ```env
   ENABLE_GOOGLE_SHEETS_EXPORT=true
   GOOGLE_SHEET_ID=votre_id
   GOOGLE_CREDENTIALS_PATH=./credentials.json
   ```

---

## 🚀 Utilisation

### **Lancer le pipeline**

```bash
python main.py
```

Le pipeline s'exécutera en boucle continue (1h par défaut entre chaque itération).

**Logs de sortie** :
```
2025-12-04 10:30:15 | root | INFO | ================================================================================
2025-12-04 10:30:15 | root | INFO | 🚀 ETL Flight Project - Pipeline démarré
2025-12-04 10:30:15 | root | INFO |    Cycle: 60 minute(s)
2025-12-04 10:30:15 | root | INFO |    Base de données: ./data/flights.db
```

### **Arrêter le pipeline**

Appuyez sur **CTRL+C** pour arrêt gracieux :

```
^C⚠️  Signal SIGINT (CTRL+C) reçu
🛑 Arrêt gracieux du pipeline en cours...
✅ Pipeline arrêté
📊 Statistiques: 2 itération(s) exécutée(s)
```

---

## 🧪 Tests

### **Lancer tous les tests**

```bash
pytest
```

### **Lancer les tests avec couverture**

```bash
pytest --cov=src --cov-report=html
```

Les rapports détaillés seront dans le dossier `htmlcov/`

### **Tests disponibles**

- `tests/test_extractor.py` - Tests extraction API
- `tests/test_transformer.py` - Tests transformation
- `tests/test_loader.py` - Tests chargement SQLite

### **Exemple de test**

```bash
pytest tests/test_transformer.py -v
```

---

## 📊 Vérification des données

### **Consulter la base SQLite**

```bash
sqlite3 data/flights.db
```

Puis dans le shell SQLite :

```sql
-- Voir le nombre de vols enregistrés
SELECT COUNT(*) FROM flights;

-- Voir les 10 premiers vols
SELECT * FROM flights LIMIT 10;

-- Voir les altitudes moyennes par pays
SELECT origin_country, AVG(baro_altitude) FROM flights GROUP BY origin_country;

-- Voir les derniers vols chargés
SELECT * FROM flights ORDER BY processed_at DESC LIMIT 5;
```

---

## 🔍 Dépannage

### **Problème : "Aucune donnée récupérée"**

**Causes possibles** :
- API OpenSky indisponible (maintenance)
- Connexion Internet manquante
- Timeout réseau

**Solutions** :
```bash
# Vérifier l'API
curl https://opensky-network.org/api/states/all

# Augmenter le timeout
# Éditer .env : TIMEOUT_SECONDS=30
```

### **Problème : "Erreur base de données"**

```bash
# Vérifier l'intégrité de la BD
sqlite3 data/flights.db "PRAGMA integrity_check;"

# Supprimer et recréer
rm data/flights.db
```

### **Problème : "Fichier credentials.json introuvable"**

- Assurez-vous que `credentials.json` est dans le dossier racine
- Vérifier le chemin dans `.env` : `GOOGLE_CREDENTIALS_PATH`

### **Problème : "Tests échouent"**

```bash
# Vérifier l'installation des dépendances de test
pip install -r requirements.txt

# Exécuter les tests en mode verbose
pytest -v --tb=short
```

### **Augmenter le niveau de log pour déboguer**

```env
LOG_LEVEL=DEBUG
```

---

## 📁 Structure du projet

---

## 🧭 Run locally

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Initialize the database (optional):

```powershell
python scripts\init_db.py
```

4. Run tests:

```powershell
pytest -q
```

5. Start the pipeline (single-run mode is supported via environment; default runs loop):

```powershell
python main.py
```


```
etl-flight-project/
├── 📂 src/                    # Modules principaux
│   ├── __init__.py
│   ├── extractor.py          # Extraction API OpenSky
│   ├── transformer.py        # Transformation données
│   ├── loader.py             # Chargement SQLite
│   ├── exporter.py           # Export Google Sheets
│   └── health_check.py       # Vérifications système
│
├── 📂 config/                 # Configuration
│   ├── __init__.py
│   └── config.py             # Config centralisée + logging
│
├── 📂 tests/                  # Tests unitaires
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_transformer.py
│   └── test_loader.py
│
├── 📂 data/                   # Données (créé auto)
│   └── flights.db            # Base SQLite
│
├── 📂 logs/                   # Fichiers de log
│   └── etl_flights.log       # Log rotatif
│
├── 📄 main.py               # Point d'entrée principal
├── 📄 requirements.txt       # Dépendances Python
├── 📄 .env.example          # Variables d'env (exemple)
├── 📄 .env                  # Variables d'env (à créer)
├── 📄 README.md             # Cette documentation
└── 📄 LICENSE               # Licence du projet
**Notes:**
- The file `etl_flights.py` at the repository root has been archived to `archive/etl_flights.py` to avoid duplication with `main.py` and the `src/` modules. Use `main.py` as the entry point.

```

---

## 📊 Améliorations apportées (v1.0)

### Architecture
- ✅ Refactorisation en modules séparés (SOLID)
- ✅ Séparation des responsabilités
- ✅ Structure professionnelle

### Robustesse
- ✅ Retry automatique avec backoff exponentiel
- ✅ Gestion d'erreurs complète
- ✅ Arrêt gracieux (CTRL+C)
- ✅ Validation de données

### Opérationnel
- ✅ Logging professionnel avec rotation
- ✅ Health checks au démarrage
- ✅ Gestion configuration via `.env`
- ✅ Accumulation de données (append mode)

### Qualité
- ✅ Tests unitaires complets
- ✅ Type hints
- ✅ Docstrings détaillées
- ✅ Code formaté et lintable

---

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :

1. Forker le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -am 'Ajoute feature'`)
4. Push la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour détails.

---

## 📞 Support

Pour des questions ou problèmes, ouvrez une issue sur GitHub :
https://github.com/capigit/etl-flight-project/issues

---

**Dernière mise à jour** : Décembre 2025