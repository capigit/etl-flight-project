# ETL OpenSky Flights (CSV + Tableau Public Web)

## Objectif
Collecter les vols en temps réel via l'API OpenSky, transformer les données si nécessaire, et exporter un CSV horodaté pour visualisation sur Tableau Public Web.

---

## Structure du projet

- `extract/opensky.py` : extraction des données OpenSky
- `transform/basic_transform.py` : nettoyage minimal et création de colonnes utiles
- `load/csv_writer.py` : export CSV
- `pipeline_csv_timestamp.py` : pipeline complet avec fichiers horodatés
- `.env` : variables d'environnement (sécurité)
- `csv_history/` : fichiers CSV horodatés
- `requirements.txt` : dépendances Python

---

## Installation

1. Créer un environnement virtuel :

```powershell
python -m venv venv
venv\Scripts\activate