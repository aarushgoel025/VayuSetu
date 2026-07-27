import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score

# Load the model package
with open(r"C:\Users\Ankit\Desktop\AQI data Delhi 2015-23\aqi_ensemble.pkl", "rb") as f:
    pkg = pickle.load(f)

w_lr, w_rf, w_gb = pkg["weights"]["w_lr"], pkg["weights"]["w_rf"], pkg["weights"]["w_gb"]
lr, rf, gb = pkg["models"]["lr"], pkg["models"]["rf"], pkg["models"]["gb"]
feature_cols = pkg["feature_cols"]
le = pkg["label_encoder"]

def ensemble_predict(X):
    return w_lr * lr.predict(X) + w_rf * rf.predict(X) + w_gb * gb.predict(X)

# Load data and prepare test set (2023) just like in training
df = pd.read_csv(r"C:\Users\Ankit\Desktop\AQI data Delhi 2015-23\all_stations_long.csv")
df["datetime"] = pd.to_datetime(df["datetime"])
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["station_id", "datetime"]).reset_index(drop=True)

def get_season(month):
    if month in [12, 1, 2]:   return 0
    if month in [3, 4, 5]:    return 1
    if month in [6, 7, 8, 9]: return 2
    return 3

df["month"] = df["date"].dt.month
df["day_of_week"] = df["datetime"].dt.dayofweek
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
df["season"] = df["month"].map(get_season)

df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

grp = df.groupby("station_id")["aqi"]
df["lag_1"] = grp.shift(1)
df["lag_2"] = grp.shift(2)
df["lag_3"] = grp.shift(3)
df["lag_6"] = grp.shift(6)
df["lag_24"] = grp.shift(24)
df["lag_48"] = grp.shift(48)

rolling_grp = df.groupby("station_id")["aqi"]
df["rolling_mean_3"] = rolling_grp.transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
df["rolling_mean_6"] = rolling_grp.transform(lambda x: x.shift(1).rolling(6, min_periods=1).mean())
df["rolling_mean_24"] = rolling_grp.transform(lambda x: x.shift(1).rolling(24, min_periods=1).mean())
df["rolling_std_3"] = rolling_grp.transform(lambda x: x.shift(1).rolling(3, min_periods=1).std())
df["station_enc"] = le.transform(df["station_id"])

df_clean = df.dropna(subset=feature_cols + ["aqi"]).reset_index(drop=True)
mask_test = df_clean["date"] > "2022-12-31"
df_test = df_clean[mask_test].copy()

X_test = df_test[feature_cols]
y_test = df_test["aqi"]

# Pick 10 random samples to show
sample_indices = np.random.choice(len(df_test), 10, replace=False)
samples = df_test.iloc[sample_indices].copy()
X_sample = samples[feature_cols]
y_sample_true = samples["aqi"].values

pred_sample = ensemble_predict(X_sample)

print("="*60)
print("TESTING ENSEMBLE MODEL ON 10 RANDOM 2023 DATA POINTS")
print("="*60)
print(f"{'Station':<15} | {'Date & Time':<20} | {'Actual AQI':<12} | {'Predicted AQI':<15} | {'Error'}")
print("-" * 80)
for i in range(10):
    station = samples.iloc[i]['station_id']
    dt = str(samples.iloc[i]['datetime'])
    actual = y_sample_true[i]
    pred = pred_sample[i]
    err = abs(actual - pred)
    print(f"{station[:13]:<15} | {dt:<20} | {actual:<12.1f} | {pred:<15.1f} | {err:.1f}")

print("\n" + "="*60)
print("OVERALL 2023 TEST SET METRICS (Unseen Data)")
print("="*60)
y_pred_all = ensemble_predict(X_test)
print(f"Mean Absolute Error (MAE): {mean_absolute_error(y_test, y_pred_all):.2f} AQI units")
print(f"R-squared (R2):            {r2_score(y_test, y_pred_all):.4f}")
