
import pandas as pd
import requests
from io import StringIO

# URL zur Webseite
url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"

# Senden Sie eine GET-Anfrage an die URL
response = requests.get(url)

if response.status_code == 200:
    data = StringIO(response.text)
    df = pd.read_csv(data, delim_whitespace=True, header=None, error_bad_lines=False)
    print(df)
else:
    print("Fehler beim Abrufen der Daten:", response.status_code)