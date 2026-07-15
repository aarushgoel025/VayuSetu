import requests

locs = [
    ("Anand Vihar", 28.6469, 77.3160),
    ("RK Puram",    28.5638, 77.1869),
    ("Bawana",      28.7706, 77.0384),
    ("Noida S125",  28.5355, 77.3910),
]

for name, lat, lng in locs:
    r = requests.get(f"http://localhost:8000/api/emissions-summary", params={"lat": lat, "lng": lng})
    d = r.json()
    total = d.get("total_co2_tonnes_today", 0)
    emitters = d.get("top_emitters", [])
    top = emitters[0] if emitters else {}
    print(f"{name:20s}: {total:8.2f} t  | top -> {top.get('source_name','—')} ({top.get('co2_tonnes',0)} t, {top.get('contribution_pct',0)}%)")
