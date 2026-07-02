import math
from typing import Union, List, Dict, Any
from db import get_table, query_latest_per_station

def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Computes the great-circle distance between two points in kilometers.
    """
    R = 6371.0  # Earth's radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(d_lat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _get_multiplier(zone_type: str) -> float:
    """
    Returns the exposure multiplier associated with each vulnerable zone type.
    """
    multipliers = {
        "school": 1.5,
        "hospital": 2.0,
        "old_age_home": 1.8
    }
    return multipliers.get(zone_type.lower(), 1.0)

def _find_closest_aqi(lat: float, lng: float) -> float:
    """
    Finds the AQI of the closest monitoring station based on coordinates.
    Defaults to 180.0 if no stations or readings are found.
    """
    try:
        stations = get_table("stations")
        latest_readings = query_latest_per_station()
        if not stations or not latest_readings:
            return 180.0
            
        readings_map = {r["station_id"]: r for r in latest_readings}
        
        closest_distance = float("inf")
        closest_aqi = 180.0
        
        for s in stations:
            s_id = s.get("id")
            s_lat = s.get("lat")
            s_lng = s.get("lng")
            
            if s_id and s_lat is not None and s_lng is not None:
                dist = _haversine_distance(lat, lng, float(s_lat), float(s_lng))
                if dist < closest_distance:
                    reading = readings_map.get(s_id)
                    if reading and reading.get("aqi") is not None:
                        closest_distance = dist
                        closest_aqi = float(reading["aqi"])
                        
        return closest_aqi
    except Exception as e:
        print(f"Error fetching closest station AQI: {e}")
        return 180.0

def get_harm_score(
    zone_lat: Union[float, str],
    zone_lng: float = None,
    radius_km: float = None,
    current_aqi: float = None
) -> dict:
    """
    Calculates the harm score and vulnerable population exposure within a given radius.
    
    Supports two signatures:
    1. get_harm_score(zone_lat, zone_lng, radius_km, current_aqi)
    2. get_harm_score(source_id)  [Compatibility fallback for Aarush's notice_generator.py]
    
    Returns:
        dict: {
            "harm_score": float,
            "children_exposed": int,
            "patients_exposed": int,
            "affected_zones": [{"name": str, "type": str, "population": int}],
            # Aarush compatibility keys:
            "score": float,
            "people_exposed": int,
            "zones_affected": list[str]
        }
    """
    # Default outputs
    result = {
        "harm_score": 0.0,
        "children_exposed": 0,
        "patients_exposed": 0,
        "affected_zones": [],
        "score": 0.0,
        "people_exposed": 0,
        "zones_affected": []
    }
    
    try:
        # Determine if single-argument source_id fallback is active
        if isinstance(zone_lat, str) or zone_lng is None:
            source_id = str(zone_lat)
            sources = get_table("sources")
            source = next((s for s in sources if s.get("id") == source_id), None)
            if not source:
                return result
                
            lat = float(source.get("lat", 0.0))
            lng = float(source.get("lng", 0.0))
            rad = float(radius_km) if radius_km is not None else 5.0
            aqi = float(current_aqi) if current_aqi is not None else _find_closest_aqi(lat, lng)
        else:
            lat = float(zone_lat)
            lng = float(zone_lng)
            rad = float(radius_km) if radius_km is not None else 5.0
            aqi = float(current_aqi) if current_aqi is not None else 180.0

        # Exposure rule: hours_exposed = 8 if AQI > 150 else 0
        hours_exposed = 8.0 if aqi > 150.0 else 0.0
        
        # Query vulnerable zones
        vulnerable_zones = get_table("vulnerable_zones")
        
        harm_score_sum = 0.0
        children = 0
        patients = 0
        affected_zones_list = []
        zones_names = []
        
        for zone in vulnerable_zones:
            z_lat = zone.get("lat")
            z_lng = zone.get("lng")
            z_name = zone.get("name", "Unknown Zone")
            z_type = zone.get("type", "unknown")
            pop = int(zone.get("estimated_population", 0))
            
            if z_lat is not None and z_lng is not None:
                dist = _haversine_distance(lat, lng, float(z_lat), float(z_lng))
                if dist <= rad:
                    multiplier = _get_multiplier(z_type)
                    harm_score_sum += float(pop) * hours_exposed * multiplier
                    
                    if z_type.lower() == "school":
                        children += pop
                    elif z_type.lower() == "hospital":
                        patients += pop
                        
                    affected_zones_list.append({
                        "name": z_name,
                        "type": z_type,
                        "population": pop
                    })
                    zones_names.append(z_name)
                    
        result["harm_score"] = round(harm_score_sum, 2)
        result["children_exposed"] = children
        result["patients_exposed"] = patients
        result["affected_zones"] = affected_zones_list
        
        # Compatibility fields for Aarush's notice_generator.py
        result["score"] = round(harm_score_sum, 2)
        result["people_exposed"] = children + patients  # Sum of core vulnerable groups
        result["zones_affected"] = zones_names
        
    except Exception as e:
        print(f"Error calculating harm score: {e}")
        
    return result
