import { 
  mockStations, 
  mockSources, 
  mockAttribution, 
  mockForecast, 
  mockHarmScore, 
  mockLegalAdvisory, 
  mockViolationHistory, 
  mockRepeatOffenders, 
  mockEmissions, 
  mockEmissionsSummary, 
  mockAccountabilityFeed,
  mockVulnerableZones
} from '../mockData/mock';

const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function fetchWithMockFallback(endpoint, mockData) {
  if (USE_MOCK_DATA) {
    await delay(600); // Simulate network latency
    return mockData;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`);
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

export async function getHarmScore(lat, lng, radiusKm = 2.0) {
  return fetchWithMockFallback(`/api/harm-score?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`, mockHarmScore);
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

  const response = await fetch(`${API_URL}/api/generate-notice?source_id=${sourceId}`, {
    method: 'POST'
  });
  
  if (!response.ok) {
    throw new Error(`Failed to generate notice: ${response.status}`);
  }
  
  return response.blob();
}
