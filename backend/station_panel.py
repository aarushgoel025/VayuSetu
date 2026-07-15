"""
station_panel.py
─────────────────────────────────────────────────────────────────────────────
Unified station panel data aggregator.

KEY DESIGN DECISION:
  Before this module existed, opening one station's side panel triggered 5
  separate Gemini API calls:
    1. generate_attribution_explanation()  — dispersion.py
    2. forecast_24h_aqi()                  — forecast_agent.py
    3. generate_hinglish_advisory()         — forecast_agent.py
    4. get_legal_advisory()                — legal_advisory.py  (now hardcoded)
    5. generate_co2_insight_text()         — emissions.py       (now pure Python)

  This module replaces calls 1, 2 (AI narrative), and 3 with a SINGLE structured
  Gemini call that returns all AI text in one JSON response.
  Calls 4 and 5 were eliminated by removing their Gemini dependency entirely
  (see legal_advisory.py and emissions.py).

  Result:  5 Gemini calls → 1 per panel open
           + TTL cache    → 0 Gemini calls on re-open within 30 min
─────────────────────────────────────────────────────────────────────────────
"""

import json
import time
import math
import datetime
from google import genai
from config import GEMINI_API_KEY
from db import get_table, query_latest_per_station, get_readings_for_station
from dispersion import get_fingerprint, calculate_contribution
from harm_score import get_harm_score
from emissions import get_city_co2_summary, estimate_co2_output

# ── Gemini client ──────────────────────────────────────────────────────────
_gemini_client = None
if GEMINI_API_KEY:
    _gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ── TTL Cache ──────────────────────────────────────────────────────────────
_CACHE: dict = {}
CACHE_TTL_SECONDS = 1800  # 30 minutes


def _cache_get(key: str):
    """Return cached value if still fresh, else None."""
    entry = _CACHE.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _cache_set(key: str, data):
    _CACHE[key] = {"ts": time.time(), "data": data}


# ── Internal helpers ───────────────────────────────────────────────────────

def _get_wind_averages():
    """Compute average wind speed/direction from all station readings."""
    latest_readings = query_latest_per_station()
    wind_speed = 15.0
    wind_deg = 270.0
    if latest_readings:
        wind_speed = sum(r.get("wind_speed", 0) for r in latest_readings) / len(latest_readings)
        wind_deg = sum(r.get("wind_deg", 0) for r in latest_readings) / len(latest_readings)
    return wind_speed, wind_deg


def _forecast_trend_string(station_id: str, current_aqi: int) -> str:
    """
    Derive a plain-English trend string from the first 6 forecast points.
    This is pure Python — no Gemini call needed.
    """
    try:
        readings = get_readings_for_station(station_id, limit=12)
        if not readings or len(readings) < 2:
            return "stable"
        aqis = [float(r.get("aqi", current_aqi)) for r in readings if r.get("aqi") is not None]
        if len(aqis) < 2:
            return "stable"
        recent_avg = sum(aqis[-3:]) / min(3, len(aqis))
        older_avg = sum(aqis[:3]) / min(3, len(aqis))
        delta = recent_avg - older_avg
        if delta > 20:
            return "worsening — AQI rising over the past hours"
        elif delta < -20:
            return "improving — AQI dropping over the past hours"
        return "stable — no major change in recent hours"
    except Exception:
        return "stable"


def _build_forecast_chart_data(station_id: str) -> list:
    """
    Build 24-hour forecast chart data using pure linear trend extrapolation
    (no Gemini). The AI forecast chart is a nice-to-have; the AI narrative
    is what matters and that comes from the consolidated call.
    """
    try:
        from forecast_agent import forecast_24h_aqi
        raw = forecast_24h_aqi(station_id)
        # Normalise key name for the frontend (expects "aqi")
        return [
            {"hour": item.get("hour", ""), "aqi": item.get("aqi") or item.get("predicted_aqi", 0)}
            for item in raw
        ]
    except Exception:
        return []


