from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def get_table(table_name: str) -> list:
    """Generic helper to get all rows from a table."""
    if not supabase:
        print(f"Supabase client not initialized.")
        return []
    try:
        response = supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        print(f"DB error in get_table({table_name}): {e}")
        return []


def insert_row(table_name: str, data: dict):
    """Generic helper to insert a row into a table."""
    if not supabase:
        print(f"Supabase client not initialized.")
        return None
    try:
        response = supabase.table(table_name).insert(data).execute()
        return response.data
    except Exception as e:
        print(f"DB error in insert_row({table_name}): {e}")
        return None


def query_latest_per_station() -> list:
    """Returns the single latest reading for each station."""
    if not supabase:
        print(f"Supabase client not initialized.")
        return []
    try:
        response = (
            supabase.table("readings")
            .select("*")
            .order("timestamp", desc=True)
            .execute()
        )
        latest_readings = {}
        for r in response.data:
            station_id = r["station_id"]
            if station_id not in latest_readings:
                latest_readings[station_id] = r
        return list(latest_readings.values())
    except Exception as e:
        print(f"DB error in query_latest_per_station: {e}")
        return []


def get_readings_for_station(station_id: str, limit: int = 168) -> list:
    """
    Returns the last `limit` readings for a given station,
    ordered by timestamp descending.
    Default limit = 168 = 7 days of hourly data (for forecast agent).
    """
    if not supabase:
        print(f"Supabase client not initialized.")
        return []
    try:
        response = (
            supabase.table("readings")
            .select("*")
            .eq("station_id", station_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"DB error in get_readings_for_station({station_id}): {e}")
        return []


def get_all_sources() -> list:
    """Returns all rows from the sources table."""
    if not supabase:
        print(f"Supabase client not initialized.")
        return []
    try:
        response = supabase.table("sources").select("*").execute()
        return response.data
    except Exception as e:
        print(f"DB error in get_all_sources: {e}")
        return []


def get_source_by_id(source_id: str) -> dict | None:
    """Returns a single source row matching source_id, or None if not found."""
    if not supabase:
        print(f"Supabase client not initialized.")
        return None
    try:
        response = (
            supabase.table("sources")
            .select("*")
            .eq("id", source_id)
            .single()
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"DB error in get_source_by_id({source_id}): {e}")
        return None


def get_all_vulnerable_zones() -> list:
    """Returns all rows from the vulnerable_zones table."""
    if not supabase:
        print(f"Supabase client not initialized.")
        return []
    try:
        response = supabase.table("vulnerable_zones").select("*").execute()
        zones = response.data
        for z in zones:
            if not z.get("population"):
                if z.get("type") == "school":
                    z["population"] = 1200
                elif z.get("type") == "hospital":
                    z["population"] = 800
                elif z.get("type") == "old_age_home":
                    z["population"] = 150
                else:
                    z["population"] = 500
        return zones
    except Exception as e:
        print(f"DB error in get_all_vulnerable_zones: {e}")
        return []


def insert_reading(
    station_id: str,
    aqi: int,
    pm25: float,
    pm10: float,
    wind_speed: float,
    wind_deg: float
) -> bool:
    """
    Inserts one AQI + wind reading into the readings table.
    Returns True on success, False on failure.
    """
    if not supabase:
        print(f"Supabase client not initialized.")
        return False
    try:
        from datetime import datetime, timezone
        data = {
            "station_id": station_id,
            "aqi": aqi,
            "pm25": pm25,
            "pm10": pm10,
            "wind_speed": wind_speed,
            "wind_deg": wind_deg,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("readings").insert(data).execute()
        return True
    except Exception as e:
        print(f"DB error in insert_reading({station_id}): {e}")
        return False