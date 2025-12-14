from extract.opensky import extract_opensky
from transform.basic_transform import transform_basic
from load.csv_writer import write_csv

df = extract_opensky()
df = transform_basic(df)

write_csv(df, "opensky_flights.csv")

print("Fichier opensky_flights.csv créé")