from fastapi import FastAPI
from typing import Optional
import os
import json
import uvicorn
import station_data 
import weather_data

app = FastAPI()

@app.get("/stations")
def get_stations(longitude: float, latitude: float, radius: float, start: int, end: int, selection: Optional[int] = None):

    df = station_data.get_stations(longitude, latitude, radius, start, end, selection)

    return json.loads(df.to_json(orient='records'))

@app.get("/reload_stations")
def reload_stations():
    station_data.load_stations()
    return "Stations reloaded"

@app.get("/data/{id}/{rythm}")
def get_data_of_year(id: str, rythm: str,start: str, end: str):

    df = weather_data.get_weather_data(id, start, end, rythm)

    return json.loads(df.to_json(orient='records'))

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)