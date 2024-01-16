from fastapi import FastAPI
from typing import Optional
from datetime import datetime
import json
import uvicorn
import station_data 
import weather_data
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stations")
def get_stations(latitude: float, longitude: float, radius: float, start: Optional[int] = None, end: Optional[int] = None, selection: Optional[int] = None):

    df = station_data.get_stations(latitude, longitude, radius, start, end, selection)

    return json.loads(df.to_json(orient='records'))

@app.get("/reload_stations")
def reload_stations():
    station_data.load_stations()
    return "Stations reloaded"

@app.get("/data/{id}/{rythm}")
def get_data_of_year(id: str, rythm: str,start: str, end: str):

    df = weather_data.get_weather_data(id, start, end, rythm)

    return json.loads(df.to_json(orient='records'))

@app.get("/stations/{name}")
def get_station_by_name(name: str):

    df = station_data.get_station_by_name(name)

    return json.loads(df.to_json(orient='records'))

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)