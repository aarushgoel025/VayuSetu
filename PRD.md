# Product Requirements Document (PRD) - VayuSetu

## 1. Project Overview
**VayuSetu** is an Urban Air Quality Intelligence platform designed specifically for the Delhi NCR region. It bridges the gap between raw environmental data and actionable insights for both citizens and government authorities. By leveraging real-time data, satellite hotspots, and Gemini AI, VayuSetu provides hyper-local, narrative-driven air quality assessments.

## 2. Target Audience
- **Citizens:** Need simplified, actionable health advisories, localized air quality forecasts, and an understanding of what is causing the pollution in their specific ward.
- **City Authorities / Policymakers:** Need comprehensive dashboards to track active violations, identify major emission sources (like thermal plants or traffic corridors), and auto-generate legal notices to offenders.

## 3. Core Problems Solved
- **Data Overload:** Traditional AQI platforms show numbers but lack context. VayuSetu translates numbers into plain English/Hindi health advisories.
- **Source Attribution:** Citizens often don't know *why* the air is bad. VayuSetu uses Gaussian plume logic and wind vectors to pinpoint exact emission sources (e.g., "Badarpur Thermal Plant is causing 45% of the local particulate matter").
- **Vulnerable Populations:** The platform calculates a "Harm Score" based on nearby schools, hospitals, and old-age homes to quantify the human cost of localized pollution.

## 4. Key Features
- **Scrollytelling Landing Page:** A cinematic, 3D interactive globe experience that guides users into the application.
- **Dual Portal System:** Seamless toggle between Citizen View (health focus) and Authority View (enforcement focus).
- **Interactive Map:** Displays monitoring stations, emission sources, vulnerable zones, and NASA satellite fire hotspots.
- **Unified Station Panel:** Clicking a station generates a holistic, Gemini-powered analysis of the area, combining attribution, forecasting, and health advisories.
- **Automated Legal Notices:** Authorities can generate legal PDF notices for repeat industrial offenders with a single click.

## 5. Future Roadmap
- Integration with live CPCB hardware APIs.
- Mobile application deployment.
- Expansion to other Tier-1 Indian cities beyond NCR.
