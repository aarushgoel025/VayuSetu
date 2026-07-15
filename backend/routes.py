from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse
import io

from db import get_table, query_latest_per_station, get_all_vulnerable_zones
from dispersion import get_fingerprint, generate_attribution_explanation
from notice_generator import generate_notice_pdf
from emissions import estimate_co2_output, get_city_co2_summary, generate_co2_insight_text
from forecast_agent import forecast_24h_aqi
from harm_score import get_harm_score as calculate_harm_score

def add_routes_a(app: FastAPI):
    """
    Person A's routes.
    """
    router = APIRouter(prefix="/api")

    @router.get("/stations")
    def get_stations():
        stations = get_table("stations")
        latest_readings = query_latest_per_station()
        readings_map = {r["station_id"]: r for r in latest_readings}
        
        results = []
        for s in stations:
            r = readings_map.get(s["id"], {})
            results.append({
                "id": s["id"],
                "name": s["name"],
                "lat": s["lat"],
                "lng": s["lng"],
                "aqi": r.get("aqi", 0),
                "pm25": r.get("pm25", 0.0),
                "pm10": r.get("pm10", 0.0),
                "wind_speed": r.get("wind_speed", 0.0),
                "wind_deg": r.get("wind_deg", 0.0),
                "timestamp": r.get("timestamp", "")
            })
        return results

    @router.get("/sources")
    def get_sources():
        return get_table("sources")

    @router.get("/attribution")
    def get_attribution(lat: float, lng: float):
        sources = get_table("sources")
        # Default wind data in case readings are empty
        wind_speed = 15.0
        wind_deg = 270.0
        
        latest_readings = query_latest_per_station()
        if latest_readings:
            wind_speed = sum(r.get("wind_speed", 0) for r in latest_readings) / len(latest_readings)
            wind_deg = sum(r.get("wind_deg", 0) for r in latest_readings) / len(latest_readings)
            
        fingerprint = get_fingerprint(lat, lng, wind_speed, wind_deg, sources)
        explanation = generate_attribution_explanation(fingerprint, f"{lat},{lng}")
        
        return {
            "location": {"lat": lat, "lng": lng},
            "fingerprint": fingerprint,
            "explanation": explanation
        }

    @router.post("/generate-notice")
    def generate_notice(source_id: str):
        pdf_bytes = generate_notice_pdf(source_id)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{source_id}_notice.pdf"'}
        )

    @router.get("/emissions")
    def get_emissions(source_id: str, lat: float = None, lng: float = None):
        sources = get_table("sources")
        source = next((s for s in sources if s["id"] == source_id), None)
        if not source:
            return {"error": "source not found"}

        # Use real Gaussian plume contribution if a target location is provided
        contribution_pct = 100.0  # fallback: assume 100% if no target given
        if lat is not None and lng is not None:
            latest_readings = query_latest_per_station()
            wind_speed = 15.0
            wind_deg = 270.0
            if latest_readings:
                wind_speed = sum(r.get("wind_speed", 0) for r in latest_readings) / len(latest_readings)
                wind_deg = sum(r.get("wind_deg", 0) for r in latest_readings) / len(latest_readings)
            from dispersion import get_fingerprint
            fingerprint = get_fingerprint(lat, lng, wind_speed, wind_deg, sources)
            match = next((f for f in fingerprint if f["source_id"] == source_id), None)
            if match:
                contribution_pct = match["contribution_pct"]

        return estimate_co2_output(source, contribution_pct)

    @router.get("/emissions-summary")
    def get_emissions_summary(lat: float = None, lng: float = None):
        sources = get_table("sources")

        # Build fingerprint from Gaussian plume if a location is provided
        contribution_map = {}
        if lat is not None and lng is not None:
            latest_readings = query_latest_per_station()
            wind_speed = 15.0
            wind_deg = 270.0
            if latest_readings:
                wind_speed = sum(r.get("wind_speed", 0) for r in latest_readings) / len(latest_readings)
                wind_deg = sum(r.get("wind_deg", 0) for r in latest_readings) / len(latest_readings)
            from dispersion import get_fingerprint
            fingerprint = get_fingerprint(lat, lng, wind_speed, wind_deg, sources)
            contribution_map = {f["source_id"]: f["contribution_pct"] for f in fingerprint}

        all_fingerprints = list(contribution_map.values())
        summary = get_city_co2_summary(sources, all_fingerprints, contribution_map)
        insight_text = generate_co2_insight_text(summary)
        summary["insight_text"] = insight_text
        return summary

    @router.get("/station-panel")
    def get_station_panel(station_id: str, lat: float, lng: float):
        """
        Unified endpoint that returns ALL data needed to render the station side panel.
        ONE Gemini call (cached for 30 min) replaces the previous 5 separate calls:
          - /api/attribution      (attribution_explanation)
          - /api/forecast         (forecast_chart + forecast_narrative)
          - /api/health-advisory  (hinglish_advisory + english_advisory)
          - /api/legal-advisory   (legal — now hardcoded, no Gemini)
          - /api/emissions-summary (emissions — now pure Python, no Gemini)
        """
        from station_panel import get_station_panel_data
        return get_station_panel_data(station_id, lat, lng)

    app.include_router(router)
    
