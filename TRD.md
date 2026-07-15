# Technical Requirements Document (TRD)

## 1. System Architecture
VayuSetu follows a standard decoupled Client-Server architecture.
- **Client:** React Single Page Application (SPA) built with Vite.
- **Server:** Python FastAPI application serving RESTful endpoints.
- **AI Integration:** Google Gemini API for narrative generation.

## 2. Technology Stack

### Frontend (User Interface)
- **Framework:** React 18
- **Build Tool:** Vite
- **Styling:** Tailwind CSS (utility-first), `clsx` and `tailwind-merge` for class management.
- **Animations:** Framer Motion (scroll sequences and micro-interactions).
- **3D Rendering:** `cobe` (for the interactive WebGL globe).
- **Icons:** `lucide-react`.

### Backend (API Server)
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Language:** Python 3.9+
- **AI Provider:** `google-genai` (Gemini API).
- **Data Handling:** Native Python structures (mocking database for rapid prototyping).

## 3. Key Technical Decisions
- **Unified API Calls:** To reduce AI latency and API cost, the frontend makes a single call to `/api/station-panel`. The backend aggregates Gaussian plume calculations, harm scores, and sends a single, massive prompt to Gemini, returning a structured JSON payload that feeds all UI components simultaneously.
- **Mock Fallback System:** The frontend `api/client.js` is equipped with a `VITE_USE_MOCK_DATA` toggle. When true, it intercepts API calls and returns predefined JSON to allow UI development without backend dependency or API rate limits.
- **TTL Caching:** The backend caches Gemini responses for 30 minutes based on `station_id` and coordinates to prevent redundant processing.

## 4. External Dependencies
- NASA FIRMS API (simulated for Satellite Hotspots).
- CPCB API (simulated for AQI readings).
- Google Gemini API (Active, requires `GEMINI_API_KEY` in `.env`).
