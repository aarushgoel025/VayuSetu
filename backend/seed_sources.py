from db import supabase

SOURCES = [
    # --- Waste-to-Energy & Power Plants ---
    {"id": "s1", "name": "Badarpur Power Plant (Closed/Residual Dust)", "type": "thermal_plant", "lat": 28.5033, "lng": 77.3040, "address": "Badarpur, Delhi", "activity_level": "low"},
    {"id": "s11", "name": "Okhla Waste-to-Energy Plant", "type": "thermal_plant", "lat": 28.5284, "lng": 77.2721, "address": "Okhla, Delhi", "activity_level": "high"},
    {"id": "s12", "name": "Ghazipur Waste-to-Energy Plant", "type": "thermal_plant", "lat": 28.6258, "lng": 77.3259, "address": "Ghazipur, Delhi", "activity_level": "high"},
    {"id": "s13", "name": "Narela-Bawana Waste-to-Energy", "type": "thermal_plant", "lat": 28.8032, "lng": 77.0620, "address": "Bawana, Delhi", "activity_level": "medium"},
    {"id": "s14", "name": "Dadri Thermal Power Plant", "type": "thermal_plant", "lat": 28.5985, "lng": 77.6046, "address": "Dadri, UP", "activity_level": "high"},

    # --- Landfills (Fires/Methane) ---
    {"id": "s15", "name": "Ghazipur Landfill Site", "type": "industrial", "lat": 28.6251, "lng": 77.3276, "address": "Ghazipur, Delhi", "activity_level": "high"},
    {"id": "s16", "name": "Bhalswa Landfill Site", "type": "industrial", "lat": 28.7408, "lng": 77.1624, "address": "Jahangirpuri, Delhi", "activity_level": "high"},
    {"id": "s17", "name": "Okhla Landfill Site", "type": "industrial", "lat": 28.5118, "lng": 77.2838, "address": "Okhla, Delhi", "activity_level": "medium"},

    # --- Major Industrial Hubs ---
    {"id": "s2", "name": "Okhla Industrial Area (Phases I-III)", "type": "industrial", "lat": 28.5273, "lng": 77.2798, "address": "Okhla, New Delhi", "activity_level": "high"},
    {"id": "s5", "name": "Bawana Industrial Area", "type": "industrial", "lat": 28.7990, "lng": 77.0600, "address": "Bawana, Delhi", "activity_level": "high"},
    {"id": "s7", "name": "Narela Industrial Area", "type": "industrial", "lat": 28.8475, "lng": 77.0911, "address": "Narela, Delhi", "activity_level": "high"},
    {"id": "s9", "name": "Mayapuri Industrial Area", "type": "industrial", "lat": 28.6310, "lng": 77.1264, "address": "Mayapuri, Delhi", "activity_level": "high"},
    {"id": "s18", "name": "Wazirpur Industrial Area", "type": "industrial", "lat": 28.6974, "lng": 77.1592, "address": "Wazirpur, Delhi", "activity_level": "high"},
    {"id": "s19", "name": "Patparganj Industrial Area", "type": "industrial", "lat": 28.6339, "lng": 77.3101, "address": "Patparganj, Delhi", "activity_level": "medium"},
    {"id": "s20", "name": "Sahibabad Industrial Area", "type": "industrial", "lat": 28.6657, "lng": 77.3496, "address": "Sahibabad, Ghaziabad", "activity_level": "high"},
    {"id": "s21", "name": "Udyog Vihar", "type": "industrial", "lat": 28.5028, "lng": 77.0864, "address": "Gurugram, Haryana", "activity_level": "high"},
    {"id": "s22", "name": "Naraina Industrial Area", "type": "industrial", "lat": 28.6288, "lng": 77.1438, "address": "Naraina, Delhi", "activity_level": "medium"},
    {"id": "s23", "name": "Anand Parbat Industrial Area", "type": "industrial", "lat": 28.6576, "lng": 77.1824, "address": "Anand Parbat, Delhi", "activity_level": "high"},
    {"id": "s24", "name": "Kirti Nagar Industrial Area", "type": "industrial", "lat": 28.6479, "lng": 77.1424, "address": "Kirti Nagar, Delhi", "activity_level": "medium"},

    # --- Major Traffic Hubs / Corridors ---
    {"id": "s10", "name": "ITO Traffic Junction", "type": "traffic_corridor", "lat": 28.6286, "lng": 77.2415, "address": "ITO, Delhi", "activity_level": "high"},
    {"id": "s4", "name": "Ring Road - Ashram Chowk", "type": "traffic_corridor", "lat": 28.5721, "lng": 77.2570, "address": "Ashram Chowk, Delhi", "activity_level": "high"},
    {"id": "s6", "name": "NH-8 Delhi-Gurgaon Border", "type": "traffic_corridor", "lat": 28.5283, "lng": 77.0988, "address": "NH-8, Delhi-Gurgaon", "activity_level": "high"},
    {"id": "s25", "name": "Anand Vihar ISBT & Railway", "type": "traffic_corridor", "lat": 28.6469, "lng": 77.3160, "address": "Anand Vihar, Delhi", "activity_level": "high"},
    {"id": "s26", "name": "Kashmere Gate ISBT", "type": "traffic_corridor", "lat": 28.6678, "lng": 77.2281, "address": "Kashmere Gate, Delhi", "activity_level": "high"},
    {"id": "s27", "name": "Dhaula Kuan Intersection", "type": "traffic_corridor", "lat": 28.5878, "lng": 77.1627, "address": "Dhaula Kuan, Delhi", "activity_level": "high"},
    {"id": "s28", "name": "Peera Garhi Chowk", "type": "traffic_corridor", "lat": 28.6791, "lng": 77.0927, "address": "Peera Garhi, Delhi", "activity_level": "high"},
    {"id": "s29", "name": "Mukarba Chowk", "type": "traffic_corridor", "lat": 28.7363, "lng": 77.1524, "address": "Jahangirpuri, Delhi", "activity_level": "high"},
    {"id": "s30", "name": "Rajiv Chowk (Gurugram)", "type": "traffic_corridor", "lat": 28.4552, "lng": 77.0326, "address": "Gurugram, Haryana", "activity_level": "high"},

    # --- Major Construction Hubs ---
    {"id": "s3", "name": "Central Secretariat / Central Vista", "type": "construction", "lat": 28.6143, "lng": 77.2118, "address": "Rajpath Area, Delhi", "activity_level": "medium"},
    {"id": "s8", "name": "Dwarka Expressway Construction", "type": "construction", "lat": 28.5218, "lng": 76.9856, "address": "Dwarka, Delhi", "activity_level": "medium"},
    {"id": "s31", "name": "RRTS Construction Corridor", "type": "construction", "lat": 28.6722, "lng": 77.3912, "address": "Ghaziabad, UP", "activity_level": "high"},
    {"id": "s32", "name": "Noida Extension Construction Hub", "type": "construction", "lat": 28.6019, "lng": 77.4418, "address": "Greater Noida West", "activity_level": "high"},
]

