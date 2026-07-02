import json
import datetime
import math
from google import genai
from config import GEMINI_API_KEY
from db import get_table

# Initialize Gemini Client if key is available
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def forecast_24h_aqi(station_id: str, historical_readings: list[dict] = None) -> list[dict]:
    """
    Predicts the next 24-hour AQI trend for a station from historical readings.
    Uses Gemini 2.5 Flash (temperature=0.3) for AI forecasting.
    Falls back to a linear trend extrapolation if the API is unavailable or parse fails.
    """
    # 1. Reuse db.py if historical readings are not provided
    if not historical_readings:
        try:
            all_readings = get_table("readings")
            historical_readings = [r for r in all_readings if r.get("station_id") == station_id]
        except Exception as e:
            print(f"Error querying database: {e}")
            historical_readings = []

    # Sort readings chronologically
    def parse_time(t_str):
        try:
            return datetime.datetime.fromisoformat(t_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.datetime.now()

    historical_readings = sorted(
        historical_readings,
        key=lambda x: parse_time(x.get("timestamp", "")) if x.get("timestamp") else datetime.datetime.min
    )

    # Determine reference/latest time
    if historical_readings:
        latest_reading = historical_readings[-1]
        latest_time_str = latest_reading.get("timestamp", "")
        latest_time = parse_time(latest_time_str)
    else:
        latest_time = datetime.datetime.now()

    # 2. Try Gemini 2.5 Flash Forecasting
    if client and historical_readings:
        # Prepare historical data for prompt
        history_summary = []
        for r in historical_readings[-168:]:  # last 7 days (168 hours) max
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

            # Strip any residual markdown blocks just in case
            response_text = response.text.strip()
            if response_text.startswith("```"):
                # strip opening tag
                lines = response_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                response_text = "\n".join(lines).strip()

            forecast_data = json.loads(response_text)

            # Validate structural shape: List of 24 items with correct fields
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
                    return validated_forecast

            print("Gemini response validation failed. Falling back to linear trend.")
        except Exception as e:
            print(f"Error forecasting with Gemini: {e}. Falling back to linear trend.")

    # 3. Fallback: Linear Trend Extrapolation
    fallback_forecast = []
    
    # Calculate simple linear regression if we have at least 2 data points
    slope = 0.0
    intercept = 150.0 # Default starting AQI if no data
    
    if len(historical_readings) >= 2:
        # Convert timestamps to float hours relative to first reading
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
        
    # Generate 24 hours of predictions
    last_record_time = latest_time
    if historical_readings:
        # Find reference hours from start
        first_time = parse_time(historical_readings[0].get("timestamp", ""))
        hours_offset = (last_record_time - first_time).total_seconds() / 3600.0
    else:
        hours_offset = 0.0

    # Diurnal cycle amplitude to make fallback look natural (peaks at night/morning)
    diurnal_amp = 15.0

    for i in range(1, 25):
        future_hour = last_record_time + datetime.timedelta(hours=i)
        future_hours_relative = hours_offset + i
        
        # Linear trend component
        predicted = intercept + slope * future_hours_relative
        
        # Diurnal fluctuation (using sine wave based on hour of day)
        # Peak around 8 AM (hour 8) and low at 4 PM (hour 16)
        diurnal_effect = diurnal_amp * math.sin((future_hour.hour - 2) * math.pi / 12)
        predicted += diurnal_effect
        
        final_aqi = max(0, min(500, int(round(predicted))))
        fallback_forecast.append({
            "hour": future_hour.strftime("%Y-%m-%dT%H:00:00"),
            "predicted_aqi": final_aqi
        })
        
    return fallback_forecast


def generate_hinglish_advisory(location_name: str, current_aqi: int, forecast_trend: str) -> str:
    """
    Generates a 2-3 sentence Hinglish health advisory using Gemini 2.5 Flash (temperature=0.6).
    Falls back to rule-based advice on API failure or configuration omission.
    """
    if client:
        prompt = f"""
        Generate a warm, friendly, and practical 2-3 sentence health advisory in Hinglish (Hindi written in the Roman/English script mixed with English words).
        Target Location: {location_name}
        Current AQI: {current_aqi}
        Forecast Trend: {forecast_trend}

        Example Hinglish style: "Aaj Delhi ka air quality level kafi unsafe hai. Please elderly log and children indoor rahein aur zaroori hone par hi N95 mask pehan kar bahar niklein."

        Ensure the advisory matches the current AQI level and the future trend. Do not use Devanagari script.
        """
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.6
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating Hinglish advisory with Gemini: {e}")

    # Fallback to rule-based Hinglish advisory
    if current_aqi > 300:
        return f"{location_name} mein AQI level bahot hi kharab ({current_aqi}) hai. Sabhi log indoor rahein aur bahar nikalte waqt mask zaroor pehnein."
    elif current_aqi > 150:
        return f"Aaj {location_name} ki hawa kafi unhealthy hai. Bacho aur buzurgon ko outdoor activities se bchna chahiye, aur ghar ke darwaze-khidkiyan band rakhein."
    elif current_aqi > 100:
        return f"{location_name} mein air quality moderate hai, par sensitive logo ko breathing issue ho sakta hai. Bahar exercise thoda dhyan se karein."
    else:
        return f"Good news! Aaj {location_name} ki air quality kafi acchi hai. Outdoor walk aur baaki activities ke liye badhiya din hai!"


