export const mockStations = [
  { id: "delhi_anand_vihar", name: "Anand Vihar", lat: 28.6469, lng: 77.3162, aqi: 312, pm25: 145, pm10: 210, wind_speed: 3.2, wind_deg: 270, timestamp: new Date().toISOString() },
  { id: "delhi_rk_puram", name: "RK Puram", lat: 28.5651, lng: 77.1700, aqi: 178, pm25: 85, pm10: 120, wind_speed: 2.8, wind_deg: 265, timestamp: new Date().toISOString() },
  { id: "delhi_dwarka", name: "Dwarka", lat: 28.5921, lng: 77.0460, aqi: 145, pm25: 65, pm10: 95, wind_speed: 4.1, wind_deg: 280, timestamp: new Date().toISOString() },
  { id: "delhi_rohini", name: "Rohini", lat: 28.7495, lng: 77.1139, aqi: 267, pm25: 120, pm10: 180, wind_speed: 2.5, wind_deg: 250, timestamp: new Date().toISOString() },
  { id: "noida_sec62", name: "Noida Sec62", lat: 28.6270, lng: 77.3710, aqi: 289, pm25: 135, pm10: 195, wind_speed: 3.0, wind_deg: 275, timestamp: new Date().toISOString() },
  { id: "gurugram_vikas_sadan", name: "Gurugram", lat: 28.4595, lng: 77.0266, aqi: 198, pm25: 95, pm10: 140, wind_speed: 3.5, wind_deg: 260, timestamp: new Date().toISOString() },
  { id: "delhi_okhla", name: "Okhla", lat: 28.5355, lng: 77.2637, aqi: 334, pm25: 155, pm10: 230, wind_speed: 2.1, wind_deg: 240, timestamp: new Date().toISOString() },
  { id: "delhi_punjabi_bagh", name: "Punjabi Bagh", lat: 28.6663, lng: 77.1313, aqi: 201, pm25: 98, pm10: 145, wind_speed: 2.9, wind_deg: 270, timestamp: new Date().toISOString() }
];

export const mockSources = [
  { id: "s1", name: "Badarpur Thermal Power Plant", type: "thermal_plant", lat: 28.5042, lng: 77.3060, address: "Badarpur", activity_level: "high" },
  { id: "s2", name: "Okhla Industrial Area", type: "industrial", lat: 28.5300, lng: 77.2750, address: "Okhla", activity_level: "high" },
  { id: "s3", name: "Noida Sector 63 Construction", type: "construction", lat: 28.6250, lng: 77.3850, address: "Noida", activity_level: "medium" },
  { id: "s4", name: "ITO Traffic Corridor", type: "traffic_corridor", lat: 28.6288, lng: 77.2410, address: "ITO", activity_level: "high" },
  { id: "s5", name: "Dadri Thermal Plant", type: "thermal_plant", lat: 28.5721, lng: 77.5815, address: "Dadri", activity_level: "high" },
  { id: "s6", name: "Bawana Industrial Area", type: "industrial", lat: 28.7900, lng: 77.0500, address: "Bawana", activity_level: "medium" },
  { id: "s7", name: "NH-8 Traffic", type: "traffic_corridor", lat: 28.4980, lng: 77.0900, address: "Gurugram NH-8", activity_level: "high" },
  { id: "s8", name: "Faridabad Industrial Sector", type: "industrial", lat: 28.3800, lng: 77.3200, address: "Faridabad", activity_level: "high" },
  { id: "s9", name: "Central Secretariat Construction", type: "construction", lat: 28.6140, lng: 77.2000, address: "Central Vista", activity_level: "low" },
  { id: "s10", name: "Kirti Nagar Timber Market", type: "industrial", lat: 28.6500, lng: 77.1350, address: "Kirti Nagar", activity_level: "medium" },
  { id: "s11", name: "Anand Vihar ISBT", type: "traffic_corridor", lat: 28.6475, lng: 77.3150, address: "Anand Vihar", activity_level: "high" },
  { id: "s12", name: "Dwarka Expressway Construction", type: "construction", lat: 28.5500, lng: 76.9900, address: "Dwarka", activity_level: "high" }
];

export const mockAttribution = {
  fingerprint: [
    { source_id: "s1", source_name: "Badarpur Thermal Power Plant", contribution_pct: 45 },
    { source_id: "s2", source_name: "Okhla Industrial Area", contribution_pct: 35 },
    { source_id: "s4", source_name: "ITO Traffic Corridor", contribution_pct: 15 },
    { source_id: "s3", source_name: "Noida Sector 63 Construction", contribution_pct: 5 }
  ],
  explanation: "Prevailing westerly winds are carrying emissions from Badarpur and Okhla directly towards this monitoring station, accounting for 80% of the local particulate matter."
};

