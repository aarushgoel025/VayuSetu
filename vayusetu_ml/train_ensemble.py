"""
train_ensemble.py
─────────────────────────────────────────────────────────────────────────────
VayuSetu AQI Ensemble Model Trainer
"3 AI Judges" — Inverse-MAE-Weighted Ensemble

Judges:
  1. Linear Regression  — catches linear seasonal trends (fast baseline)
  2. Random Forest      — handles nonlinear patterns + noisy CPCB data
  3. Gradient Boosting  — sequentially corrects residual errors, often most
                          accurate on tabular pollution data

Combination formula:
  Each judge gets a voting weight = (1 / its_MAE) / sum(1 / all_MAEs)
  → Models with lower error get higher weight (inverse-error weighting)
  → Weights sum to 1.0 by construction

Task: Forecast AQI for hour t using only information available at t-1 and
      before (no data leakage). Lag features are computed per-station.

Train: 2017-01-01 to 2021-12-31
Val:   2022-01-01 to 2022-12-31  (used only to compute MAE weights)
Test:  2023-01-01 to 2023-12-31  (held-out final evaluation)

Output: aqi_ensemble.pkl  (models + weights + encoder, for backend inference)
─────────────────────────────────────────────────────────────────────────────
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder

# ── 1. Config ──────────────────────────────────────────────────────────────
# Paths are relative to this script's directory (vayusetu_ml/)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(_SCRIPT_DIR, "data", "all_stations_long.csv")
OUTPUT_DIR  = _SCRIPT_DIR
MODEL_FILE  = os.path.join(OUTPUT_DIR, "aqi_ensemble.pkl")

TRAIN_END   = "2021-12-31"
VAL_END     = "2022-12-31"

# ── 2. Load data ───────────────────────────────────────────────────────────
print("=" * 60)
print("VayuSetu AQI Ensemble Trainer -- 3 AI Judges")
print("=" * 60)
print("\n[1/6] Loading data...")
df = pd.read_csv(DATA_PATH)
df["datetime"] = pd.to_datetime(df["datetime"])
df["date"]     = pd.to_datetime(df["date"])

print(f"      Loaded {len(df):,} rows across {df['station_id'].nunique()} stations.")
print(f"      Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"      AQI missing: {df['aqi'].isna().mean()*100:.1f}%")

# ── 3. Feature Engineering ─────────────────────────────────────────────────
print("\n[2/6] Engineering features (lag & temporal)...")

df = df.sort_values(["station_id", "datetime"]).reset_index(drop=True)

# India-specific season encoding
# Winter: Dec-Feb (peak pollution), Pre-monsoon: Mar-May,
# Monsoon: Jun-Sep (lowest pollution), Post-monsoon: Oct-Nov
def get_season(month):
    if month in [12, 1, 2]:   return 0  # Winter
    if month in [3, 4, 5]:    return 1  # Pre-monsoon
    if month in [6, 7, 8, 9]: return 2  # Monsoon
    return 3                             # Post-monsoon

df["month"]       = df["date"].dt.month
df["day_of_week"] = df["datetime"].dt.dayofweek  # Monday=0
df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)
df["season"]      = df["month"].map(get_season)

# Cyclical encoding for hour and month (wraps correctly: 23->0, Dec->Jan)
df["hour_sin"]  = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"]  = np.cos(2 * np.pi * df["hour"] / 24)
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

# Lag features computed per station (no bleed-across stations)
grp = df.groupby("station_id")["aqi"]
df["lag_1"]  = grp.shift(1)   # 1h ago
df["lag_2"]  = grp.shift(2)   # 2h ago
df["lag_3"]  = grp.shift(3)   # 3h ago
df["lag_6"]  = grp.shift(6)   # 6h ago
df["lag_24"] = grp.shift(24)  # Same hour yesterday
df["lag_48"] = grp.shift(48)  # Same hour 2 days ago

# Rolling statistics (shift(1) ensures no current-hour leakage)
rolling_grp = df.groupby("station_id")["aqi"]
df["rolling_mean_3"]  = rolling_grp.transform(lambda x: x.shift(1).rolling(3,  min_periods=1).mean())
df["rolling_mean_6"]  = rolling_grp.transform(lambda x: x.shift(1).rolling(6,  min_periods=1).mean())
df["rolling_mean_24"] = rolling_grp.transform(lambda x: x.shift(1).rolling(24, min_periods=1).mean())
df["rolling_std_3"]   = rolling_grp.transform(lambda x: x.shift(1).rolling(3,  min_periods=1).std())

# Station encoding
le = LabelEncoder()
df["station_enc"] = le.fit_transform(df["station_id"])

feature_cols = [
    "hour", "hour_sin", "hour_cos",
    "month", "month_sin", "month_cos",
    "day_of_week", "is_weekend", "season",
    "lag_1", "lag_2", "lag_3", "lag_6", "lag_24", "lag_48",
    "rolling_mean_3", "rolling_mean_6", "rolling_mean_24", "rolling_std_3",
    "station_enc"
]
target_col = "aqi"

df_clean = df.dropna(subset=feature_cols + [target_col]).reset_index(drop=True)
print(f"      After dropping NaN-lag rows: {len(df_clean):,} rows ({(1-len(df_clean)/len(df))*100:.1f}% dropped)")

# ── 4. Train / Val / Test Split (chronological, no shuffle) ───────────────
print("\n[3/6] Time-based split...")

mask_train = df_clean["date"] <= TRAIN_END
mask_val   = (df_clean["date"] > TRAIN_END) & (df_clean["date"] <= VAL_END)
mask_test  = df_clean["date"] > VAL_END

X_train, y_train = df_clean.loc[mask_train, feature_cols], df_clean.loc[mask_train, target_col]
X_val,   y_val   = df_clean.loc[mask_val,   feature_cols], df_clean.loc[mask_val,   target_col]
X_test,  y_test  = df_clean.loc[mask_test,  feature_cols], df_clean.loc[mask_test,  target_col]

print(f"      Train: {len(X_train):>7,} rows  (2017-2021)")
print(f"      Val:   {len(X_val):>7,} rows  (2022 - weighting only)")
print(f"      Test:  {len(X_test):>7,} rows  (2023 - held-out)")

# ── 5. Train the 3 Judges ─────────────────────────────────────────────────
print("\n[4/6] Training 3 judges on identical feature set...")

lr = LinearRegression()
rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
gb = GradientBoostingRegressor(n_estimators=100, max_depth=4,
                                learning_rate=0.1, random_state=42)

print("      [1/3] Linear Regression...")
lr.fit(X_train, y_train)

print("      [2/3] Random Forest (100 trees, max_depth=8)...")
rf.fit(X_train, y_train)

print("      [3/3] Gradient Boosting (100 trees, lr=0.1, max_depth=4)...")
gb.fit(X_train, y_train)

print("      All 3 judges trained.")

# ── 6. Inverse-MAE Weighting ───────────────────────────────────────────────
print("\n[5/6] Computing inverse-MAE weights from validation set (2022)...")

mae_lr = mean_absolute_error(y_val, lr.predict(X_val))
mae_rf = mean_absolute_error(y_val, rf.predict(X_val))
mae_gb = mean_absolute_error(y_val, gb.predict(X_val))

def compute_weights(mae_lr, mae_rf, mae_gb):
    """
    Inverse-error weighting: lower MAE = higher weight.
    Weights are normalised to sum to 1.0 exactly.
    This is the "3 AI Judges" formula for VayuSetu.
    """
    inv_lr = 1.0 / mae_lr
    inv_rf = 1.0 / mae_rf
    inv_gb = 1.0 / mae_gb
    total  = inv_lr + inv_rf + inv_gb
    return inv_lr / total, inv_rf / total, inv_gb / total

w_lr, w_rf, w_gb = compute_weights(mae_lr, mae_rf, mae_gb)

print(f"\n      {'Judge':<25} {'Val MAE':>10}  {'Weight':>8}")
print(f"      {'-'*48}")
print(f"      {'Linear Regression':<25} {mae_lr:>10.2f}  {w_lr:>7.4f}  ({w_lr*100:.1f}%)")
print(f"      {'Random Forest':<25} {mae_rf:>10.2f}  {w_rf:>7.4f}  ({w_rf*100:.1f}%)")
print(f"      {'Gradient Boosting':<25} {mae_gb:>10.2f}  {w_gb:>7.4f}  ({w_gb*100:.1f}%)")
print(f"      {'Sum':<25} {'':>10}  {w_lr+w_rf+w_gb:>7.4f}  (should be 1.0000)")

def ensemble_predict(X, lr, rf, gb, w_lr, w_rf, w_gb):
    """
    Returns the weighted combination of all three judges' predictions.
    Each model contributes proportional to its validation accuracy.
    """
    return w_lr * lr.predict(X) + w_rf * rf.predict(X) + w_gb * gb.predict(X)

# ── 7. Final Evaluation on Held-Out Test Set 2023 ─────────────────────────
print("\n[6/6] Evaluating on held-out test set (2023)...")

pred_lr  = lr.predict(X_test)
pred_rf  = rf.predict(X_test)
pred_gb  = gb.predict(X_test)
pred_ens = ensemble_predict(X_test, lr, rf, gb, w_lr, w_rf, w_gb)

def eval_model(y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2))
    r2   = r2_score(y_true, y_pred)
    return mae, rmse, r2

mae_lr_t,  rmse_lr_t,  r2_lr_t  = eval_model(y_test, pred_lr)
mae_rf_t,  rmse_rf_t,  r2_rf_t  = eval_model(y_test, pred_rf)
mae_gb_t,  rmse_gb_t,  r2_gb_t  = eval_model(y_test, pred_gb)
mae_ens_t, rmse_ens_t, r2_ens_t = eval_model(y_test, pred_ens)

print(f"\n      {'Model':<25} {'MAE':>8}  {'RMSE':>8}  {'R2':>8}")
print(f"      {'-'*55}")
print(f"      {'Linear Regression':<25} {mae_lr_t:>8.2f}  {rmse_lr_t:>8.2f}  {r2_lr_t:>8.4f}")
print(f"      {'Random Forest':<25} {mae_rf_t:>8.2f}  {rmse_rf_t:>8.2f}  {r2_rf_t:>8.4f}")
print(f"      {'Gradient Boosting':<25} {mae_gb_t:>8.2f}  {rmse_gb_t:>8.2f}  {r2_gb_t:>8.4f}")
print(f"      {'-'*55}")
print(f"      {'ENSEMBLE (weighted)':<25} {mae_ens_t:>8.2f}  {rmse_ens_t:>8.2f}  {r2_ens_t:>8.4f}")

best_ind = min(mae_lr_t, mae_rf_t, mae_gb_t)
improvement = (best_ind - mae_ens_t) / best_ind * 100
print(f"\n      Ensemble improvement over best individual: {improvement:+.2f}%")

# ── 8. Save Model Package ─────────────────────────────────────────────────
print(f"\n[Save] Writing model package to: {MODEL_FILE}")

model_package = {
    "models":        {"lr": lr, "rf": rf, "gb": gb},
    "weights":       {"w_lr": float(w_lr), "w_rf": float(w_rf), "w_gb": float(w_gb)},
    "val_mae":       {"lr": float(mae_lr), "rf": float(mae_rf), "gb": float(mae_gb)},
    "test_metrics":  {
        "lr":       {"mae": mae_lr_t,  "rmse": rmse_lr_t,  "r2": r2_lr_t},
        "rf":       {"mae": mae_rf_t,  "rmse": rmse_rf_t,  "r2": r2_rf_t},
        "gb":       {"mae": mae_gb_t,  "rmse": rmse_gb_t,  "r2": r2_gb_t},
        "ensemble": {"mae": mae_ens_t, "rmse": rmse_ens_t, "r2": r2_ens_t},
    },
    "feature_cols":  feature_cols,
    "label_encoder": le,
    "description":   "VayuSetu AQI Ensemble — Inverse-MAE-Weighted 3-Judge model",
}

with open(MODEL_FILE, "wb") as f:
    pickle.dump(model_package, f)

print(f"      Saved successfully.")

# ── 9. Print UI-Ready Weights ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("ENSEMBLE WEIGHTS (ready to paste into UI or backend):")
print("=" * 60)
print(f"  Linear Regression:  {w_lr:.4f}  ({w_lr*100:.1f}%)")
print(f"  Random Forest:      {w_rf:.4f}  ({w_rf*100:.1f}%)")
print(f"  Gradient Boosting:  {w_gb:.4f}  ({w_gb*100:.1f}%)")
print(f"\n  Test MAE  (2023): {mae_ens_t:.2f} AQI units")
print(f"  Test RMSE (2023): {rmse_ens_t:.2f} AQI units")
print(f"  Test R2   (2023): {r2_ens_t:.4f}")
print("=" * 60)
print("\nDone.")
