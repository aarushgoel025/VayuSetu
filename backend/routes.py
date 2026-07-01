from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from db import get_table, query_latest_per_station
from dispersion import get_fingerprint, generate_attribution_explanation
from notice_generator import generate_notice_pdf
from emissions import estimate_co2_output, get_city_co2_summary, generate_co2_insight_text

class NoticeRequest(BaseModel):
    source_id: str

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
    def generate_notice(payload: NoticeRequest):
        pdf_bytes = generate_notice_pdf(payload.source_id)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{payload.source_id}_notice.pdf"'}
        )

    @router.get("/emissions")
    def get_emissions(source_id: str):
        sources = get_table("sources")
        source = next((s for s in sources if s["id"] == source_id), None)
        if not source:
            return {"error": "source not found"}
        
        # mock contribution for this source
        return estimate_co2_output(source, 100.0)

    @router.get("/emissions-summary")
    def get_emissions_summary():
        sources = get_table("sources")
        summary = get_city_co2_summary(sources, [])
        insight_text = generate_co2_insight_text(summary)
        summary["insight_text"] = insight_text
        return summary

    app.include_router(router)
    
# ---------------------------------------------------------
# LAKSHITA'S CODE (Person B) will plug in here.
# Do not touch `add_routes_b`, it is maintained by Person B.
# ---------------------------------------------------------
