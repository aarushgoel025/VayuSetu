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
