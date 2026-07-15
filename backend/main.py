from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import io
import csv
import httpx

from ingest import ingest_job
from routes import add_routes_a
from violation_tracker import add_violation_tracker_routes
from legal_advisory import add_legal_advisory_routes
from config import FIRMS_KEY

# LAKSHITA'S ROUTER IMPORTS (Person B)
try:
    from routes import add_routes_b
except ImportError:
    def add_routes_b(app: FastAPI):
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    from datetime import datetime
    scheduler.add_job(ingest_job, 'interval', minutes=15, next_run_time=datetime.now())
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)

app = FastAPI(title="VayuSetu Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to VayuSetu API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ─────────────────────────────────────────────────────────────
# NASA FIRMS Satellite Thermal Hotspot Endpoint
# Fetches real satellite data from VIIRS SNPP NRT for NCR region
# ─────────────────────────────────────────────────────────────
def _parse_firms_csv(raw_text: str) -> list[dict]:
    """Parse NASA FIRMS CSV response into clean JSON list."""
    hotspots = []
    try:
        reader = csv.DictReader(io.StringIO(raw_text))
        for row in reader:
            try:
                lat = float(row.get("latitude") or row.get("lat", 0))
                lng = float(row.get("longitude") or row.get("lon", 0) or row.get("lng", 0))
                brightness = float(row.get("bright_ti4") or row.get("brightness", 0))
                confidence = row.get("confidence", "nominal").strip().lower()

                # Skip rows outside NCR bounding box
                if not (27.5 <= lat <= 29.5 and 76.0 <= lng <= 78.5):
                    continue

                # Map confidence string to numeric level
                conf_map = {"low": 1, "nominal": 2, "high": 3, "l": 1, "n": 2, "h": 3}
                conf_level = conf_map.get(confidence, 2)

                hotspots.append({
                    "lat": round(lat, 5),
                    "lng": round(lng, 5),
                    "brightness": round(brightness, 1),
                    "confidence": confidence,
                    "confidence_level": conf_level,   # 1=low, 2=nominal, 3=high
                    "acq_date": row.get("acq_date", ""),
                    "acq_time": row.get("acq_time", ""),
                    "satellite": row.get("satellite", "VIIRS"),
                    "frp": float(row.get("frp", 0) or 0),   # Fire Radiative Power (MW)
                })
            except (ValueError, KeyError):
                continue
    except Exception as e:
        print(f"[FIRMS] CSV parse error: {e}")
    return hotspots


@app.get("/api/satellite-hotspots")
async def get_satellite_hotspots():
    """
    Returns real-time satellite thermal hotspot detections from NASA FIRMS
    (VIIRS SNPP NRT) for the NCR region (last 24 hours).
    These are distinct from ground AQI sensors — they show industrial heat
    sources detected from space.
    """
    if not FIRMS_KEY:
        return {"hotspots": [], "source": "NASA FIRMS", "error": "FIRMS_KEY not configured"}

    # NCR bounding box: lat 27.5–29.5, lng 76.0–78.5
    firms_url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv"
        f"/{FIRMS_KEY}/VIIRS_SNPP_NRT/76.0,27.5,78.5,29.5/1"
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(firms_url)
            resp.raise_for_status()
            hotspots = _parse_firms_csv(resp.text)
    except Exception as e:
        print(f"[FIRMS] API error: {e}")
        hotspots = []

    return {
        "hotspots": hotspots,
        "count": len(hotspots),
        "source": "NASA FIRMS VIIRS SNPP NRT",
        "region": "NCR (76.0-78.5E, 27.5-29.5N)",
    }


# Add Routes
add_routes_a(app)
add_routes_b(app)
add_violation_tracker_routes(app)
add_legal_advisory_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
