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
        # Use real plume contribution if available.
        # Default to 0.0 (not 100.0) — if a source isn't in the fingerprint,
        # it means its plume is not reaching this location (upwind / too far).
        pct = contribution_map.get(src_id, 0.0) if contribution_map else 100.0
        if pct <= 0:
            continue  # skip sources with zero contribution to this location
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
        "trend": "stable"
    }

def generate_co2_insight_text(summary: dict) -> str:
    """
    Pure-Python CO2 comparison — no Gemini call.
    Formula: 0.12 kg CO2/km × 40 km average daily drive = 4.8 kg CO2/car/day.
    NOTE: Gemini was removed here to save API credits. The output is identical
    in quality since this was just a fixed-formula comparison sentence.
    """
    total_tonnes = summary.get('total_co2_tonnes_today', 0)
    cars = int((total_tonnes * 1000) / (0.12 * 40))
    return f"This local footprint is equivalent to {cars:,} cars being driven today."
