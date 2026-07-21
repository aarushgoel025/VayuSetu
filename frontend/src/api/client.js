import { 
  mockStations, 
  mockSources, 
  mockAttribution, 
  mockForecast, 
  mockLegalAdvisory, 
  mockViolationHistory, 
  mockRepeatOffenders, 
  mockEmissions, 
  mockEmissionsSummary, 
  mockAccountabilityFeed,
  mockVulnerableZones
} from '../mockData/mock';
import { supabase } from './supabase';

const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function fetchWithMockFallback(endpoint, mockData, options = {}) {
  if (USE_MOCK_DATA) {
    await delay(600); // Simulate network latency
    return mockData;
  }
  
  const headers = { ...options.headers };
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`;
    }
  } catch (err) {
    console.warn("Could not retrieve Supabase session:", err);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}


export async function getStations() {
  return fetchWithMockFallback('/api/stations', mockStations);
}

export async function getSources() {
  return fetchWithMockFallback('/api/sources', mockSources);
}

export async function getVulnerableZones() {
  return fetchWithMockFallback('/api/vulnerable-zones', mockVulnerableZones);
}

export async function getAttribution(lat, lng) {
  return fetchWithMockFallback(`/api/attribution?lat=${lat}&lng=${lng}`, mockAttribution);
}

export async function getForecast(stationId) {
  return fetchWithMockFallback(`/api/forecast?station_id=${stationId}`, mockForecast);
}


export async function getLegalAdvisory(lat, lng, sourceId = null) {
  const url = sourceId 
    ? `/api/legal-advisory?lat=${lat}&lng=${lng}&source_id=${sourceId}`
    : `/api/legal-advisory?lat=${lat}&lng=${lng}`;
  return fetchWithMockFallback(url, mockLegalAdvisory);
}

export async function getViolationHistory(sourceId) {
  return fetchWithMockFallback(`/api/violation-history?source_id=${sourceId}`, mockViolationHistory);
}

export async function getRepeatOffenders() {
  return fetchWithMockFallback('/api/repeat-offenders', mockRepeatOffenders);
}

export async function getEmissions(sourceId, lat, lng) {
  const url = lat && lng 
    ? `/api/emissions?source_id=${sourceId}&lat=${lat}&lng=${lng}`
    : `/api/emissions?source_id=${sourceId}`;
  return fetchWithMockFallback(url, mockEmissions);
}

export async function getEmissionsSummary(lat, lng) {
  const url = lat && lng 
    ? `/api/emissions-summary?lat=${lat}&lng=${lng}`
    : `/api/emissions-summary`;
  return fetchWithMockFallback(url, mockEmissionsSummary);
}

export async function getAccountabilityFeed() {
  return fetchWithMockFallback('/api/accountability-feed', mockAccountabilityFeed);
}

export async function getHealthAdvisory(stationId, lat, lng) {
  return fetchWithMockFallback(
    `/api/health-advisory?station_id=${stationId}&lat=${lat}&lng=${lng}`,
    {
      station_id: stationId,
      station_name: 'This Station',
      current_aqi: 180,
      forecast_trend: 'stable — no major change expected in the next 6 hours',
      english: 'Air quality is Moderate. People with respiratory conditions, elderly, and children should reduce outdoor exposure. Keep windows closed and avoid heavy outdoor exercise.',
      hinglish: 'Aaj yahan ki hawa thodi kharab hai. Bachon aur buzurgon ko bahar jaane se bachna chahiye, aur bahar nikalte waqt N95 mask zaroor pehnein. Ghar ki khidkiyan band rakhein.',
    }
  );
}

export async function getSatelliteHotspots() {
  return fetchWithMockFallback('/api/satellite-hotspots', {
    hotspots: [
      { lat: 28.6310, lng: 77.4725, brightness: 341.2, confidence: 'high',    confidence_level: 3, frp: 12.4, satellite: 'VIIRS', acq_date: '2025-07-10' },
      { lat: 28.5083, lng: 77.3024, brightness: 328.8, confidence: 'nominal', confidence_level: 2, frp: 7.1,  satellite: 'VIIRS', acq_date: '2025-07-10' },
      { lat: 28.7706, lng: 77.0384, brightness: 356.4, confidence: 'high',    confidence_level: 3, frp: 18.9, satellite: 'VIIRS', acq_date: '2025-07-10' },
      { lat: 28.4501, lng: 77.0263, brightness: 312.1, confidence: 'low',     confidence_level: 1, frp: 3.2,  satellite: 'VIIRS', acq_date: '2025-07-10' },
      { lat: 28.6731, lng: 77.4700, brightness: 339.6, confidence: 'nominal', confidence_level: 2, frp: 9.5,  satellite: 'VIIRS', acq_date: '2025-07-10' },
    ],
    count: 5,
    source: 'NASA FIRMS VIIRS SNPP NRT',
    region: 'NCR',
  });
}

export async function getStationPanel(stationId, lat, lng) {
  const mockPanelData = {
    station_id: stationId,
    station_name: 'Anand Vihar',
    current_aqi: 312,
    aqi_label: 'Severe',
    pm25: 145,
    pm10: 210,
    fingerprint: [
      { source_id: 's1', source_name: 'Badarpur Thermal Power Plant', source_type: 'thermal_plant', contribution_pct: 45 },
      { source_id: 's2', source_name: 'Okhla Industrial Area', source_type: 'industrial', contribution_pct: 35 },
      { source_id: 's4', source_name: 'ITO Traffic Corridor', source_type: 'traffic_corridor', contribution_pct: 15 },
    ],
    attribution_explanation: 'Prevailing westerly winds are carrying emissions from Badarpur Thermal Power Plant and Okhla Industrial Area directly towards this monitoring station, accounting for over 80% of the local particulate matter. Construction dust from Central Vista adds a background contribution during afternoon hours.',
    forecast_chart: Array.from({ length: 24 }).map((_, i) => {
      let baseAqi = 150;
      if ((i >= 8 && i <= 10) || (i >= 18 && i <= 21)) baseAqi += 100 + Math.random() * 50;
      else baseAqi += Math.random() * 30 - 15;
      return { hour: `${i.toString().padStart(2, '0')}:00`, aqi: Math.round(baseAqi) };
    }),
    forecast_trend: 'worsening — AQI rising over the past hours',
    forecast_narrative: 'Air quality is expected to worsen through the evening peak traffic hours, with AQI likely crossing 350 by 8 PM. Residents are strongly advised to limit outdoor exposure after 6 PM.',
    hindi_advisory: 'आज आनंद विहार में वायु प्रदूषण का स्तर अत्यंत गंभीर (AQI: 312) है। बच्चों और बुजुर्गों को बाहर जाने से बिल्कुल बचना चाहिए, और यदि आवश्यक हो तो N95 मास्क अवश्य पहनें। घर की खिड़कियाँ बंद रखें और एयर प्यूरीफायर का उपयोग करें।',
    english_advisory: 'SEVERE air pollution alert at Anand Vihar (AQI: 312). Stay indoors with windows and doors closed. Avoid all outdoor activities. Hospitals and schools should suspend outdoor programmes immediately.',
    harm: {
      children_exposed: 12500,
      patients_exposed: 3400,
      affected_zones: [
        { name: 'Delhi Public School', type: 'school', population: 2000 },
        { name: 'Max Super Speciality', type: 'hospital', population: 500 },
        { name: 'Vasant Vihar Old Age Home', type: 'old_age_home', population: 150 },
      ],
    },
    emissions: {
      total_co2_tonnes_today: 8450,
      trend: 'stable',
      insight_text: 'This is equivalent to 1,758,333 cars being driven across NCR today.',
      top_emitters: [
        { source_id: 's5', source_name: 'Dadri Thermal Plant', co2_tonnes: 3200, contribution_pct: 38 },
        { source_id: 's1', source_name: 'Badarpur Thermal', co2_tonnes: 2800, contribution_pct: 33 },
        { source_id: 's2', source_name: 'Okhla Industrial', co2_tonnes: 850, contribution_pct: 10 },
      ],
    },
    legal: {
      citizen_rights_text: 'Under the Air (Prevention and Control of Pollution) Act 1981 and the Environment Protection Act 1986, every citizen has a constitutionally protected right to a clean and healthy environment. You are legally empowered to demand accountability from any entity whose emissions violate prescribed ambient air quality standards.',
      complaint_guidance_text: 'File a formal complaint via the CPCB SAMEER app or through your State Pollution Control Board\'s online grievance portal. If unresolved after 60 days, petition the National Green Tribunal (NGT) under Section 14 of the NGT Act 2010 — no court fee is required.',
      notice_status: 'issued',
      relevant_authority: 'Central Pollution Control Board (CPCB)',
      disclaimer: 'This is general informational guidance only and does not constitute legal advice.',
    },
  };
  return fetchWithMockFallback(
    `/api/station-panel?station_id=${stationId}&lat=${lat}&lng=${lng}`,
    mockPanelData
  );
}

export async function generateNotice(sourceId) {
  if (USE_MOCK_DATA) {
    await delay(1500); // Simulate heavy PDF generation
    // Create a minimal valid blank PDF blob
    const base64Pdf = 'JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwogIC9QYWdlcyAyIDAgUgo+PgplbmRvYmoKCjIgMCBvYmoKPDwKICAvVHlwZSAvUGFnZXMKICAvTWVkaWFCb3ggWyAwIDAgMjAwIDIwMCBdCiAgL0NvdW50IDEKICAvS2lkcyBbIDMgMCBSIF0KPj4KZW5kb2JqCgozIDAgb2JqCjw8CiAgL1R5cGUgL1BhZ2UKICAvUGFyZW50IDIgMCBSCiAgL1Jlc291cmNlcyA8PAogICAgL0ZvbnQgPDwKICAgICAgL0YxIDQgMCBSCj4+Cj4+CiAgL0NvbnRlbnRzIDUgMCBSCj4+CmVuZG9iagoKNCAwIG9iago8PAogIC9UeXBlIC9Gb250CiAgL1N1YnR5cGUgL1R5cGUxCiAgL0Jhc2VGb250IC9UaW1lcy1Sb21hbgo+PgplbmRvYmoKCjUgMCBvYmoKPDwKICAvTGVuZ3RoIDIxPj4Kc3RyZWFtCkJUCjcwIDUwIFRECi9GMSAxMiBUZgooTW9jayBQREYpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDEwIDEwMDAwIG4gCjAwMDAwMDAwNjkgMTAwMDAgbiAKMDAwMDAwMDE0MSAxMDAwMCBuIAowMDAwMDAwMjQ5IDEwMDAwIG4gCjAwMDAwMDAzNDEgMTAwMDAgbiAKdHJhaWxlcgo8PAogIC9TaXplIDYKICAvUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNBE5CiUlRU9GCg==';
    const byteCharacters = atob(base64Pdf);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: 'application/pdf' });
  }
  const headers = {};
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`;
    }
  } catch (err) {
    console.warn("Could not retrieve Supabase session:", err);
  }

  const response = await fetch(`${API_URL}/api/generate-notice?source_id=${sourceId}`, {
    method: 'POST',
    headers
  });
  
  if (!response.ok) {
    throw new Error(`Failed to generate notice: ${response.status}`);
  }
  
  return response.blob();
}

export async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });
  if (error) throw error;
  return data;
}

export async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}
