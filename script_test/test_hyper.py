from extract.opensky import extract_opensky
from transform.basic_transform import transform_basic
from load.hyper_writer import write_hyper

df = extract_opensky()
df = transform_basic(df)

write_hyper(df, "opensky_flights.hyper")

print("Fichier opensky_flights.hyper créé")