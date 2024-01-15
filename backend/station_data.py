import pandas as pd
import requests
from io import StringIO
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime

def _get_stations_() -> pd.DataFrame:
    """gets all stations

    Return: df with id and name
    """
    # URL zur Webseite
    url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"

    # Senden Sie eine GET-Anfrage an die URL
    response = requests.get(url)

    if response.status_code == 200:
        data = StringIO(response.text)
        df = pd.read_fwf(data, colspecs=[(0, 11), (12,20), (21,30), (41,71)], names=['id', 'latitude', 'longitude', 'name'], header=None)
    else:
        print("Fehler beim Abrufen der Daten:", response.status_code)

    return df

def _get_inventory_() -> pd.DataFrame:
    """gets the inventory of all stations
    
    Return: df with id, element, first_year and last_year
    """

    # URL zur Webseite
    url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"

    # Senden Sie eine GET-Anfrage an die URL
    response = requests.get(url)

    if response.status_code == 200:
        data = StringIO(response.text)
        df = pd.read_fwf(data, colspecs=[(0, 11),  (31,35), (36,40), (41,45)], names=['id',  'element', 'first_year', 'last_year'], header=None) #(12,20), (21, 30), 'latitude', 'longitude',
        df = df.loc[(df['element'] == 'TMAX') | (df['element'] == 'TMIN')]
        df = df[['id',  'first_year', 'last_year']] #'latitude','longitude',
        df = df.drop_duplicates(subset=['id'])
    else:
        print("Fehler beim Abrufen der Daten:", response.status_code)
    
    return df

def load_stations() -> None:
    """loads stations and inventory and saves it in a csv file"""
    df_stations = _get_stations_()
    df_inventory = _get_inventory_()

    df = pd.merge(df_stations, df_inventory, on='id', how='outer')

    df.to_csv('stations.csv', index=False)

def _get_combine_stations_and_inventory_() -> pd.DataFrame:
    """combines stations and inventory and saves it in a csv file
    
    Return: df with id, name, latitude, longitude, element, first_year and last_year
    """
    try: 
        print("try loading from File")
        df = pd.read_csv('stations.csv')
    except:
        print('File not found, loading from Web')
        load_stations()
        df = pd.read_csv('stations.csv')

    return df

def _calculate_distance_(lat1: float, lon1: float, lat2:float, lon2:float) -> float:
    """calculates the distance between two points on earth with the haversine formula
    
    Keyword arguments:
    lat and lon from position 1 and two
    Return: distance in km
    """
    
    # Umrechnung von Grad zu Radian
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine Formel
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    # Radius der Erde in Kilometern
    R = 6371.0
    distance = R * c

    return distance

def get_stations(latitude: float, longitude: float, radius: float, start: int , end: int, selection: int = None) -> pd.DataFrame:
    """gets all stations in a given radius

    Keyword arguments:
    longitude, latitude, radius, start, end and selection
    Return: df with id, name, latitude, longitude, element, first_year and last_year
    """
    df = _get_combine_stations_and_inventory_()

    df['distance'] = df.apply(lambda row: _calculate_distance_(latitude, longitude, row['latitude'], row['longitude']), axis=1)
    df = df.sort_values(by=['distance'])
    df = df.head(selection)
    df = df.loc[
        (df['distance'] <= radius) 
        & (df['first_year'] >= start) 
        & (df['last_year'] <= end)
        ]
    
def get_station_by_name(name: str) -> pd.DataFrame:
    """gets all stations with a given name
    
    Keyword arguments:
    name
    Return: df with id, name, latitude, longitude, element, first_year and last_year
    """
    df = _get_combine_stations_and_inventory_()
    df = df.loc[df['name'].str.contains(name, case=False)]
    
    return df
