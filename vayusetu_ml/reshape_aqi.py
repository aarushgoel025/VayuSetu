import os
import glob
import re
import pandas as pd
import numpy as np

def parse_cpcb_file(file_path, station_id):
    months_map = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    
    rows = []
    current_year = None
    current_month = None
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            # Skip blank or quote-only separator rows
            if not line_str or line_str == '"' or line_str.startswith('"'):
                continue
            
            # Detect header rows (e.g. "January-2017,00:00:00,01:00:00...")
            if "00:00:00" in line_str and "01:00:00" in line_str:
                parts = [p.strip().strip('"').strip("'") for p in line_str.split(",")]
                first_col = parts[0]
                match = re.match(r"^([A-Za-z]+)-(\d{4})$", first_col)
                if match:
                    month_name = match.group(1).lower()
                    year_val = int(match.group(2))
                    if month_name in months_map:
                        current_month = months_map[month_name]
                        current_year = year_val
                continue
            
            # If we haven't encountered a valid header yet, skip lines
            if not current_year or not current_month:
                continue
                
            # Parse day rows
            cols = [c.strip().strip('"').strip("'") for c in line_str.split(",")]
            if len(cols) < 25:
                continue
                
            col0 = cols[0]
            if not col0:
                continue
                
            try:
                # Convert day float/int representation to int (e.g. "1.0" or "1" -> 1)
                day_val = int(float(col0))
            except ValueError:
                continue
                
            if not (1 <= day_val <= 31):
                continue
                
            # Extract 24 hourly AQI values
            hourly_values = cols[1:25]
            for h in range(24):
                val_str = hourly_values[h]
                aqi_val = np.nan
                if val_str:
                    try:
                        aqi_val = float(val_str)
                    except ValueError:
                        pass
                
                try:
                    # Validate date correctness (handles calendar boundaries like Feb 30, April 31)
                    date_obj = pd.Timestamp(year=current_year, month=current_month, day=day_val)
                    dt_val = pd.Timestamp(year=current_year, month=current_month, day=day_val, hour=h)
                    
                    rows.append({
                        "datetime": dt_val,
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "hour": h,
                        "aqi": aqi_val,
                        "station_id": station_id
                    })
                except ValueError:
                    continue
                    
    df = pd.DataFrame(rows)
    return df

def main():
    directory = r"C:\Users\Ankit\Desktop\AQI data Delhi 2015-23"
    
    # 1. Process Anand Vihar first
    anand_vihar_path = os.path.join(directory, "Anand Vihar.csv")
    print(f"Processing Anand Vihar from: {anand_vihar_path}")
    df_av = parse_cpcb_file(anand_vihar_path, "Anand Vihar")
    
    # Columns requested: datetime, date, hour, aqi
    # Save as anand_vihar_long.csv (retaining station_id is fine, but let's select columns or keep it)
    df_av_output = df_av[["datetime", "date", "hour", "aqi"]]
    av_output_path = os.path.join(directory, "anand_vihar_long.csv")
    df_av_output.to_csv(av_output_path, index=False)
    print(f"Saved Anand Vihar long format to: {av_output_path}")
    
    # Print stats
    total_rows = len(df_av)
    min_date = df_av['date'].min()
    max_date = df_av['date'].max()
    missing_pct = df_av['aqi'].isna().mean() * 100
    print(f"--- Anand Vihar Stats ---")
    print(f"Total Row Count: {total_rows}")
    print(f"Date Range: {min_date} to {max_date}")
    print(f"Missing AQI %: {missing_pct:.2f}%")
    print("-" * 30)
    
    # 2. Process all other 8 files and concatenate
    all_dfs = [df_av]
    
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        if filename in ["Anand Vihar.csv", "anand_vihar_long.csv", "all_stations_long.csv"]:
            continue
            
        station_id = os.path.splitext(filename)[0]
        print(f"Processing station: {station_id} from {file_path}")
        df_station = parse_cpcb_file(file_path, station_id)
        
        # Stats for this station
        if not df_station.empty:
            st_rows = len(df_station)
            st_min = df_station['date'].min()
            st_max = df_station['date'].max()
            st_missing = df_station['aqi'].isna().mean() * 100
            print(f"Parsed {station_id} -> Rows: {st_rows}, Date Range: {st_min} to {st_max}, Missing: {st_missing:.2f}%")
            all_dfs.append(df_station)
        else:
            print(f"Warning: No data parsed for {station_id}")
            
    # Concatenate all 9 datasets
    df_all = pd.concat(all_dfs, ignore_index=True)
    all_output_path = os.path.join(directory, "all_stations_long.csv")
    
    # Ensure correct columns
    df_all_output = df_all[["station_id", "datetime", "date", "hour", "aqi"]]
    df_all_output.to_csv(all_output_path, index=False)
    print(f"Saved all 9 stations concatenated long format to: {all_output_path}")
    print(f"--- Combined Dataset Stats ---")
    print(f"Total Rows: {len(df_all)}")
    print(f"Unique Stations: {df_all['station_id'].nunique()}")
    print(f"Overall Missing AQI %: {df_all['aqi'].isna().mean() * 100:.2f}%")

if __name__ == "__main__":
    main()