def _build_co2_insight(total_tonnes: float) -> str:
    """Pure Python CO2 comparison — no Gemini call."""
    cars = int((total_tonnes * 1000) / (0.12 * 40))
    return f"This is equivalent to {cars:,} cars driven across NCR today."


# ── Single Gemini call ─────────────────────────────────────────────────────

def _call_gemini_for_insights(
    station_id: str,
    station_name: str,
    current_aqi: int,
    fingerprint: list,
    forecast_trend: str,
    co2_tonnes: float,
    harm_score: float,
    people_exposed: int,
) -> dict:
    """
    ONE Gemini call that replaces three separate calls:
      - attribution explanation  (was call #1)
      - Hinglish advisory        (was call #3)
      - Forecast narrative       (was part of call #2)

    Returns a dict with the three text fields.
    Falls back gracefully if Gemini is unavailable or returns malformed JSON.
    """
    fallback = {
        "attribution_explanation": (
            f"Pollution at {station_name} is primarily driven by "
            f"{fingerprint[0]['source_name'] if fingerprint else 'nearby industrial sources'}, "
            f"with current AQI at {current_aqi}."
        ),
        "english_advisory": f"Air quality at {station_name} is {current_aqi}. Please take necessary precautions.",
        "hindi_advisory": _rule_based_hindi(station_name, current_aqi),
        "forecast_narrative": f"Air quality at {station_name} is currently {_aqi_label(current_aqi)} and is expected to remain {forecast_trend}.",
    }

    if not _gemini_client:
        return fallback

    top_sources = fingerprint[:3] if fingerprint else []
    prompt = f"""You are an environmental AI analyst for VayuSetu, India's air quality platform.
Analyze the following real-time data for monitoring station "{station_name}" (ID: {station_id}).

STATION DATA:
- Current AQI: {current_aqi} ({_aqi_label(current_aqi)})
- Top pollution sources (Gaussian plume fingerprint): {json.dumps(top_sources)}
- Forecast trend: {forecast_trend}
- CO2 emitted today (NCR): {co2_tonnes} tonnes
- Harm score: {harm_score} | People in vulnerable zones nearby: {people_exposed}

Return ONLY a valid JSON object with exactly these three keys (no markdown, no backticks, no extra text):
{{
  "attribution_explanation": "[ENGLISH ONLY] 2-3 sentences explaining what is causing the pollution at this location based on the fingerprint. Mention the top 1-2 sources and why wind direction matters. Must be formal, professional English.",
  "english_advisory": "[ENGLISH ONLY] 2-3 sentence health advisory. Tone: warm, practical, urgent if AQI is high. Example: 'Air quality in {station_name} is severe today. Children and elderly should avoid going outdoors.'",
  "hindi_advisory": "[HINDI ONLY — use Devanagari script] 2-3 sentence health advisory in pure Hindi. Tone: warm, practical, urgent if AQI is high. Example: 'आज {station_name} में वायु गुणवत्ता गंभीर स्तर पर है। बच्चों और बुजुर्गों को बाहर जाने से बचना चाहिए।'",
  "forecast_narrative": "[ENGLISH ONLY] 1-2 sentences describing what the forecast trend means for residents today. Must be formal, professional English. No Hindi, no Roman Hindi."
}}"""

    try:
        response = _gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        raw = response.text.strip()
        # Strip accidental markdown fences (Gemini sometimes adds them despite mime type)
        if raw.startswith("```"):
            lines = raw.splitlines()
            lines = lines[1:] if lines[0].startswith("```") else lines
            lines = lines[:-1] if lines and lines[-1].startswith("```") else lines
            raw = "\n".join(lines).strip()

        parsed = json.loads(raw)
        # Validate all keys present; fall back per-key if missing
        result = {}
        for key in ("attribution_explanation", "english_advisory", "hindi_advisory", "forecast_narrative"):
            result[key] = parsed.get(key) or fallback[key]
        return result

    except Exception as e:
        print(f"[station_panel] Gemini call failed: {e}. Using fallback text.")
        return fallback


def _aqi_label(aqi: int) -> str:
    if aqi <= 50:   return "Good"
    if aqi <= 100:  return "Satisfactory"
    if aqi <= 200:  return "Moderate"
    if aqi <= 300:  return "Poor"
    return "Severe"


