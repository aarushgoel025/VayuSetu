# VayuSetu Frontend

This is the fully functioning React + Tailwind CSS frontend for VayuSetu (PS5 - Urban Air Quality Intelligence).

## Setup & Run

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run the Development Server:**
   ```bash
   npm run dev
   ```

## API Connection

The application is controlled by `.env` variables:
- `VITE_USE_MOCK_DATA=true` — Runs using the rich mock data defined in `src/mockData/mock.js`. Does not require the FastAPI backend to be running.
- `VITE_USE_MOCK_DATA=false` — Connects to the real backend running at `VITE_API_URL` (default: `http://localhost:8000`).

## Tech Stack
- **Framework:** Vite + React
- **Styling:** Tailwind CSS v3
- **Mapping:** react-leaflet + Leaflet (CartoDB Dark Matter tiles)
- **Charts:** Recharts
- **Icons:** Lucide React