VULNERABLE_ZONES = [
    # --- Delhi ---
    {"name": "AIIMS New Delhi", "type": "hospital", "lat": 28.5672, "lng": 77.2100, "estimated_population": 15000},
    {"name": "Safdarjung Hospital", "type": "hospital", "lat": 28.5684, "lng": 77.2064, "estimated_population": 8000},
    {"name": "Sir Ganga Ram Hospital", "type": "hospital", "lat": 28.6384, "lng": 77.1897, "estimated_population": 6000},
    {"name": "RML Hospital", "type": "hospital", "lat": 28.6253, "lng": 77.2012, "estimated_population": 7500},
    {"name": "Hindu Rao Hospital", "type": "hospital", "lat": 28.6713, "lng": 77.2109, "estimated_population": 4000},
    {"name": "Max Super Speciality Hospital Saket", "type": "hospital", "lat": 28.5273, "lng": 77.2117, "estimated_population": 3000},
    {"name": "Fortis Escorts Heart Institute Okhla", "type": "hospital", "lat": 28.5601, "lng": 77.2796, "estimated_population": 2500},
    {"name": "Holy Family Hospital Okhla", "type": "hospital", "lat": 28.5630, "lng": 77.2750, "estimated_population": 2000},
    {"name": "Delhi Public School RK Puram", "type": "school", "lat": 28.5615, "lng": 77.1751, "estimated_population": 4000},
    {"name": "Springdales School Dhaula Kuan", "type": "school", "lat": 28.5866, "lng": 77.1643, "estimated_population": 2500},
    {"name": "Vasant Valley School", "type": "school", "lat": 28.5312, "lng": 77.1469, "estimated_population": 1800},
    {"name": "Modern School Barakhamba Road", "type": "school", "lat": 28.6293, "lng": 77.2274, "estimated_population": 3000},
    {"name": "St. Columba's School", "type": "school", "lat": 28.6310, "lng": 77.2066, "estimated_population": 3200},
    {"name": "The Shri Ram School, Vasant Vihar", "type": "school", "lat": 28.5614, "lng": 77.1593, "estimated_population": 2100},
    {"name": "HelpAge India Old Age Home", "type": "old_age_home", "lat": 28.5369, "lng": 77.1952, "estimated_population": 150},
    {"name": "Godhuli Senior Citizens Home Dwarka", "type": "old_age_home", "lat": 28.5912, "lng": 77.0435, "estimated_population": 120},
    {"name": "Sandhya Old Age Home Netaji Nagar", "type": "old_age_home", "lat": 28.5750, "lng": 77.1901, "estimated_population": 80},
    {"name": "Ashirwad Old Age Home Rohini", "type": "old_age_home", "lat": 28.7153, "lng": 77.1147, "estimated_population": 100},
    {"name": "Anand Vihar Hospital", "type": "hospital", "lat": 28.6475, "lng": 77.3155, "estimated_population": 5000},
    {"name": "Vivekanand School Anand Vihar", "type": "school", "lat": 28.6450, "lng": 77.3170, "estimated_population": 3000},
    {"name": "LNJP Hospital ITO", "type": "hospital", "lat": 28.6386, "lng": 77.2405, "estimated_population": 12000},
    {"name": "Bal Bhavan Public School ITO", "type": "school", "lat": 28.6290, "lng": 77.2450, "estimated_population": 2000},
    {"name": "Maharaja Agrasen Hospital Punjabi Bagh", "type": "hospital", "lat": 28.6720, "lng": 77.1320, "estimated_population": 6000},
    {"name": "Hansraj Model School Punjabi Bagh", "type": "school", "lat": 28.6750, "lng": 77.1300, "estimated_population": 3500},
    
    # --- Gurugram ---
    {"name": "Medanta Hospital Gurugram", "type": "hospital", "lat": 28.4300, "lng": 77.0500, "estimated_population": 10000},
    {"name": "Fortis Memorial Research Institute", "type": "hospital", "lat": 28.4580, "lng": 77.0725, "estimated_population": 4000},
    {"name": "Artemis Hospital", "type": "hospital", "lat": 28.4326, "lng": 77.0683, "estimated_population": 3000},
    {"name": "DPS Gurugram", "type": "school", "lat": 28.4520, "lng": 77.0300, "estimated_population": 4000},
    {"name": "The Heritage School", "type": "school", "lat": 28.4116, "lng": 77.0674, "estimated_population": 2500},
    {"name": "Pathways World School", "type": "school", "lat": 28.3292, "lng": 77.0510, "estimated_population": 2000},
    {"name": "Shiv Nadar School", "type": "school", "lat": 28.4184, "lng": 77.0984, "estimated_population": 2200},
    {"name": "NEMA Eldercare", "type": "old_age_home", "lat": 28.4285, "lng": 77.0700, "estimated_population": 150},
    {"name": "Golden Estate Old Age Home", "type": "old_age_home", "lat": 28.4190, "lng": 77.0110, "estimated_population": 100},

    # --- Noida ---
    {"name": "Jaypee Hospital Noida", "type": "hospital", "lat": 28.5200, "lng": 77.3600, "estimated_population": 7000},
    {"name": "Fortis Hospital Noida", "type": "hospital", "lat": 28.6186, "lng": 77.3725, "estimated_population": 3500},
    {"name": "Kailash Hospital Sector 27", "type": "hospital", "lat": 28.5772, "lng": 77.3236, "estimated_population": 2500},
    {"name": "Amity International School Noida", "type": "school", "lat": 28.5430, "lng": 77.3300, "estimated_population": 4500},
    {"name": "Step by Step School", "type": "school", "lat": 28.4984, "lng": 77.3719, "estimated_population": 2500},
    {"name": "Genesis Global School", "type": "school", "lat": 28.5020, "lng": 77.3722, "estimated_population": 1500},
    {"name": "Lotus Valley International School", "type": "school", "lat": 28.5318, "lng": 77.3482, "estimated_population": 2000},
    {"name": "Vridhashram Old Age Home Sector 55", "type": "old_age_home", "lat": 28.6010, "lng": 77.3501, "estimated_population": 120},
    {"name": "Anand Niketan Old Age Home", "type": "old_age_home", "lat": 28.5801, "lng": 77.3312, "estimated_population": 90},

    # --- Faridabad & Ghaziabad ---
    {"name": "Asian Institute of Medical Sciences", "type": "hospital", "lat": 28.4230, "lng": 77.3101, "estimated_population": 2500},
    {"name": "Metro Hospital Faridabad", "type": "hospital", "lat": 28.4069, "lng": 77.3235, "estimated_population": 1500},
    {"name": "Delhi Public School Faridabad", "type": "school", "lat": 28.3846, "lng": 77.3168, "estimated_population": 3500},
    {"name": "Mata Amar Kaur Old Age Home", "type": "old_age_home", "lat": 28.4150, "lng": 77.2912, "estimated_population": 70},
    {"name": "Yashoda Super Speciality Hospital", "type": "hospital", "lat": 28.6534, "lng": 77.3270, "estimated_population": 3000},
    {"name": "Max Super Speciality Hospital Vaishali", "type": "hospital", "lat": 28.6430, "lng": 77.3204, "estimated_population": 2500},
    {"name": "DPS Indirapuram", "type": "school", "lat": 28.6366, "lng": 77.3688, "estimated_population": 4000},
    {"name": "Sai Vridhashram Ghaziabad", "type": "old_age_home", "lat": 28.6601, "lng": 77.3510, "estimated_population": 110},
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
    # First, clear old data and re-insert to avoid duplicates
    try:
        supabase.table("vulnerable_zones").delete().neq("id", 0).execute()
        print("  Cleared old vulnerable zones.")
    except Exception as e:
        print(f"  Could not clear old zones: {e}")
    
    for v in VULNERABLE_ZONES:
        try:
            resp = supabase.table("vulnerable_zones").insert(v).execute()
            print(f"  OK zone: {v['name']} -> {len(resp.data)} row(s)")
        except Exception as e:
            print(f"  SKIP zone {v['name']}: {e}")

    print("Seeding complete!")

if __name__ == "__main__":
    seed()
