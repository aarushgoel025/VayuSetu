from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def get_table(table_name: str):
    """Generic helper to get all rows from a table."""
    if not supabase: return []
    response = supabase.table(table_name).select("*").execute()
    return response.data

def insert_row(table_name: str, data: dict):
    """Generic helper to insert a row into a table."""
    if not supabase: return None
    response = supabase.table(table_name).insert(data).execute()
    return response.data

def query_latest_per_station():
    """Returns the latest reading for each station."""
    if not supabase: return []
    response = supabase.table("readings").select("*").order("timestamp", desc=True).execute()
    
    latest_readings = {}
    for r in response.data:
        station_id = r["station_id"]
        if station_id not in latest_readings:
            latest_readings[station_id] = r
            
    return list(latest_readings.values())
