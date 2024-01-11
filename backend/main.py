from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/stations")
def get_stations(longitude: float, latitude: float, radius: float, start: str, end: str, selection: Optional[int] = None):
    # Führen Sie Ihre Logik hier aus und geben Sie die Daten zurück
    return {"stations": [
        {"id": "1", "name": "Station 1", "longitude": 0.0, "latitude": 0.0},
    ]}

@app.get("/data_of_year/{id}")
def get_data_of_year(id: str):
    # Führen Sie Ihre Logik hier aus und geben Sie die Daten zurück
    return {"data": [
        {"year": "2020",
         "min": 0.0,
         "max": 0.0,
         }
        ]
    }

@app.get("/data_of_month/{id}")
def get_data_of_month(id: str):
    # Führen Sie Ihre Logik hier aus und geben Sie die Daten zurück
    return {"data": [
        {"month-year": "08-2020",
         "min": 0.0,
         "max": 0.0,
         }
        ]
    }

@app.get("/data_of_day/{id}")
def get_data_of_day(id: str):
    # Führen Sie Ihre Logik hier aus und geben Sie die Daten zurück
        return {"data": [
        {"day-month-year": "01-08-2020",
         "min": 0.0,
         "max": 0.0,
         }
        ]
    }

@app.get("/data_of_season/{id}")
def get_data_of_season(id: str):
    # Führen Sie Ihre Logik hier aus und geben Sie die Daten zurück
    return {"data": [
        {"season-year": "winter-2020",
         "min": 0.0,
         "max": 0.0,
         }
        ]
    }