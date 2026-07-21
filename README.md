# 🌬️ VayuSetu — Urban Air Quality Intelligence System

> **"Data without action is just noise. VayuSetu turns pollution data into regulatory enforcement."**

VayuSetu is an AI-powered urban air quality intelligence platform built for the **ET AI Hackathon 2.0**. It bridges the gap between raw sensor data and real-world regulatory enforcement, providing dual portals for government authorities (enforcement & accountability) and citizens (health advisories & transparency).

---

## 📸 What VayuSetu Does

| Feature | Description |
|---|---|
| 🗺️ **Live Multi-Layer Map** | Real-time AQI stations, emission sources, vulnerable zones (schools/hospitals), and NASA FIRMS satellite thermal hotspots — all on one map |
| 🔬 **Gaussian Plume Source Attribution** | Mathematically attributes pollution at any station to specific industrial sources using atmospheric physics |
| 🤖 **Hybrid AQI Forecasting** | 24-48 hour forecasts using a trained ML ensemble (LR + RF + GB) with Gemini AI fallback |
| ⚖️ **Automated Legal Enforcement** | One-click PDF legal notice generation under Section 19 of the Air (Prevention & Control of Pollution) Act, 1981 |
| 👶 **Vulnerable Population Tracking** | Calculates children, seniors, and hospitals within 2 km of any pollution hotspot |
| 🛰️ **NASA Satellite Fusion** | Integrates NASA FIRMS VIIRS satellite thermal data for fire/stubble-burning detection |
| 🌐 **Bilingual Advisories** | English + Hindi health advisories for maximum citizen reach |
| 🔐 **Supabase Auth** | JWT-based authentication for the authority portal |

---

## 🏗️ Architecture Overview

```
VayuSetu/
├── backend/          # Python FastAPI server
│   ├── main.py           # App entry point, APScheduler data ingest job
│   ├── routes.py         # All API route handlers
│   ├── station_panel.py  # Unified station intelligence aggregator
│   ├── dispersion.py     # Gaussian Plume source attribution model
│   ├── forecast_agent.py # Hybrid ML + Gemini AQI forecasting
│   ├── harm_score.py     # Vulnerable population radius analysis
│   ├── notice_generator.py # ReportLab PDF legal notice generation
│   ├── violation_tracker.py # Repeat offender tracking
│   ├── legal_advisory.py # Legal advisory text engine
│   ├── emissions.py      # Emissions estimation
│   ├── ingest.py         # AQICN + OpenWeatherMap data ingestion
│   ├── db.py             # Supabase database helpers
│   ├── auth.py           # JWT authentication middleware
│   ├── config.py         # Environment variable loader
│   └── requirements.txt  # Python dependencies
│
└── frontend/         # React + Vite application
    ├── src/
    │   ├── App.jsx           # Main app, authority portal
    │   ├── components/
    │   │   ├── MapView.jsx       # Leaflet map with 4 data layers
    │   │   ├── StationMarker.jsx # AQI station bubbles
    │   │   ├── ZoneMarker.jsx    # Vulnerable zone markers
    │   │   ├── ForecastChart.jsx # 24h AQI forecast chart
    │   │   ├── FingerprintList.jsx # Source attribution list
    │   │   ├── HarmScoreCard.jsx # Vulnerable population card
    │   │   ├── LegalAdvisoryCard.jsx # Legal notice UI
    │   │   ├── EmissionsCard.jsx # Emissions summary
    │   │   ├── CitizenDashboard.jsx # Citizen portal
    │   │   ├── LandingSequence.jsx  # Animated landing page
    │   │   └── Login.jsx            # Auth screen
    │   └── api/
    │       ├── client.js     # API call functions + mock fallbacks
    │       └── supabase.js   # Supabase client initializer
    └── package.json
```

---

## 🔑 API Keys — Where to Get Them

You need **5 API keys** to run VayuSetu. All are free to obtain.

### 1. AQICN API Key (Air Quality Data)
- Go to: **https://aqicn.org/data-platform/token/**
- Sign up with your email
- Your token will be emailed to you immediately
- Used for: Real-time AQI readings from NCR monitoring stations

### 2. OpenWeatherMap API Key (Wind Data)
- Go to: **https://home.openweathermap.org/users/sign_up**
- Create a free account
- Navigate to **API Keys** tab in your dashboard
- Copy the default key (or create a new one)
- Used for: Wind speed and direction data for the Gaussian dispersion model
- **Note:** Free tier allows 1,000 calls/day — sufficient for development

### 3. Google Gemini API Key (AI Forecasting)
- Go to: **https://aistudio.google.com/apikey**
- Sign in with your Google account
- Click **"Create API Key"**
- Copy the generated key
- Used for: AQI forecast fallback for unknown stations and station panel intelligence

### 4. Supabase Project (Database + Auth)
- Go to: **https://supabase.com** and sign up
- Click **"New Project"**, choose a name and set a database password
- Once created, go to **Project Settings → API**
- You need two values:
  - **Project URL** → used as `SUPABASE_URL`
  - **`service_role` secret key** → used as `SUPABASE_KEY` (backend, has full DB access)
  - **`anon` public key** → used as `VITE_SUPABASE_ANON_KEY` (frontend, restricted access)
