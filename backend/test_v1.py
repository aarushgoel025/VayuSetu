import os
from forecast_agent import forecast_24h_aqi, v1_pkg
from db import query_latest_per_station

print(f"V1 Package Loaded: {v1_pkg is not None}")

# Test 1: V1 model forecast (Anand Vihar is one of the 9 stations)
print("Testing Anand Vihar forecast (Should use V1 model)...")
av_forecast = forecast_24h_aqi("Anand Vihar, Delhi - DPCC")
print(f"AV Forecast len: {len(av_forecast)}, Sample: {av_forecast[0] if av_forecast else 'None'}")

# Test 2: Unknown station forecast (Should use Gemini / fallback)
print("Testing Unknown Station forecast...")
un_forecast = forecast_24h_aqi("Unknown Station 999")
print(f"Unknown Forecast len: {len(un_forecast)}, Sample: {un_forecast[0] if un_forecast else 'None'}")

print("Test complete.")
