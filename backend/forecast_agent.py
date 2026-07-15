import json
import datetime
import math
import time
import os
import pickle
import numpy as np
import pandas as pd
from google import genai
from config import GEMINI_API_KEY
from db import get_table, get_readings_for_station

# Initialize Gemini Client if key is available
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

# ── Load Local V1 Model ────────────────────────────────────────────────────
V1_MODEL_PATH = r"C:\Users\Ankit\Desktop\AQI data Delhi 2015-23\aqi_ensemble.pkl"
v1_pkg = None
V1_STATIONS = []

try:
    if os.path.exists(V1_MODEL_PATH):
        with open(V1_MODEL_PATH, "rb") as f:
            v1_pkg = pickle.load(f)
            V1_STATIONS = list(v1_pkg["label_encoder"].classes_)
            print(f"[forecast_agent] Loaded V1 Model with {len(V1_STATIONS)} stations.")
except Exception as e:
    print(f"[forecast_agent] Error loading V1 Model: {e}")

# ── TTL Cache for forecast data ────────────────────────────────────────────
_FORECAST_CACHE: dict = {}
FORECAST_CACHE_TTL = 1800  # 30 minutes


def _forecast_cache_get(station_id: str):
    entry = _FORECAST_CACHE.get(station_id)
    if entry and (time.time() - entry["ts"]) < FORECAST_CACHE_TTL:
        return entry["data"]
    return None


def _forecast_cache_set(station_id: str, data):
    _FORECAST_CACHE[station_id] = {"ts": time.time(), "data": data}


def _predict_v1(X):
    return (v1_pkg["weights"]["w_lr"] * v1_pkg["models"]["lr"].predict(X) +
            v1_pkg["weights"]["w_rf"] * v1_pkg["models"]["rf"].predict(X) +
            v1_pkg["weights"]["w_gb"] * v1_pkg["models"]["gb"].predict(X))

def get_season(month):
    if month in [12, 1, 2]:   return 0
    if month in [3, 4, 5]:    return 1
    if month in [6, 7, 8, 9]: return 2
    return 3