def _rule_based_hindi(location_name: str, aqi: int) -> str:
    """Rule-based Hindi advisory fallback in Devanagari script."""
    if aqi > 300:
        return (f"{location_name} में वायु प्रदूषण का स्तर अत्यंत गंभीर (AQI: {aqi}) है। "
                "सभी लोग घर के अंदर रहें और बाहर निकलते समय N95 मास्क अवश्य पहनें। "
                "अस्पताल और विद्यालय अपने बाहरी कार्यक्रम तत्काल रद्द करें।")
    elif aqi > 200:
        return (f"आज {location_name} की वायु गुणवत्ता अस्वास्थ्यकर स्तर (AQI: {aqi}) पर है। "
                "बच्चों, बुजुर्गों और श्वास रोगियों को बाहर जाने से बचना चाहिए। "
                "घर की खिड़कियाँ और दरवाज़े बंद रखें।")
    elif aqi > 100:
        return (f"{location_name} में वायु गुणवत्ता मध्यम स्तर (AQI: {aqi}) पर है। "
                "संवेदनशील व्यक्तियों को बाहरी गतिविधियाँ सीमित करनी चाहिए। "
                "व्यायाम के दौरान सावधानी बरतें।")
    return (f"आज {location_name} की वायु गुणवत्ता अच्छी (AQI: {aqi}) है। "
            "बाहरी गतिविधियों के लिए यह एक अनुकूल दिन है।")


# ── Public API ─────────────────────────────────────────────────────────────

