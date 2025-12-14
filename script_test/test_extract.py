from extract.opensky import extract_opensky

df = extract_opensky()

print(df.shape)
print(df.head(5))