import pandas as pd
import requests
from io import StringIO
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime
import time
import numpy as np

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

def calculate_distances(df, latitude, longitude):
    # Umrechnung von Grad zu Radian
    lat1, lon1, lat2, lon2 = map(np.radians, [latitude, longitude, df['latitude'], df['longitude']])

    # Haversine Formel
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # Radius der Erde in Kilometern
    R = 6371.0
    df['distance'] = R * c
    return df

def get_stations(latitude: float, longitude: float, radius: float, start: int , end: int, selection: int = None) -> pd.DataFrame:
    #start_time = time.time()
    df = _get_combine_stations_and_inventory_()
    #print("get_combined: --- %s seconds ---" % (time.time() - start_time))
    #start_time = time.time()
    df = calculate_distances(df, latitude, longitude)
    #print("calculate_distance: --- %s seconds ---" % (time.time() - start_time))
    #start_time = time.time()
    df = df.sort_values(by=['distance'], ascending=True).head(selection).loc[
        (df['distance'] <= radius) 
        & (df['first_year'] <= start) 
        & (df['last_year'] >= end)
        ]
    #print("filter: --- %s seconds ---" % (time.time() - start_time))

    return df
    
def get_station_by_name(name: str) -> pd.DataFrame:
    """gets all stations with a given name
    
    Keyword arguments:
    name
    Return: df with id, name, latitude, longitude, element, first_year and last_year
    """
    df = _get_combine_stations_and_inventory_()
    df = df.loc[df['name'].str.contains(name, case=False)]
    
    return df

if __name__ == "__main__":
    print(get_stations(51.5, 7.5, 10000, 2010, 2020, 10))