def forecast_24h_aqi(station_id: str, historical_readings: list[dict] = None) -> list[dict]:
    """
    Predicts the next 24-hour AQI trend for a station from historical readings.
    Uses the blazing fast V1 Local Ensemble Model if the station is known.
    Falls back to Gemini 2.5 Flash for unknown stations (or if data is insufficient).
    """
    cached = _forecast_cache_get(station_id)
    if cached is not None:
        return cached

    if not historical_readings:
        try:
            historical_readings = get_readings_for_station(station_id, limit=96)
        except Exception:
            historical_readings = []

    def parse_time(t_str):
        try:
            return datetime.datetime.fromisoformat(t_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return datetime.datetime.now()

    historical_readings = sorted(
        historical_readings,
        key=lambda x: parse_time(x.get("timestamp", "")) if x.get("timestamp") else datetime.datetime.min
    )

    if historical_readings:
        latest_time = parse_time(historical_readings[-1].get("timestamp", ""))
    else:
        latest_time = datetime.datetime.now()

    # ── STRATEGY 1: Use Local V1 Model if applicable ───────────────────────
    if v1_pkg is not None and station_id in V1_STATIONS and len(historical_readings) >= 48:
        try:
            # We need the last 48 hours to compute lag_48 and rolling_24
            hist_aqi = [float(r.get("aqi", 150)) for r in historical_readings]
            
            predictions = []
            station_enc = v1_pkg["label_encoder"].transform([station_id])[0]
            
            # Recursive forecasting loop for 24 hours
            current_history = hist_aqi.copy()
            current_time = latest_time
            
            for i in range(1, 25):
                future_time = current_time + datetime.timedelta(hours=1)
                
                # Build features from the tail of current_history
                # ['hour', 'hour_sin', 'hour_cos', 'month', 'month_sin', 'month_cos', 
                #  'day_of_week', 'is_weekend', 'season', 'lag_1', 'lag_2', 'lag_3', 
                #  'lag_6', 'lag_24', 'lag_48', 'rolling_mean_3', 'rolling_mean_6', 
                #  'rolling_mean_24', 'rolling_std_3', 'station_enc']
                
                h = future_time.hour
                m = future_time.month
                dow = future_time.weekday()
                
                lag_1 = current_history[-1]
                lag_2 = current_history[-2]
                lag_3 = current_history[-3]
                lag_6 = current_history[-6]
                lag_24 = current_history[-24]
                lag_48 = current_history[-48]
                
                rm_3 = np.mean(current_history[-3:])
                rm_6 = np.mean(current_history[-6:])
                rm_24 = np.mean(current_history[-24:])
                rs_3 = np.std(current_history[-3:]) if len(current_history[-3:]) > 1 else 0.0
                
                features = {
                    "hour": h,
                    "hour_sin": math.sin(2 * math.pi * h / 24),
                    "hour_cos": math.cos(2 * math.pi * h / 24),
                    "month": m,
                    "month_sin": math.sin(2 * math.pi * m / 12),
                    "month_cos": math.cos(2 * math.pi * m / 12),
                    "day_of_week": dow,
                    "is_weekend": 1 if dow >= 5 else 0,
                    "season": get_season(m),
                    "lag_1": lag_1, "lag_2": lag_2, "lag_3": lag_3,
                    "lag_6": lag_6, "lag_24": lag_24, "lag_48": lag_48,
                    "rolling_mean_3": rm_3, "rolling_mean_6": rm_6,
                    "rolling_mean_24": rm_24, "rolling_std_3": rs_3,
                    "station_enc": station_enc
                }
                
                # Ensure feature order matches the model
                X = pd.DataFrame([features])[v1_pkg["feature_cols"]]
                
                pred_aqi = float(_predict_v1(X)[0])
                pred_aqi = max(0, min(500, int(round(pred_aqi))))
                
                predictions.append({
                    "hour": future_time.strftime("%Y-%m-%dT%H:00:00"),
                    "predicted_aqi": pred_aqi
                })
                
                # Append to history for the next iteration step
                current_history.append(pred_aqi)
                current_time = future_time
                
            _forecast_cache_set(station_id, predictions)
            return predictions
            
        except Exception as e:
            print(f"[forecast_agent] V1 Local Model failed: {e}. Falling back to Gemini.")

    # ── STRATEGY 2: Fallback to Gemini 2.5 Flash for Unknown Stations ───────
    if client and historical_readings:
        history_summary = []
        for r in historical_readings[-168:]:
            history_summary.append({
                "timestamp": r.get("timestamp"),
                "aqi": r.get("aqi")
            })

        prompt = f"""
        You are an environmental data scientist forecasting air quality for station {station_id}.
        Given the following historical AQI readings (up to last 7 days):
        {json.dumps(history_summary)}

        Predict the AQI for the next 24 hours, starting exactly from the hour after the last record.
        The last record timestamp is: {history_summary[-1]['timestamp'] if history_summary else latest_time.isoformat()}

        Return a strict JSON array containing exactly 24 elements with the keys "hour" and "predicted_aqi":
        [
          {{"hour": "YYYY-MM-DDTHH:00:00", "predicted_aqi": 245}},
          ...
        ]
        
        Rules:
        - Output MUST be raw JSON. Do not include markdown code block fences (```json or ```).
        - Predict realistic AQI trends based on the historical pattern (daily peaks, diurnal cycle, trend).
        - AQI values must be integers between 0 and 500.
        """
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )

            response_text = response.text.strip()
            if response_text.startswith("```"):
                lines = response_text.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines[-1].startswith("```"): lines = lines[:-1]
                response_text = "\n".join(lines).strip()

            forecast_data = json.loads(response_text)

            if isinstance(forecast_data, list) and len(forecast_data) == 24:
                validated_forecast = []
                for item in forecast_data:
                    hour_val = item.get("hour")
                    aqi_val = item.get("predicted_aqi")
                    if hour_val and aqi_val is not None:
                        validated_forecast.append({
                            "hour": str(hour_val),
                            "predicted_aqi": max(0, min(500, int(aqi_val)))
                        })
                if len(validated_forecast) == 24:
                    _forecast_cache_set(station_id, validated_forecast)
                    return validated_forecast

            print("Gemini response validation failed. Falling back to linear trend.")
        except Exception as e:
            print(f"Error forecasting with Gemini: {e}. Falling back to linear trend.")

    # ── STRATEGY 3: Final Fallback to Linear Trend ─────────────────────────
    fallback_forecast = []
    slope = 0.0
    intercept = 150.0 
    
    if len(historical_readings) >= 2:
        first_time = parse_time(historical_readings[0].get("timestamp", ""))
        x_vals = []
        y_vals = []
        for r in historical_readings:
            t = parse_time(r.get("timestamp", ""))
            hours_diff = (t - first_time).total_seconds() / 3600.0
            x_vals.append(hours_diff)
            y_vals.append(float(r.get("aqi", 150)))
            
        n = len(x_vals)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xx = sum(x ** 2 for x in x_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        
        denom = (n * sum_xx - sum_x ** 2)
        if denom != 0:
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0.0
            intercept = y_vals[-1]
    elif len(historical_readings) == 1:
        slope = 0.0
        intercept = float(historical_readings[0].get("aqi", 150))
        
    current_aqi = float(historical_readings[-1].get("aqi", 150)) if historical_readings else 150.0
    diurnal_amp = 15.0

    for i in range(1, 25):
        future_hour = latest_time + datetime.timedelta(hours=i)
        predicted = current_aqi + (slope * i)
        diurnal_effect = diurnal_amp * math.sin((future_hour.hour - 2) * math.pi / 12)
        predicted += diurnal_effect
        final_aqi = max(0, min(500, int(round(predicted))))
        fallback_forecast.append({
            "hour": future_hour.strftime("%Y-%m-%dT%H:00:00"),
            "predicted_aqi": final_aqi
        })

    _forecast_cache_set(station_id, fallback_forecast)
    return fallback_forecast
