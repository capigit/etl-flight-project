import pandas as pd
from pathlib import Path

def write_csv(df: pd.DataFrame, output_path: str):
    output_path = Path(output_path)
    df.to_csv(output_path, index=False)