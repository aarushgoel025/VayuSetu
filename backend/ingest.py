import time
from datetime import datetime, timezone
import requests
from config import AQICN_API_KEY, OPENWEATHER_API_KEY
from db import supabase

STATIONS = [
    {"id": "delhi_anand_vihar", "name": "Anand Vihar, Delhi", "lat": 28.6469, "lng": 77.3160, "city": "Delhi"},
    {"id": "delhi_ito", "name": "ITO, Delhi", "lat": 28.6286, "lng": 77.2415, "city": "Delhi"},
    {"id": "delhi_rks_puram", "name": "R.K. Puram, Delhi", "lat": 28.5638, "lng": 77.1869, "city": "Delhi"},
    {"id": "delhi_punjabi_bagh", "name": "Punjabi Bagh, Delhi", "lat": 28.6738, "lng": 77.1309, "city": "Delhi"},
    {"id": "noida_sector_125", "name": "Sector 125, Noida", "lat": 28.5447, "lng": 77.3230, "city": "Noida"},
    {"id": "gurugram_vikas_sadan", "name": "Vikas Sadan, Gurugram", "lat": 28.4503, "lng": 77.0253, "city": "Gurugram"},
]

def fetch_aqicn_data(lat, lng):
    url = f"https://api.waqi.info/feed/geo:{lat};{lng}/?token={AQICN_API_KEY}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                iaqi = data["data"]["iaqi"]
                return {
                    "aqi": data["data"].get("aqi", 0),
                    "pm25": iaqi.get("pm25", {}).get("v", 0.0),
                    "pm10": iaqi.get("pm10", {}).get("v", 0.0),
                }
    except Exception as e:
        print(f"AQICN fetch error: {e}")
    return None

def fetch_weather_data(lat, lng):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "wind_speed": data["wind"].get("speed", 0.0) * 3.6, # m/s to km/h
                "wind_deg": data["wind"].get("deg", 0.0)
            }
    except Exception as e:
        print(f"OpenWeather fetch error: {e}")
    return None

def ingest_job():
    if not supabase:
        print("Database not connected. Skipping ingestion.")
        return
        
    print(f"[{datetime.now(timezone.utc)}] Running ingest_job...")
    for st in STATIONS:
        try:
            aqi_data = fetch_aqicn_data(st["lat"], st["lng"])
            weather_data = fetch_weather_data(st["lat"], st["lng"])
            
            if aqi_data and weather_data:
                row = {
                    "station_id": st["id"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "aqi": aqi_data["aqi"],
                    "pm25": float(aqi_data["pm25"]),
                    "pm10": float(aqi_data["pm10"]),
                    "wind_speed": float(weather_data["wind_speed"]),
                    "wind_deg": float(weather_data["wind_deg"])
                }
                supabase.table("readings").insert(row).execute()
                print(f"  -> Ingested data for {st['id']}")
            else:
                print(f"  -> Failed to fetch all data for {st['id']}")
        except Exception as e:
            print(f"  -> Error ingesting for {st['id']}: {e}")
