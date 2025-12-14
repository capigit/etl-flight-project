# 🛫 ETL OpenSky Flights Pipeline

Pipeline ETL automatisé pour collecter, traiter et visualiser les données de vols en temps réel depuis l'API OpenSky.

**[Voir la visualisation interactive sur Tableau Public](https://public.tableau.com/app/profile/alpha.amadou.balde/viz/AutomatedOpenSkyETLPipeline/Cartedesvolsactifs)**

---

## 📋 Vue d'ensemble

Ce projet implémente un pipeline ETL complet qui :
- 📡 **Extrait** les données de vols en temps réel via l'API OpenSky
- 🔄 **Transforme** les données pour enrichir et nettoyer les informations
- 💾 **Charge** les données dans des fichiers CSV horodatés
- 📊 **Visualise** les résultats dans Tableau Public

---

## 📁 Structure du projet

```
etl-flight-project/
├── extract/
│   └── opensky.py              # Extraction des données OpenSky API
├── transform/
│   └── basic_transform.py      # Nettoyage et enrichissement des données
├── load/
│   └── csv_writer.py           # Écriture des données CSV
├── script_test/
│   ├── test_csv.py
│   ├── test_env.py
│   ├── test_extract.py
│   ├── test_hyper.py
│   └── test_transform.py
├── config/
│   └── config.yml              # Configuration du projet
├── csv_history/                # Historique des fichiers CSV horodatés
├── pipeline_csv.py             # Pipeline principal
├── requirements.txt            # Dépendances Python
├── .env                        # Variables d'environnement
└── README.md                   # Ce fichier
```

---

## 🚀 Installation

### 1. Cloner le repository
```bash
git clone <https://github.com/capigit/etl-flight-project>
cd etl-flight-project
```

### 2. Créer un environnement virtuel
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances
```powershell
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
```powershell
# Créer un fichier .env avec :
OPENSKY_USERNAME=votre_username
OPENSKY_PASSWORD=votre_password
```

---

## ⚙️ Configuration

Éditer `config/config.yml` pour personnaliser :
- Les paramètres d'extraction (limites géographiques, altitude, etc.)
- Les chemins de sortie
- Les paramètres de transformation

---

## 🏃 Exécution

### Pipeline complet avec horodatage
```powershell
python pipeline_csv.py
```

Cela va :
1. Extraire les données de l'API OpenSky
2. Transformer et enrichir les données
3. Exporter un CSV horodaté dans `csv_history/`
4. Sauvegarder une copie dans `opensky_flights.csv`

---

## 🧪 Tests

Exécuter les tests du projet :
```powershell
python -m pytest script_test/
```

Tests disponibles :
- `test_extract.py` - Tests d'extraction
- `test_transform.py` - Tests de transformation
- `test_csv.py` - Tests d'écriture CSV
- `test_env.py` - Tests de configuration
- `test_hyper.py` - Tests hyperparamètres

---

## 📊 Visualisation

Les données sont automatiquement synchronisées avec un tableau de bord Tableau Public :

**[Carte des vols actifs - Tableau Public](https://public.tableau.com/app/profile/alpha.amadou.balde/viz/AutomatedOpenSkyETLPipeline/Cartedesvolsactifs)**

Les données se mettent à jour automatiquement avec chaque exécution du pipeline.

---

## 🔐 Sécurité

⚠️ **Important** : Ajouter à `.gitignore` :
- `.env` - Variables d'environnement
- `credentials.json` - Identifiants
- `venv/` - Environnement virtuel
- `__pycache__/` - Fichiers compilés

---

## 📝 Format des données

### Entrée (OpenSky API)
Données brutes des vols en temps réel (ICAO24, callsign, latitude, longitude, altitude, etc.)

### Sortie (CSV)
Fichiers CSV horodatés avec colonnes enrichies dans `csv_history/` et export courant dans `opensky_flights.csv`

---

## 🛠️ Dépendances principales

- `requests` - Requêtes HTTP
- `pandas` - Manipulation de données
- `python-dotenv` - Gestion des variables d'environnement
- `pyyaml` - Configuration YAML

Voir `requirements.txt` pour la liste complète.

---

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs dans les fichiers CSV
2. Consulter la documentation de l'API OpenSky : https://opensky-network.org/apidoc/rest.html
3. Vérifier les tests

---

## 📄 Licence

Voir le fichier [LICENSE](LICENSE) pour plus d'informations.