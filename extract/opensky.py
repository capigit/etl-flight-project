import requests
import pandas as pd

OPEN_SKY_URL = "https://opensky-network.org/api/states/all"

def extract_opensky():
    response = requests.get(OPEN_SKY_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    columns = [
        "icao24", "callsign", "origin_country", "time_position",
        "last_contact", "longitude", "latitude", "baro_altitude",
        "on_ground", "velocity", "heading", "vertical_rate",
        "sensors", "geo_altitude", "squawk", "spi", "position_source"
    ]

    return pd.DataFrame(data["states"], columns=columns)