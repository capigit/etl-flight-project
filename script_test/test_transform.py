from extract.opensky import extract_opensky
from transform.basic_transform import transform_basic

df_raw = extract_opensky()
df_transformed = transform_basic(df_raw)

print("Avant :", df_raw.shape)
print("Après :", df_transformed.shape)
print(df_transformed[[
    "callsign", "latitude", "longitude",
    "velocity", "velocity_kmh", "is_flying"
]].head())