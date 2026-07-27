import pandas as pd

df = pd.read_csv(r"C:\Users\Ankit\Desktop\AQI data Delhi 2015-23\all_stations_long.csv")
print("Shape:", df.shape)
print("Dtypes:\n", df.dtypes)
print("Stations:", df['station_id'].unique().tolist())
print("\nSample:\n", df.head(10))
print("\nNulls per column:\n", df.isnull().sum())
print("\nDate range:", df['date'].min(), "to", df['date'].max())
print("\nHour distribution:\n", df['hour'].value_counts().sort_index())
