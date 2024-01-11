import requests
import gzip
from io import BytesIO
import pandas as pd

# URL zur gz-Datei
url_weather_data = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_station/ACW00011604.csv.gz"

response = requests.get(url_weather_data)
compressed_file = BytesIO(response.content)
decompressed_file = gzip.open(compressed_file, 'rt')

df = pd.read_csv(decompressed_file, header=None)

print(df)