import pickle
with open(r"C:\Users\Ankit\Desktop\AQI data Delhi 2015-23\aqi_ensemble.pkl", "rb") as f:
    pkg = pickle.load(f)

w = pkg["weights"]
print("Saved weights:")
print(f"  w_lr = {w['w_lr']:.6f}")
print(f"  w_rf = {w['w_rf']:.6f}")
print(f"  w_gb = {w['w_gb']:.6f}")
print(f"  SUM  = {w['w_lr']+w['w_rf']+w['w_gb']:.6f}  (must be 1.0)")
print("\nTest metrics:")
for k, v in pkg["test_metrics"].items():
    print(f"  {k}: MAE={v['mae']:.2f}, RMSE={v['rmse']:.2f}, R2={v['r2']:.4f}")
print("\nFeatures:", pkg["feature_cols"])
