from db import supabase

try:
    response = supabase.table('readings').select('id, aqi, pm25').gt('aqi', 500).execute()
    for row in response.data:
        pm25 = row.get('pm25', 0)
        new_aqi = pm25 if pm25 > 0 and pm25 < 400 else 500
        supabase.table('readings').update({'aqi': new_aqi}).eq('id', row['id']).execute()
        print(f"Updated row {row['id']} AQI from {row['aqi']} to {new_aqi}")
    print("Done")
except Exception as e:
    print(e)
