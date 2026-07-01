# Project Name - VayuSetu

### What our project does
*The system follows a bottom-up architecture where raw environmental data is collected from multiple sources, processed by an AI engine to generate pollution intelligence, transformed into decision-support insights, and finally delivered through dedicated dashboards for authorities and citizens.*

1) Acquires Raw Data 
   - Two layers- 
        1.  Data Source- Source	                        What it gives us	Cost
                        AQICN API	                    Real-time AQI, PM2.5, PM10 readings from Indian monitoring stations	Free (1,000 calls/day)
                        OpenWeatherMap	                Wind speed and direction — critical input for the dispersion model	Free tier
                        OpenStreetMap (Overpass API)	Schools, hospitals, old-age homes as GeoJSON — for victim impact scoring	Free
                        Mock source database	        Manually seeded list of ~15–20 known emission sources (thermal plants, construction  zones,industrial areas) with coordinates	Free (we build it)
        2. Ingestion- 
            •	A scheduled FastAPI job (APScheduler) pulls AQI and wind data every 15 minutes
            •	Data is stored in Supabase PostgreSQL (free tier) as a time-series table
            •	GeoJSON layers (schools, hospitals, sources) are loaded once at setup
    Data is fetched using the data sources and then using the FastAPI jobs the AQI and wind data is pulled every 15 minutes and then the data is cleaned and formatted to be stored in a Supabase Postgre SQL and thus ready for AI processing and information like schools, hospitals etc are all loaded once at setup since there is no need to fetch them every 15 minutes
2) Gets processed by AI core
    This is the major brain of our project
    - It contains 1 layer 
        AI CORE:
        The AI Core does not directly fetch data from the external data sources (AQICN or OpenWeatherMap). Instead, it retrieves the latest processed data from Supabase, which acts as the centralized data repository.
        It contains 3 major parts:
          1. Dispersion Engine: From the supabase the gaussian plum model has everything it needs and thus on the basis of wind speed and its direction it measures exactly how the pollution disperses downwind from a source. These source contribution estimates are then used by the Pollution Fingerprint module to determine the percentage contribution of each source to the observed pollution.
          **The gausian plum model only gives us the numbers** 
          2. Gemini 2.5 flash: The Gemini 2.5 flash converts these numbers into explanations ie **24 hour AQI forecast and citizen advisory**
          3. Chroma DB: Only used when we need to draft a legal notice. It stores all the relevant legal documents and when the officer clicks draft a legal notice, Chroma DB is used then.
3) Passes through unique differentiator models
   Simply means that all the data processed, is made into actionable insight such as polluton fingerprint, victim impact score and legal notice generator
4) Produces outputs for both the authorities and the citizens
    Contains portal for both :
    1. Authorities
        *Users*:
        Pollution Control Board
        Municipal officers
        Inspectors
        *Contains*:
        Live Leaflet Map
        Enforcement Panel
        Evidence PDF Download
    2. Citizens
        *Users*:
        General public
        *Contains*:
        Hindi/English health advisories
        Public accountability feed