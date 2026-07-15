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
    {"id": "delhi_dwarka_sec8", "name": "Sector 8, Dwarka", "lat": 28.5710, "lng": 77.0719, "city": "Delhi"},
    {"id": "delhi_okhla_ph2", "name": "Okhla Phase 2, Delhi", "lat": 28.5307, "lng": 77.2730, "city": "Delhi"},
    {"id": "delhi_bawana", "name": "Bawana, Delhi", "lat": 28.7944, "lng": 77.0543, "city": "Delhi"},
    {"id": "delhi_rohini", "name": "Rohini, Delhi", "lat": 28.7299, "lng": 77.1066, "city": "Delhi"},
    {"id": "delhi_igi_airport", "name": "IGI Airport (T3), Delhi", "lat": 28.5562, "lng": 77.1000, "city": "Delhi"},
    {"id": "faridabad_sec11", "name": "Sector 11, Faridabad", "lat": 28.3800, "lng": 77.3100, "city": "Faridabad"},
    {"id": "ghaziabad_indirapuram", "name": "Indirapuram, Ghaziabad", "lat": 28.6415, "lng": 77.3714, "city": "Ghaziabad"},
    {"id": "greater_noida_kp5", "name": "Knowledge Park V, Greater Noida", "lat": 28.5900, "lng": 77.4600, "city": "Greater Noida"},
    {"id": "gurugram_sec51", "name": "Sector 51, Gurugram", "lat": 28.4310, "lng": 77.0680, "city": "Gurugram"},
]

def fetch_aqicn_data(lat, lng):
    url = f"https://api.waqi.info/feed/geo:{lat};{lng}/?token={AQICN_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                iaqi = data["data"]["iaqi"]
                raw_aqi = data["data"].get("aqi", 0)
                pm25_aqi = iaqi.get("pm25", {}).get("v", 0.0)
                pm10_aqi = iaqi.get("pm10", {}).get("v", 0.0)
                
                # Sanity check: If PM10 sensor glitches causing AQI > 500, fallback to PM2.5 AQI
                if raw_aqi > 500 and 0 < pm25_aqi < 400:
                    final_aqi = pm25_aqi
                else:
                    final_aqi = min(500, raw_aqi)

                return {
                    "aqi": final_aqi,
                    "pm25": pm25_aqi,
                    "pm10": pm10_aqi,
                }
    except Exception as e:
        print(f"AQICN fetch error: {e}")
    return None

def fetch_weather_data(lat, lng):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
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
