# Backend Schema & API Documentation

## 1. Database Schema (Mocked/In-Memory)

### `stations`
- `id` (String): Unique identifier.
- `name` (String): Station location name.
- `lat`, `lng` (Float): Coordinates.

### `sources`
- `id` (String): Unique identifier.
- `name` (String): Emitter name (e.g., Thermal Plant).
- `type` (String): Enum (industrial, traffic, construction, stubble_burning).
- `lat`, `lng` (Float): Coordinates.
- `base_emission_rate` (Float): Grams per second.

### `vulnerable_zones`
- `id` (String): Unique identifier.
- `name` (String): Institution name.
- `type` (String): Enum (school, hospital, old_age_home).
- `lat`, `lng` (Float): Coordinates.
- `population` (Integer): Estimated people at risk.

## 2. Core API Endpoints

### `GET /api/stations`
Returns a list of all AQI monitoring stations with their latest readings and wind vectors.

### `GET /api/sources`
Returns a list of known industrial and civic emission sources.

### `GET /api/satellite-hotspots`
Returns active fire anomalies (stubbling burning) detected by NASA VIIRS.

### `GET /api/station-panel?station_id={id}&lat={lat}&lng={lng}`
**The primary aggregated endpoint.**
Calculates wind dispersion, harm scores, and invokes Gemini for contextual generation.
**Response Body:**
```json
{
  "station_id": "string",
  "station_name": "string",
  "current_aqi": 312,
  "aqi_label": "Severe",
  "fingerprint": [
    { "source_name": "Badarpur Plant", "contribution_pct": 45 }
  ],
  "attribution_explanation": "Gemini generated text...",
  "forecast_narrative": "Gemini generated text...",
  "hindi_advisory": "Gemini generated text...",
  "english_advisory": "Rule-based text...",
  "harm": {
    "harm_score": 45000,
    "children_exposed": 820000,
    "patients_exposed": 380000,
    "affected_zones": [...]
  }
}
```

### `POST /api/generate-notice?source_id={id}`
Generates a PDF legal notice for the specified offending emission source and returns it as a streaming blob.