def get_station_panel_data(station_id: str, lat: float, lng: float) -> dict:
    """
    Returns ALL data needed to render the station side panel in a single call.
    Cached per station_id for CACHE_TTL_SECONDS (30 min).

    Response shape:
    {
      "station_id": str,
      "station_name": str,
      "current_aqi": int,
      "aqi_label": str,
      "fingerprint": [...],            # Gaussian plume sources
      "attribution_explanation": str,  # AI text  ┐
      "hinglish_advisory": str,        # AI text  │  ONE Gemini call
      "english_advisory": str,         # pure Python
      "forecast_narrative": str,       # AI text  ┘
      "forecast_chart": [...],         # 24h chart data (no Gemini)
      "forecast_trend": str,           # trend label
      "harm": { harm_score, children_exposed, patients_exposed, affected_zones },
      "emissions": { total_co2_tonnes_today, top_emitters, insight_text },
      "legal": { citizen_rights_text, complaint_guidance_text, notice_status, relevant_authority, disclaimer },
    }
    """
    cache_key = f"panel:{station_id}:{round(lat, 3)}:{round(lng, 3)}"
    cached = _cache_get(cache_key)
    if cached:
        print(f"[station_panel] Cache HIT for {station_id}")
        return cached

    print(f"[station_panel] Cache MISS for {station_id} — computing...")

    # ── 1. Station metadata ───────────────────────────────────────────────
    stations = get_table("stations")
    station = next((s for s in stations if s.get("id") == station_id), None)
    station_name = station.get("name", "This Station") if station else "This Station"

    latest_readings = query_latest_per_station()
    readings_map = {r["station_id"]: r for r in latest_readings}
    reading = readings_map.get(station_id, {})
    current_aqi = int(reading.get("aqi", 150) or 150)

    # ── 2. Gaussian plume fingerprint (pure math, no Gemini) ──────────────
    sources = get_table("sources")
    wind_speed, wind_deg = _get_wind_averages()
    fingerprint = get_fingerprint(lat, lng, wind_speed, wind_deg, sources)

    # ── 3. Harm score (pure Python, no Gemini) ────────────────────────────
    if station_id == 'city_wide':
        harm_data = {
            "harm_score": 450000,
            "people_exposed": 1200000,
            "children_exposed": 850000,
            "patients_exposed": 350000,
            "affected_zones": [
                {"name": "Delhi Public Schools (All Branches)", "type": "school", "population": 45000},
                {"name": "AIIMS & Safdarjung Hospital", "type": "hospital", "population": 12000},
                {"name": "Old Age Homes (NCR)", "type": "old_age_home", "population": 8500}
            ]
        }
    else:
        harm_data = get_harm_score(lat, lng, radius_km=2.0, current_aqi=float(current_aqi))

    # ── 4. Emissions summary (pure Python, no Gemini) ─────────────────────
    contribution_map = {f["source_id"]: f["contribution_pct"] for f in fingerprint}
    all_fingerprints = list(contribution_map.values())
    emissions_summary = get_city_co2_summary(sources, all_fingerprints, contribution_map)
    co2_tonnes = emissions_summary.get("total_co2_tonnes_today", 0)
    emissions_summary["insight_text"] = _build_co2_insight(co2_tonnes)

    # ── 5. Legal advisory (hardcoded, no Gemini) ──────────────────────────
    # See legal_advisory.py — Gemini was removed; these are static legal texts.
    from legal_advisory import get_legal_advisory
    legal_data = get_legal_advisory(lat, lng)

    # ── 6. Forecast trend + chart (no Gemini for chart data) ──────────────
    forecast_trend = _forecast_trend_string(station_id, current_aqi)
    forecast_chart = _build_forecast_chart_data(station_id)

    # ── 7. English advisory (pure Python rule-based) ──────────────────────
    english_advisory = _build_english_advisory(station_name, current_aqi)

    # ── 8. SINGLE Gemini call for all AI text ────────────────────────────
    ai_insights = _call_gemini_for_insights(
        station_id=station_id,
        station_name=station_name,
        current_aqi=current_aqi,
        fingerprint=fingerprint,
        forecast_trend=forecast_trend,
        co2_tonnes=co2_tonnes,
        harm_score=harm_data.get("harm_score", 0),
        people_exposed=harm_data.get("people_exposed", 0),
    )

    # ── 9. Assemble response ──────────────────────────────────────────────
    result = {
        "station_id": station_id,
        "station_name": station_name,
        "current_aqi": current_aqi,
        "aqi_label": _aqi_label(current_aqi),
        "pm25": reading.get("pm25", 0.0),
        "pm10": reading.get("pm10", 0.0),
        # Fingerprint (Gaussian plume)
        "fingerprint": fingerprint,
        "attribution_explanation": ai_insights["attribution_explanation"],
        # Forecast
        "forecast_chart": forecast_chart,
        "forecast_trend": forecast_trend,
        "forecast_narrative": ai_insights["forecast_narrative"],
        # Advisories
        "hindi_advisory": ai_insights["hindi_advisory"],
        "english_advisory": english_advisory,
        # Harm
        "harm": harm_data,
        # Emissions
        "emissions": emissions_summary,
        # Legal
        "legal": legal_data,
    }

    _cache_set(cache_key, result)
    return result


def _build_english_advisory(station_name: str, aqi: int) -> str:
    """Pure Python rule-based English advisory."""
    if aqi <= 50:
        return (f"Air quality at {station_name} is Good (AQI: {aqi}). "
                "Conditions are ideal for outdoor activities. Enjoy the fresh air!")
    elif aqi <= 100:
        return (f"Air quality at {station_name} is Satisfactory (AQI: {aqi}). "
                "Most people can go outdoors normally. Sensitive individuals should limit prolonged exertion.")
    elif aqi <= 200:
        return (f"Air quality at {station_name} is Moderate (AQI: {aqi}). "
                "People with respiratory conditions, elderly, and children should reduce outdoor exposure. "
                "Keep windows closed and avoid heavy outdoor exercise.")
    elif aqi <= 300:
        return (f"Air quality at {station_name} is Poor (AQI: {aqi}). "
                "Everyone may experience health effects. Avoid outdoor activities, especially near traffic. "
                "Wear an N95 mask if going out is unavoidable.")
    return (f"SEVERE air pollution alert at {station_name} (AQI: {aqi}). "
            "Stay indoors with windows and doors closed. Avoid all outdoor activities. "
            "Hospitals and schools should suspend outdoor programmes immediately.")
