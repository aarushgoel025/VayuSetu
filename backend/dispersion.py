import math
from google import genai
from config import GEMINI_API_KEY

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

def calculate_contribution(source_lat, source_lng, source_type, wind_speed_kmh, wind_deg, target_lat, target_lng) -> float:
    """Gaussian plume dispersion model, returns relative contribution 0.0-1.0.
    C(x,y,z) = (Q / (2*pi*u*sigma_y*sigma_z)) * exp(-y^2/(2*sigma_y^2)) * exp(-z^2/(2*sigma_z^2))
    """
    # Q by source_type
    Q_map = {
        "thermal_plant": 100,
        "industrial": 70,
        "construction": 50,
        "traffic_corridor": 40
    }
    Q = Q_map.get(source_type, 10)
    
    # Wind speed in m/s
    u = max(wind_speed_kmh / 3.6, 1.0) # avoid division by zero
    
    # Distance calculation (haversine/equirectangular approx)
    R = 6371000 # Earth radius in meters
    lat1_rad = math.radians(source_lat)
    lat2_rad = math.radians(target_lat)
    dlat = math.radians(target_lat - source_lat)
    dlng = math.radians(target_lng - source_lng)
    
    x_dist = dlng * math.cos((lat1_rad + lat2_rad) / 2) * R
    y_dist = dlat * R
    distance = math.sqrt(x_dist**2 + y_dist**2)
    
    if distance < 1:
        distance = 1 # Avoid zero distance
        
    # Determine downwind x and crosswind y based on wind direction
    # Wind direction is where wind is coming FROM.
    # Plume goes TO wind_deg + 180
    plume_dir = (wind_deg + 180) % 360
    
    # Angle from source to target
    target_angle = math.atan2(x_dist, y_dist)
    target_angle_deg = (math.degrees(target_angle) + 360) % 360
    
    angle_diff = abs(target_angle_deg - plume_dir)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
        
    if angle_diff > 90:
        return 0.0 # Target is upwind
        
    angle_diff_rad = math.radians(angle_diff)
    
    # x: downwind distance, y: crosswind distance
    x = distance * math.cos(angle_diff_rad)
    y = distance * math.sin(angle_diff_rad)
    
    if x < 1:
        x = 1
        
    # Effective stack height (H) by source_type in meters
    H_map = {
        "thermal_plant": 150.0,
        "industrial": 50.0,
        "construction": 10.0,
        "traffic_corridor": 2.0
    }
    H = H_map.get(source_type, 10.0)
    
    # Pasquill-Gifford class D
    sigma_y = 0.08 * x * (1 + 0.0001 * x) ** -0.5
    sigma_z = 0.06 * x * (1 + 0.0015 * x) ** -0.5
    
    z = 2.0 # receptor height (breathing level)
    
    term_y = math.exp(- (y**2) / (2 * sigma_y**2))
    
    # term_z with ground reflection (standard Gaussian Plume implementation)
    term_z = math.exp(- ((z - H)**2) / (2 * sigma_z**2)) + math.exp(- ((z + H)**2) / (2 * sigma_z**2))
    
    C = (Q / (2 * math.pi * u * sigma_y * sigma_z)) * term_y * term_z
    
    # normalize to roughly 0-1 for relative scale within bounds
    # Since Q is arbitrary, this gives a raw magnitude
    return float(C)

def get_fingerprint(target_lat, target_lng, wind_speed, wind_deg, all_sources: list) -> list[dict]:
    """Run calculate_contribution for every source, normalize to 100%, sorted descending, only >2%."""
    raw_contributions = []
    total_c = 0.0
    
    for s in all_sources:
        c = calculate_contribution(s["lat"], s["lng"], s["type"], wind_speed, wind_deg, target_lat, target_lng)
        raw_contributions.append({
            "source_id": s["id"],
            "source_name": s["name"],
            "source_type": s["type"],
            "c_val": c
        })
        total_c += c
        
    if total_c == 0:
        return []
        
    fingerprint = []
    for rc in raw_contributions:
        pct = (rc["c_val"] / total_c) * 100
        if pct > 2.0:
            fingerprint.append({
                "source_id": rc["source_id"],
                "source_name": rc["source_name"],
                "source_type": rc["source_type"],
                "contribution_pct": round(pct, 2)
            })
            
    fingerprint.sort(key=lambda x: x["contribution_pct"], reverse=True)
    return fingerprint

def generate_attribution_explanation(fingerprint: list[dict], location_name: str) -> str:
    """Gemini 2.5 Flash, temperature=0.3. 2-3 sentence plain-English explanation of the fingerprint."""
    if not fingerprint:
        return "Local pollution sources are currently minimal or blowing away from this location."
        
    prompt = f"Given this pollution fingerprint for {location_name}: {fingerprint}. Write a 2-3 sentence plain-English explanation of what is causing the pollution here."
    
    if not client:
        return "Explanation placeholder (Gemini not configured)."
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(temperature=0.3)
        )
        return response.text.strip()
    except Exception as e:
        return "Unable to generate explanation at this time."
