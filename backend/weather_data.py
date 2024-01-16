import json
import requests
import gzip
from io import BytesIO
import pandas as pd
from datetime import datetime
import time

def get_data_from_id(id:str) -> pd.DataFrame:
    """gets Data from a given id
    
    Keyword arguments:
    id
    Return: df with date, element and data_value
    """
    
    # URL zur gz-Datei
    url_weather_data = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_station/{id}.csv.gz"

    response = requests.get(url_weather_data)
    compressed_file = BytesIO(response.content)
    decompressed_file = gzip.open(compressed_file, 'rt')

    df = pd.read_csv(decompressed_file, header=None, names=['id', 'date', 'element', 'data_value','m-flag', 'q-flag', 's-flag', 'obs-time'], usecols=['date', 'element', 'data_value'], dtype={'data_value': float})
    df = df.loc[(df['element'] == 'TMAX') | (df['element'] == 'TMIN')]
    df = df[['date', 'element', 'data_value']]
    df['data_value'] = df['data_value'].apply(lambda x: x / 10)

    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    return df

def filter_data(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """filters the data from a given df
    
    Keyword arguments:
    df
    start
    end
    Return: df with date, element and data_value
    """

    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
    return df

def get_season(date):
    year = str(date.year)
    seasons = {'spring': pd.date_range(start='21/03/'+year, end='20/06/'+year),
               'summer': pd.date_range(start='21/06/'+year, end='22/09/'+year),
               'autumn': pd.date_range(start='23/09/'+year, end='20/12/'+year)}
    if date in seasons['spring']:
        return 'spring'
    if date in seasons['summer']:
        return 'summer'
    if date in seasons['autumn']:
        return 'autumn'
    else:
        return 'winter'

def calc_mean(df: pd.DataFrame, rythm: str) -> pd.DataFrame:
    """calculates the mean of the data from a given df
    
    Keyword arguments:
    df
    start
    end
    rythm
    Return: df with date, element and data_value
    """

    if rythm == 'year':
        df = df.groupby([df['date'].dt.to_period("Y"), 'element'])['data_value'].mean().reset_index()
    elif rythm == 'month':
        df = df.groupby([df['date'].dt.to_period("M"), 'element'])['data_value'].mean().reset_index()
    elif rythm == 'day':
        df = df.groupby([df['date'].dt.to_period("D"), 'element'])['data_value'].mean().reset_index()
    elif rythm == 'season':
        df['season'] = df['date'].map(get_season)
        df = df.groupby(['season', 'element'])['data_value'].mean().reset_index()
    else:
        return 'Rythm not found'
    
    if rythm != 'season':
        df['date'] = df['date'].astype(str)
    return df

def get_weather_data(id: str, start: str, end: str, rythm: str) -> pd.DataFrame:
    """gets the weather data from a given id
    
    Keyword arguments:
    id
    start
    end
    rythm
    Return: df with date, element and data_value
    """
    #start_time = time.time()
    df = get_data_from_id(id)
    #print("get_data_from_id --- %s seconds ---" % (time.time() - start_time))
    #start_time = time.time()
    df = filter_data(df, start, end)
    #print("filter_data --- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    df = calc_mean(df, rythm)
    #print("calc_mean --- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    df = df.pivot(index='date', columns='element', values='data_value').reset_index()
    #print("pivot --- %s seconds ---" % (time.time() - start_time))

    return df

if __name__ == '__main__':
    print(get_weather_data('USW00094728', '2020-01-01', '2021-12-31', 'season').to_json(orient="records"))