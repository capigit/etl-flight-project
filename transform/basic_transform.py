import pandas as pd

def transform_basic(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Nettoyage minimal
    df["callsign"] = df["callsign"].fillna("").str.strip()
    df = df.dropna(subset=["latitude", "longitude"])

    # Champs utiles pour la visualisation
    df["velocity_kmh"] = df["velocity"] * 3.6
    df["is_flying"] = ~df["on_ground"]

    return df