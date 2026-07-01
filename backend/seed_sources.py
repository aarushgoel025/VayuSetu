from db import supabase

SOURCES = [
    {"id": "s1", "name": "Badarpur Power Plant (Closed/Residual)", "type": "thermal_plant", "lat": 28.5033, "lng": 77.3040, "address": "Badarpur, Delhi", "activity_level": "low"},
    {"id": "s2", "name": "Okhla Industrial Area", "type": "industrial", "lat": 28.5273, "lng": 77.2798, "address": "Okhla, New Delhi", "activity_level": "high"},
    {"id": "s3", "name": "Central Secretariat Metro Construction", "type": "construction", "lat": 28.6143, "lng": 77.2118, "address": "Rajpath Area, Delhi", "activity_level": "high"},
    {"id": "s4", "name": "Ring Road Traffic - Ashram Chowk", "type": "traffic_corridor", "lat": 28.5721, "lng": 77.2570, "address": "Ashram Chowk, Delhi", "activity_level": "high"},
    {"id": "s5", "name": "Bawana Industrial Area", "type": "industrial", "lat": 28.7990, "lng": 77.0600, "address": "Bawana, Delhi", "activity_level": "medium"},
    {"id": "s6", "name": "NH-8 Traffic Corridor", "type": "traffic_corridor", "lat": 28.5283, "lng": 77.0988, "address": "NH-8, Delhi-Gurgaon", "activity_level": "high"},
    {"id": "s7", "name": "Narela Industrial Area", "type": "industrial", "lat": 28.8475, "lng": 77.0911, "address": "Narela, Delhi", "activity_level": "medium"},
    {"id": "s8", "name": "Dwarka Expressway Construction", "type": "construction", "lat": 28.5218, "lng": 76.9856, "address": "Dwarka, Delhi", "activity_level": "medium"},
    {"id": "s9", "name": "Mayapuri Industrial Area", "type": "industrial", "lat": 28.6310, "lng": 77.1264, "address": "Mayapuri, Delhi", "activity_level": "high"},
    {"id": "s10", "name": "ITO Traffic Junction", "type": "traffic_corridor", "lat": 28.6286, "lng": 77.2415, "address": "ITO, Delhi", "activity_level": "high"},
]

VULNERABLE_ZONES = [
    {"name": "AIIMS New Delhi", "type": "hospital", "lat": 28.5672, "lng": 77.2100, "estimated_population": 15000},
    {"name": "Delhi Public School RK Puram", "type": "school", "lat": 28.5615, "lng": 77.1751, "estimated_population": 4000},
    {"name": "Safdarjung Hospital", "type": "hospital", "lat": 28.5684, "lng": 77.2064, "estimated_population": 8000},
    {"name": "Springdales School Dhaula Kuan", "type": "school", "lat": 28.5866, "lng": 77.1643, "estimated_population": 2500},
    {"name": "HelpAge India Old Age Home", "type": "old_age_home", "lat": 28.5369, "lng": 77.1952, "estimated_population": 150},
]

def seed():
    if not supabase:
        print("Database not connected. Please set SUPABASE_URL and SUPABASE_KEY in .env")
        return

    # --- Seed Stations (from ingest.py STATIONS list) ---
    print("Seeding stations...")
    from ingest import STATIONS
    for st in STATIONS:
        try:
            resp = supabase.table("stations").upsert(st).execute()
            print(f"  OK station: {st['id']} -> {len(resp.data)} row(s)")
        except Exception as e:
            print(f"  FAIL station {st['id']}: {e}")

    # --- Seed Sources ---
    print("Seeding sources...")
    for s in SOURCES:
        try:
            resp = supabase.table("sources").upsert(s).execute()
            print(f"  OK source: {s['id']} -> {len(resp.data)} row(s)")
        except Exception as e:
            print(f"  FAIL source {s['id']}: {e}")

    # --- Seed Vulnerable Zones ---
    print("Seeding vulnerable zones...")
    for v in VULNERABLE_ZONES:
        try:
            resp = supabase.table("vulnerable_zones").insert(v).execute()
            print(f"  OK zone: {v['name']} -> {len(resp.data)} row(s)")
        except Exception as e:
            print(f"  SKIP zone {v['name']}: (likely already exists)")

    print("Seeding complete!")

if __name__ == "__main__":
    seed()
