from google import genai
from config import GEMINI_API_KEY

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

def estimate_co2_output(source: dict, contribution_pct: float, duration_hours: float = 24) -> dict:
    """Estimates CO2 based on emission factors."""
    factors = {
        "thermal_plant": {"high": 4500, "medium": 2800, "low": 1200},
        "industrial": {"high": 1800, "medium": 900, "low": 400},
        "construction": {"high": 600, "medium": 300, "low": 120},
        "traffic_corridor": {"high": 900, "medium": 450, "low": 180}
    }
    
    stype = source.get("type", "industrial")
    slevel = source.get("activity_level", "medium")
    
    factor = factors.get(stype, factors["industrial"]).get(slevel, 900)
    
    co2_kg = factor * duration_hours * (contribution_pct / 100.0)
    
    return {
        "source_id": source.get("id"),
        "co2_kg_today": round(co2_kg, 2),
        "co2_tonnes_today": round(co2_kg / 1000, 2),
        "equivalent_trees_needed": int(co2_kg / 21)
    }

def get_city_co2_summary(all_sources: list, all_fingerprints: list, contribution_map: dict = None) -> dict:
    """Aggregate across all sources using real Gaussian plume contributions where available."""
    total_kg = 0
    source_totals = []
    
    for src in all_sources:
        src_id = src.get("id")
        # Use real plume contribution if available, else fall back to 100% (total potential)
        pct = contribution_map.get(src_id, 100.0) if contribution_map else 100.0
        output = estimate_co2_output(src, pct)
        total_kg += output["co2_kg_today"]
        source_totals.append({
            "source_id": src_id,
            "source_name": src.get("name"),
            "co2_tonnes": output["co2_tonnes_today"],
            "contribution_pct": round(pct, 2)
        })
        
    source_totals.sort(key=lambda x: x["co2_tonnes"], reverse=True)
    
    return {
        "total_co2_tonnes_today": round(total_kg / 1000, 2),
        "top_emitters": source_totals[:5],
        "trend": "stable" # mock trend
    }

def generate_co2_insight_text(summary: dict) -> str:
    """Gemini, temperature=0.4. One relatable comparison sentence."""
    total_tonnes = summary.get('total_co2_tonnes_today', 0)
    
    if not client:
        cars = int((total_tonnes * 1000) / (0.12 * 40))
        return f"This is equivalent to {cars} cars being driven today."
        
    prompt = f"""
    The city emitted {total_tonnes} tonnes of CO2 today.
    Write exactly ONE relatable comparison sentence (e.g. equivalent to X cars driven today).
    Use 0.12kg CO2/km and 40km average daily drive as the constant.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(temperature=0.4)
        )
        return response.text.strip()
    except Exception as e:
        cars = int((total_tonnes * 1000) / (0.12 * 40))
        return f"This is equivalent to {cars} cars being driven today."