- Run the seed script after setup: `python backend/seed_sources.py`

### 5. NASA FIRMS API Key (Satellite Hotspots)
- Go to: **https://firms.modaps.eosdis.nasa.gov/api/area/**
- Click **"Get API Key"** and register
- Your key will be shown immediately after registration
- Used for: NASA FIRMS VIIRS thermal hotspot data (fire/stubble burning detection)

---

## ⚙️ Environment Setup

### Backend — `backend/.env`
Create a file at `backend/.env` with the following contents:

```env
AQICN_API_KEY="your_aqicn_token_here"
OPENWEATHER_API_KEY="your_openweathermap_key_here"
GEMINI_API_KEY="your_gemini_api_key_here"
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_KEY="your_supabase_service_role_key_here"
FIRMS_KEY="your_nasa_firms_key_here"
```

### Frontend — `frontend/.env`
Create a file at `frontend/.env` with the following contents:

```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false
VITE_SUPABASE_URL="https://your-project-id.supabase.co"
VITE_SUPABASE_ANON_KEY="your_supabase_anon_key_here"
```

> ⚠️ **Important:** Use the `anon` (public) key for `VITE_SUPABASE_ANON_KEY`, NOT the `service_role` key. The service_role key has admin access and must never be exposed in the frontend.

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/aarushgoel025/VayuSetu.git
cd VayuSetu
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create your `backend/.env` file (see Environment Setup above).

Seed the database with initial source and vulnerable zone data:
```bash
python seed_sources.py
```

Start the backend server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 3. Frontend Setup
```bash
cd frontend
npm install
```

Create your `frontend/.env` file (see Environment Setup above).

Start the development server:
```bash
npm run dev
```

The app will be available at: `http://localhost:5173`

---

## 🗄️ Database Schema (Supabase Tables)

VayuSetu uses the following Supabase tables. Run the seed script to auto-populate them.

| Table | Description |
|---|---|
| `stations` | AQI monitoring station metadata (name, lat, lng, city) |
| `readings` | Real-time AQI sensor readings (AQI, PM2.5, timestamp) |
| `sources` | Known emission sources (thermal plants, industrial zones, etc.) |
| `vulnerable_zones` | Schools, hospitals, old age homes with population estimates |
| `violations` | Logged enforcement violations per source |
| `notices_log` | Audit trail of all generated legal notices |

---

## 📡 Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/stations` | Get all AQI stations with latest readings |
| `GET` | `/api/station-panel` | Unified station intelligence (forecast, attribution, health, emissions, legal) |
| `GET` | `/api/sources` | Get all known emission sources |
| `GET` | `/api/vulnerable-zones` | Get all vulnerable zones (schools/hospitals) |
| `GET` | `/api/satellite-hotspots` | NASA FIRMS thermal hotspots |
| `GET` | `/api/accountability-feed` | Enforcement activity feed |
| `POST` | `/api/generate-notice` | Generate & download PDF legal notice |
| `GET` | `/api/violation-history/{source_id}` | Violation history for a source |
| `POST` | `/api/auth/signin` | User authentication |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Framer Motion |
| **Maps** | Leaflet, React-Leaflet |
| **Charts** | Recharts |
| **Backend** | Python, FastAPI, Uvicorn |
| **Database** | Supabase (PostgreSQL) |
| **Auth** | Supabase Auth + PyJWT |
| **AI/ML** | Google Gemini Flash, Scikit-learn (LR + RF + GB ensemble) |
| **Data Sources** | AQICN, OpenWeatherMap, NASA FIRMS VIIRS |
| **PDF Generation** | ReportLab |
| **Task Scheduling** | APScheduler (15-min data ingest loop) |

---

## 🧠 How the AI Works

### Source Attribution (Gaussian Plume Model)
VayuSetu uses a **Pasquill-Gifford Class D Gaussian Plume Dispersion Model** to calculate how much each known emission source contributes to the measured AQI at a given station. Real-time wind speed and direction data from OpenWeatherMap is used to calculate the plume trajectory and concentration at the station coordinates.

### AQI Forecasting (Hybrid ML)
- **Known NCR stations:** A trained ensemble model (Linear Regression + Random Forest + Gradient Boosting) predicts the next 24-48 hours using lag features (1h, 2h, 6h, 24h, 48h), rolling statistics, and cyclical time encoding (sin/cos for hour and month).
- **Unknown stations:** Falls back to Gemini Flash for narrative forecast generation, or a simple linear regression.

---

## ⚠️ Known Limitations
- The V1 ML model is trained on Delhi NCR data only — AQI forecasting for other cities is less accurate.
- The Gaussian plume model uses averaged wind vectors — does not account for spatial wind field variation.
- "Report a Source" feature in Citizen Dashboard is a UI prototype; API integration pending.

---

## 📄 License
This project is submitted as part of the **ET AI Hackathon 2.0**. All rights reserved by the team.

---

## 🙌 Team
Built with ❤️ for cleaner air, faster enforcement, and smarter cities.
