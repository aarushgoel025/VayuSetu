# VayuSetu ML — AQI Ensemble Forecasting Model

This directory contains the machine learning model that powers VayuSetu's **24-hour AQI forecasting** for Delhi stations.

## Model Overview

**Architecture:** Inverse-MAE-Weighted Ensemble ("3 AI Judges")

| Judge | Algorithm | Role |
|-------|-----------|------|
| 1 | Linear Regression | Captures linear seasonal trends (fast baseline) |
| 2 | Random Forest | Handles nonlinear patterns + noisy CPCB data |
| 3 | Gradient Boosting | Sequentially corrects residual errors |

**Combination formula:**  
Each judge's weight = `(1 / its_MAE) / sum(1 / all_MAEs)`  
→ Lower error = higher weight. Weights sum to exactly 1.0.

## Data

- **Source:** CPCB Delhi AQI monitoring stations (2015–2023)
- **Stations:** Anand Vihar, Bawana, Dwarka Sector 8, IGI T3, ITO, Okhla Phase 2, Punjabi Bagh, RK Puram, Rohini
- **Split:** Train (2017–2021) → Val (2022, for weighting) → Test (2023, held-out)

> **Note:** Raw CSV training data is excluded from this repo (too large). Download from the shared drive or re-run `reshape_aqi.py` + `train_ensemble.py` with your local data.

## Files

| File | Description |
|------|-------------|
| `aqi_ensemble.pkl` | Trained model package (models + weights + label encoder) |
| `train_ensemble.py` | Full training pipeline with evaluation |
| `reshape_aqi.py` | Preprocesses raw CPCB station CSVs into `all_stations_long.csv` |
| `test_ensemble_predictions.py` | Validates model predictions against real data |
| `verify_model.py` | Quick sanity check on the loaded `.pkl` |
| `debug_weights.py` | Prints ensemble judge weights |
| `eda_check.py` | EDA utilities for the training data |
| `ensemble_run.log` | Training log with metrics from the last training run |

## Performance (Test Set — 2023, Held-Out)

See `ensemble_run.log` for full metrics. The ensemble consistently outperforms all three individual judges on MAE.

## How to Retrain

```bash
# 1. Install dependencies (use the backend venv or a new one)
pip install pandas numpy scikit-learn

# 2. Prepare data (if starting from raw CSVs)
python reshape_aqi.py

# 3. Train
python train_ensemble.py
# → Outputs: aqi_ensemble.pkl
```

## Backend Integration

The model is loaded in [`backend/forecast_agent.py`](../backend/forecast_agent.py).  
The model path is resolved **relative to the project root** using `MODEL_PATH` in `config.py`.

### Loaded Package Schema

```python
{
  "models":        {"lr": ..., "rf": ..., "gb": ...},   # sklearn models
  "weights":       {"w_lr": float, "w_rf": float, "w_gb": float},
  "val_mae":       {"lr": float, "rf": float, "gb": float},
  "test_metrics":  { ... },   # MAE / RMSE / R² per model
  "feature_cols":  [...],     # ordered list of 20 feature names
  "label_encoder": LabelEncoder,
  "description":   str
}
```