// Generate 24 hours of forecast data
export const mockForecast = Array.from({ length: 24 }).map((_, i) => {
  let baseAqi = 150;
  if ((i >= 8 && i <= 10) || (i >= 18 && i <= 21)) {
    baseAqi += 100 + Math.random() * 50; // Peak hours
  } else {
    baseAqi += Math.random() * 30 - 15; // Off-peak
  }
  return {
    hour: `${i.toString().padStart(2, '0')}:00`,
    aqi: Math.round(baseAqi)
  };
});

export const mockHarmScore = {
  harm_score: 4.2,
  children_exposed: 12500,
  patients_exposed: 3400,
  affected_zones: [
    { name: "Delhi Public School", type: "school", population: 2000 },
    { name: "Max Super Speciality", type: "hospital", population: 500 },
    { name: "Vasant Vihar Old Age Home", type: "old_age_home", population: 150 }
  ]
};

export const mockLegalAdvisory = {
  citizen_rights_text: "Under the Air (Prevention and Control of Pollution) Act 1981 and the Environment Protection Act 1986, citizens have a fundamental right to a clean environment. You are legally empowered to seek accountability for hazardous emissions affecting your health and locality.",
  complaint_guidance_text: "You can officially register a complaint using the CPCB SAMEER application or through your State Pollution Control Board's grievance portal. If the issue persists without resolution, it can be escalated to the National Green Tribunal (NGT) for further intervention.",
  notice_status: "issued",
  relevant_authority: "Central Pollution Control Board (CPCB)",
  disclaimer: "This is general informational guidance only and does not constitute legal advice."
};

export const mockViolationHistory = {
  source_id: "s5",
  source_name: "Dadri Thermal Plant",
  total_notices: 4,
  repeat_offender: true,
  notices: [
    { generated_at: new Date(Date.now() - 86400000 * 2).toISOString(), contribution_pct: 52.3, people_exposed: 24000 },
    { generated_at: new Date(Date.now() - 86400000 * 15).toISOString(), contribution_pct: 48.1, people_exposed: 21500 },
    { generated_at: new Date(Date.now() - 86400000 * 45).toISOString(), contribution_pct: 55.6, people_exposed: 26000 },
    { generated_at: new Date(Date.now() - 86400000 * 90).toISOString(), contribution_pct: 61.0, people_exposed: 28500 }
  ]
};

export const mockRepeatOffenders = {
  offenders: [
    { source_id: "s5", source_name: "Dadri Thermal Plant", notice_count: 4, last_notice_at: new Date(Date.now() - 86400000 * 2).toISOString() },
    { source_id: "s2", source_name: "Okhla Industrial Area", notice_count: 3, last_notice_at: new Date(Date.now() - 86400000 * 5).toISOString() },
    { source_id: "s8", source_name: "Faridabad Industrial Sector", notice_count: 2, last_notice_at: new Date(Date.now() - 86400000 * 12).toISOString() }
  ]
};

export const mockEmissions = {
  co2_kg_today: 450000,
  co2_tonnes_today: 450,
  equivalent_trees_needed: 21400
};

export const mockEmissionsSummary = {
  total_co2_tonnes_today: 8450,
  trend: "+5% vs yesterday",
  insight_text: "Thermal power generation accounts for 65% of today's CO2 emissions in the NCR region.",
  top_emitters: [
    { name: "Dadri Thermal Plant", tonnes: 3200 },
    { name: "Badarpur Thermal", tonnes: 2800 },
    { name: "Okhla Industrial", tonnes: 850 },
    { name: "Bawana Industrial", tonnes: 600 },
    { name: "Faridabad Sector", tonnes: 450 }
  ]
};

export const mockAccountabilityFeed = {
  worst_offender: { source_name: "Dadri Thermal Plant", contribution_pct: 62.4, people_exposed: 34500 },
  summary_text: "TODAY'S WORST OFFENDER: Dadri Thermal Plant — 62.4% contribution — 34,500 people exposed"
};

export const mockVulnerableZones = [
  { id: "z1", name: "Delhi Public School", type: "school", lat: 28.5821, lng: 77.0560, population: 2000 },
  { id: "z2", name: "Max Super Speciality", type: "hospital", lat: 28.5255, lng: 77.2137, population: 500 },
  { id: "z3", name: "Vasant Vihar Old Age Home", type: "old_age_home", lat: 28.5551, lng: 77.1600, population: 150 },
  { id: "z4", name: "AIIMS New Delhi", type: "hospital", lat: 28.5672, lng: 77.2100, population: 4500 },
  { id: "z5", name: "Modern School Barakhamba", type: "school", lat: 28.6280, lng: 77.2250, population: 2500 }
];