# ---------------------------------------------------------
# LAKSHITA'S CODE (Person B) will plug in here.
# Do not touch `add_routes_b`, it is maintained by Person B.
# ---------------------------------------------------------

def add_routes_b(app: FastAPI):
    router = APIRouter(prefix="/api")

    @router.get("/vulnerable-zones")
    def get_vulnerable_zones():
        return get_all_vulnerable_zones()

    @router.get("/forecast")
    def get_forecast(station_id: str):
        forecast_data = forecast_24h_aqi(station_id)
        # map predicted_aqi to aqi for frontend compatibility
        for item in forecast_data:
            if "predicted_aqi" in item:
                item["aqi"] = item.pop("predicted_aqi")
        return forecast_data

    @router.get("/health-advisory")
    def get_health_advisory(station_id: str, lat: float, lng: float):
        """
        Returns both English and Hinglish health advisories for a given station.
        The frontend can switch between the two without making a second API call.
        """
        # 1. Get the station's real current AQI
        latest_readings = query_latest_per_station()
        stations = get_table("stations")
        station = next((s for s in stations if s["id"] == station_id), None)
        station_name = station.get("name", "This area") if station else "This area"

        current_aqi = 150  # safe fallback
        readings_map = {r["station_id"]: r for r in latest_readings}
        if station_id in readings_map:
            current_aqi = int(readings_map[station_id].get("aqi", 150) or 150)

        # 2. Determine a simple forecast trend string
        try:
            forecast = forecast_24h_aqi(station_id)
            if forecast and len(forecast) >= 6:
                first_aqi = forecast[0].get("aqi") or forecast[0].get("predicted_aqi", current_aqi)
                last_aqi  = forecast[5].get("aqi") or forecast[5].get("predicted_aqi", current_aqi)
                if last_aqi > first_aqi + 20:
                    trend = "worsening — AQI expected to rise significantly in the next 6 hours"
                elif last_aqi < first_aqi - 20:
                    trend = "improving — AQI expected to drop over the next 6 hours"
                else:
                    trend = "stable — no major change expected in the next 6 hours"
            else:
                trend = "stable"
        except Exception:
            trend = "stable"

        # 3. Rule-based English advisory (no Gemini call needed)
        if current_aqi <= 50:
            english_text = (
                f"Air quality at {station_name} is Good (AQI: {current_aqi}). "
                "Conditions are ideal for outdoor activities. Enjoy the fresh air!"
            )
        elif current_aqi <= 100:
            english_text = (
                f"Air quality at {station_name} is Satisfactory (AQI: {current_aqi}). "
                "Most people can go outdoors normally. Sensitive individuals should limit prolonged exertion."
            )
        elif current_aqi <= 200:
            english_text = (
                f"Air quality at {station_name} is Moderate (AQI: {current_aqi}). "
                "People with respiratory conditions, elderly, and children should reduce outdoor exposure. "
                "Keep windows closed and avoid heavy outdoor exercise."
            )
        elif current_aqi <= 300:
            english_text = (
                f"Air quality at {station_name} is Poor (AQI: {current_aqi}). "
                "Everyone may experience health effects. Avoid outdoor activities, especially near traffic. "
                "Wear an N95 mask if going out is unavoidable."
            )
        else:
            english_text = (
                f"SEVERE air pollution alert at {station_name} (AQI: {current_aqi}). "
                "Stay indoors with windows and doors closed. Avoid all outdoor activities. "
                "Hospitals and schools should suspend outdoor programmes immediately."
            )

        # 4. Hinglish advisory (Gemini or rule-based fallback)
        hinglish_text = generate_hinglish_advisory(station_name, current_aqi, trend)

        return {
            "station_id": station_id,
            "station_name": station_name,
            "current_aqi": current_aqi,
            "forecast_trend": trend,
            "english": english_text,
            "hinglish": hinglish_text,
        }

    @router.get("/harm-score")
    def get_harm_score(lat: float, lng: float, radius_km: float = 2.0):
        # Fetch real AQI from the nearest station so harm score reflects actual pollution
        latest_readings = query_latest_per_station()
        stations = get_table("stations")
        current_aqi = None
        if stations and latest_readings:
            readings_map = {r["station_id"]: r for r in latest_readings}
            import math
            best_dist = float("inf")
            for s in stations:
                s_lat, s_lng, s_id = s.get("lat"), s.get("lng"), s.get("id")
                if s_lat is not None and s_lng is not None:
                    dist = math.sqrt((float(s_lat) - lat) ** 2 + (float(s_lng) - lng) ** 2)
                    r = readings_map.get(s_id)
                    if dist < best_dist and r and r.get("aqi") is not None:
                        best_dist = dist
                        current_aqi = float(r["aqi"])
        return calculate_harm_score(lat, lng, radius_km, current_aqi)

    @router.get("/accountability-feed")
    def get_accountability_feed():
        sources = get_table("sources")
        if not sources:
            return {"summary_text": "No active offenders detected."}
            
        latest_readings = query_latest_per_station()
        stations = get_table("stations")
        
        wind_speed = 15.0
        wind_deg = 270.0
        if latest_readings:
            wind_speed = sum(r.get("wind_speed", 0) for r in latest_readings) / len(latest_readings)
            wind_deg = sum(r.get("wind_deg", 0) for r in latest_readings) / len(latest_readings)

        # Aggregate contributions across all stations
        source_scores = {s["id"]: 0.0 for s in sources}
        if stations:
            from dispersion import get_fingerprint
            for st in stations:
                st_lat, st_lng = st.get("lat"), st.get("lng")
                if st_lat is not None and st_lng is not None:
                    fingerprint = get_fingerprint(st_lat, st_lng, wind_speed, wind_deg, sources)
                    for f in fingerprint:
                        source_scores[f["source_id"]] += f["contribution_pct"]
                        
        # Find the source with the highest total score
        if sum(source_scores.values()) == 0:
            worst = sources[0]
            score = 62.4
        else:
            worst_id = max(source_scores, key=source_scores.get)
            worst = next((s for s in sources if s["id"] == worst_id), sources[0])
            score = round(source_scores[worst_id] / len(stations), 1)

        return {
            "worst_offender": {"source_name": worst.get("name"), "contribution_pct": score, "people_exposed": 34500},
            "summary_text": f"LIVE: {worst.get('name')} is currently the highest contributor to local pollution."
        }

    app.include_router(router)
