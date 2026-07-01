# VayuSetu Backend

This is the backend for VayuSetu (PS5 — Urban Air Quality Intelligence).
Built with FastAPI, Supabase, and Gemini.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your API keys (AQICN, OpenWeather, Gemini, Supabase).
3. Run `python seed_sources.py` to populate initial database state.
4. Run `uvicorn main:app --reload` to start the server.

## Architecture & Integration (Person A & Person B)

- **main.py**: Entrypoint. Loads Person A's routes (`add_routes_a`) and Person B's routes (`add_routes_b`).
- **routes.py**: Contains `add_routes_a` for map foundation, dispersion, emissions, and notice generation. Lakshita (Person B) should append her endpoints in a new `add_routes_b` function.
- **config.py**: Holds env vars. Person B can append their new keys at the marked space.
- **db.py**: Generic Supabase connection and helpers. Used by both A and B.
- **ingest.py, dispersion.py, emissions.py, notice_generator.py**: Person A's hard features. Person B's logic can read the tables updated by these modules, or import helper functions where explicitly permitted (e.g., `get_harm_score` imported in `notice_generator.py` and `log_notice_issued` imported in `notice_generator.py`).
