import React, { useState, useEffect } from 'react';
import { 
  getStations, 
  getSources, 
  getForecast, 
  getAccountabilityFeed,
  getVulnerableZones
} from '../api/client';
import { 
  mockStations, 
  mockSources, 
  mockForecast, 
  mockAccountabilityFeed,
  mockVulnerableZones
} from '../mockData/mock';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  ResponsiveContainer, 
  Tooltip 
} from 'recharts';
import { 
  ShieldAlert, 
  Bell, 
  MapPin, 
  Clock, 
  AlertTriangle, 
  FileText, 
  Award, 
  PlusCircle, 
  HeartPulse, 
  PhoneCall, 
  Wind, 
  ArrowRight,
  Sparkles,
  CheckCircle2,
  X,
  Scale,
  Compass,
  FileCheck2,
  Info
} from 'lucide-react';

export default function CitizenDashboard({ onViewSwitch }) {
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState(null);
  const [sources, setSources] = useState([]);
  const [zones, setZones] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [feed, setFeed] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Interactive Modals State
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [isWardOpen, setIsWardOpen] = useState(false);
  const [isHealthOpen, setIsHealthOpen] = useState(false);
  const [healthLang, setHealthLang] = useState('en'); // 'en' or 'hi'
  const [reportSubmitted, setReportSubmitted] = useState(false);
  const [reportForm, setReportForm] = useState({
    title: '',
    description: '',
    sourceType: 'industrial',
    location: ''
  });

  useEffect(() => {
    const loadData = async () => {
      let stData = [];
      let srcData = [];
      let feedData = null;
      let zoneData = [];

      try {
        stData = await getStations();
      } catch (err) {
        console.warn("getStations failed, using mock data", err);
        stData = mockStations;
      }

      try {
        srcData = await getSources();
      } catch (err) {
        console.warn("getSources failed, using mock data", err);
        srcData = mockSources;
      }

      try {
        feedData = await getAccountabilityFeed();
      } catch (err) {
        console.warn("getAccountabilityFeed failed, using mock data", err);
        feedData = mockAccountabilityFeed;
      }

      try {
        zoneData = await getVulnerableZones();
      } catch (err) {
        console.warn("getVulnerableZones failed, using mock data", err);
        zoneData = mockVulnerableZones;
      }

      // If data is empty, fall back to mock
      if (!Array.isArray(stData) || stData.length === 0) {
        stData = mockStations;
      }
      if (!Array.isArray(srcData) || srcData.length === 0) {
        srcData = mockSources;
      }
      if (!feedData) {
        feedData = mockAccountabilityFeed;
      }
      if (!Array.isArray(zoneData) || zoneData.length === 0) {
        zoneData = mockVulnerableZones;
      }

      setStations(stData);
      setSources(srcData);
      setFeed(feedData);
      setZones(zoneData);
      
      const defaultSt = stData.find(s => s.id === 'delhi_rk_puram') || stData[0];
      setSelectedStation(defaultSt);
      setLoading(false);
    };
    
    loadData();
  }, []);

  // Fetch forecast whenever selected station changes
  useEffect(() => {
    if (selectedStation) {
      getForecast(selectedStation.id)
        .then(setForecast)
        .catch((err) => {
          console.warn("Failed to fetch forecast, using mock", err);
          setForecast(mockForecast);
        });
    }
  }, [selectedStation]);

  if (loading || !selectedStation) {
    return (
      <div className="min-h-screen bg-background flex flex-col justify-center items-center gap-4">
        <div className="w-10 h-10 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        <p className="text-secondary font-bold text-xs uppercase tracking-wider animate-pulse">Loading Citizen Portal...</p>
      </div>
    );
  }

  const aqi = selectedStation.aqi;
  let aqiTheme = {
    class: 'from-green-100 to-green-200 text-green-800 border-green-300',
    status: 'Excellent',
    desc: 'The air quality is ideal for most individuals; enjoy your outdoor activities.',
    risk: 'Low',
    riskText: 'Minimal risk of respiratory irritation for sensitive groups.',
    exercise: '06:00 AM - 10:00 AM',
    exerciseDesc: 'Low pollution window',
    iconColor: 'text-green-700',
    indicatorBorder: 'border-green-600'
  };

  if (aqi > 50 && aqi <= 100) {
    aqiTheme = {
      class: 'from-yellow-100 to-yellow-200 text-yellow-800 border-yellow-300',
      status: 'Moderate',
      desc: 'Air quality is acceptable; however, sensitive groups may experience minor irritation.',
      risk: 'Moderate',
      riskText: 'Sensitive individuals should limit prolonged outdoor exertion.',
      exercise: '07:00 AM - 09:30 AM',
      exerciseDesc: 'Acceptable pollution window',
      iconColor: 'text-yellow-700',
      indicatorBorder: 'border-yellow-600'
    };
  } else if (aqi > 100 && aqi <= 200) {
    aqiTheme = {
      class: 'from-orange-100 to-orange-200 text-orange-800 border-orange-300',
      status: 'Poor',
      desc: 'Particulate levels are elevated. Avoid long outdoor sessions.',
      risk: 'High',
      riskText: 'Increased risk of throat irritation and breathing difficulty.',
      exercise: '08:00 AM - 09:30 AM',
      exerciseDesc: 'Limited exposure window',
      iconColor: 'text-orange-700',
      indicatorBorder: 'border-orange-600'
    };
  } else if (aqi > 200) {
    aqiTheme = {
      class: 'from-red-100 to-red-200 text-red-800 border-red-300',
      status: 'Severe',
      desc: 'Air quality is hazardous. Active children and adults, and people with respiratory disease, should avoid outdoor exertion.',
      risk: 'Critical',
      riskText: 'High risk of severe irritation. Remain indoors with air purifiers active.',
      exercise: 'Avoid Outdoors',
      exerciseDesc: 'Use indoor purification',
      iconColor: 'text-red-700',
      indicatorBorder: 'border-red-600'
    };
  }

  const localSources = sources.slice(0, 2);

  const handleReportSubmit = (e) => {
    e.preventDefault();
    setReportSubmitted(true);
    setTimeout(() => {
      setIsReportOpen(false);
      setReportSubmitted(false);
      setReportForm({ title: '', description: '', sourceType: 'industrial', location: '' });
    }, 2000);
  };

  // Find institutions close to the selected station
  const nearbyInstitutions = zones.filter(z => 
    Math.abs(z.lat - selectedStation.lat) < 0.08 && 
    Math.abs(z.lng - selectedStation.lng) < 0.08
  );

  return (
    <div className="min-h-screen bg-background text-on-surface flex flex-col font-sans">
      {/* Top Header Bar */}
      <header className="fixed top-0 w-full h-16 border-b border-outline-variant bg-white flex justify-between items-center px-6 z-30 flex-shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-xl font-bold tracking-tight text-primary">VayuSetu</span>
        </div>
        
        <nav className="hidden md:flex items-center gap-6">
          <button className="text-primary font-bold border-b-2 border-primary pb-1 text-xs tracking-wider">Dashboard</button>
          <button onClick={() => setIsWardOpen(true)} className="text-secondary hover:text-primary transition-colors text-xs tracking-wider font-semibold">My Ward</button>
          <button onClick={() => setIsHealthOpen(true)} className="text-secondary hover:text-primary transition-colors text-xs tracking-wider font-semibold">Health Guide</button>
          <button onClick={() => setIsReportOpen(true)} className="text-secondary hover:text-primary transition-colors text-xs tracking-wider font-semibold">Report Concern</button>
        </nav>
        
        <div className="flex items-center gap-3">
          {/* Ward selector */}
          <div className="relative">
            <MapPin className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-primary" />
            <select 
              value={selectedStation.id}
              onChange={(e) => {
                const match = stations.find(s => s.id === e.target.value);
                if (match) setSelectedStation(match);
              }}
              className="bg-surface-container-low border-none rounded-full pl-8 pr-8 py-1 text-xs focus:ring-2 focus:ring-primary text-on-surface font-semibold cursor-pointer appearance-none"
            >
              {stations.map(st => (
                <option key={st.id} value={st.id}>{st.name}</option>
              ))}
            </select>
          </div>
          
          <button className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-surface-container-low transition-colors text-on-surface-variant relative">
            <Bell className="w-4 h-4" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full"></span>
          </button>
          
          <button 
            onClick={() => onViewSwitch('authority')}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-primary text-primary hover:bg-primary hover:text-white transition-all text-xs font-bold uppercase tracking-wider"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Portal View</span>
          </button>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-grow pt-24 pb-12 px-6 max-w-7xl mx-auto w-full space-y-6">
        
        {/* Welcome Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Good Morning, Citizen</h1>
            <p className="text-xs text-secondary font-medium">Monitoring {selectedStation.name} Ward • Updated 2 mins ago</p>
          </div>
          
          <div className="flex gap-2 sm:hidden w-full">
            <button 
              onClick={() => setIsWardOpen(true)}
              className="flex-1 bg-surface-container-high text-on-surface border border-outline-variant/30 text-xs font-bold py-2 rounded-lg transition-all"
            >
              My Ward
            </button>
            <button 
              onClick={() => setIsHealthOpen(true)}
              className="flex-1 bg-surface-container-high text-on-surface border border-outline-variant/30 text-xs font-bold py-2 rounded-lg transition-all"
            >
              Health Guide
            </button>
            <button 
              onClick={() => setIsReportOpen(true)}
              className="flex-1 bg-primary text-white text-xs font-bold py-2 rounded-lg hover:brightness-110 transition-all flex items-center justify-center gap-1"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Report</span>
            </button>
          </div>
        </div>
        
        {/* Bento Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* Left Column (8/12 grid span) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* AQI Gradient Hero Card */}
            <div className={`bg-gradient-to-br ${aqiTheme.class} rounded-2xl p-6 flex flex-col md:flex-row items-center gap-6 shadow-sm border border-outline-variant/20`}>
              <div className="flex-grow text-center md:text-left">
                <span className="px-2.5 py-1 bg-white/40 rounded-full text-[10px] font-bold inline-block mb-3 uppercase tracking-wider text-secondary">Current Air Quality</span>
                <div className="flex items-baseline gap-1 justify-center md:justify-start">
                  <span className="text-6xl font-black leading-none tracking-tighter">{selectedStation.aqi}</span>
                  <span className="text-xs font-bold opacity-80 uppercase tracking-widest">AQI</span>
                </div>
                <h2 className="text-xl font-extrabold mt-3">Status: {aqiTheme.status}</h2>
                <p className="text-xs mt-1.5 opacity-90 leading-relaxed max-w-md">{aqiTheme.desc}</p>
              </div>
              
              <div className="w-full md:w-56 aspect-square glass-panel rounded-2xl flex flex-col justify-center items-center p-5 text-on-surface text-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-3">
                  <HeartPulse className="w-6 h-6 text-primary" />
                </div>
                <p className="font-bold text-sm">Outdoor Activity</p>
                <p className="text-[11px] text-secondary mt-1 leading-normal">
                  {aqiTheme.risk === 'Low' ? 'No health restrictions needed today.' : `Caution: air is ${aqiTheme.risk.toLowerCase()} risk for asthma patients.`}
                </p>
              </div>
            </div>
            
            {/* Bento cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Local Context */}
              <div className="bg-white border border-outline-variant rounded-xl p-5 shadow-soft flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-sm font-bold flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-primary" />
                      <span>Local Context</span>
                    </h3>
                    <button onClick={() => onViewSwitch('authority')} className="text-xs text-primary font-bold hover:underline">View Map</button>
                  </div>
                  
                  <div className="space-y-3">
                    {localSources.map((src, i) => (
                      <div key={src.id} className="flex items-start gap-3 p-3 bg-surface-container-low rounded-lg border border-outline-variant/30">
                        <div className="w-2.5 h-2.5 rounded-full bg-tertiary mt-1"></div>
                        <div>
                          <p className="font-bold text-xs">{src.name}</p>
                          <p className="text-[10px] text-secondary mt-0.5">{src.type.replace('_', ' ')} • Active emissions tracking</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Safe Times & Risk Indicator */}
              <div className="grid grid-rows-2 gap-6">
                {/* Safe Exercise Card */}
                <div className="bg-primary-container text-on-primary-container p-5 rounded-xl flex items-center justify-between overflow-hidden relative shadow-soft border border-primary/20">
                  <div className="z-10">
                    <span className="text-[9px] font-bold opacity-80 uppercase tracking-widest">Optimal Exercise Time</span>
                    <p className="text-base font-extrabold mt-0.5">{aqiTheme.exercise}</p>
                    <p className="text-[10px] opacity-90 mt-0.5">{aqiTheme.exerciseDesc}</p>
                  </div>
                  <Clock className="w-16 h-16 opacity-10 absolute -right-3 -bottom-3 rotate-12" />
                </div>
                
                {/* Health Risk Indicator */}
                <div className="bg-white border border-outline-variant p-5 rounded-xl flex items-center gap-4 shadow-soft">
                  <div className={`w-12 h-12 rounded-full border-4 ${aqiTheme.indicatorBorder} flex items-center justify-center text-xs font-bold shrink-0`}>
                    {aqiTheme.risk}
                  </div>
                  <div>
                    <h4 className="font-bold text-xs">Ward Health Risk</h4>
                    <p className="text-[10px] text-secondary mt-0.5 leading-relaxed">{aqiTheme.riskText}</p>
                  </div>
                </div>
              </div>
              
            </div>
            
            {/* Forecast Chart */}
            <div className="bg-white border border-outline-variant p-5 rounded-xl shadow-soft">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-sm text-on-surface">Hourly Pollution Trend</h3>
                <span className="text-[10px] font-bold text-secondary uppercase flex items-center gap-1">
                  <span className="w-2.5 h-2.5 bg-primary rounded-full"></span> AQI Level
                </span>
              </div>
              
              {forecast && forecast.length > 0 ? (
                <div className="h-36 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={forecast.slice(0, 12)} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
                      <XAxis 
                        dataKey="hour" 
                        stroke="#737686" 
                        fontSize={9} 
                        axisLine={false} 
                        tickLine={false} 
                        tickMargin={8}
                      />
                      <YAxis 
                        stroke="#737686" 
                        fontSize={9} 
                        axisLine={false} 
                        tickLine={false} 
                      />
                      <Tooltip 
                        cursor={{ fill: 'rgba(0, 0, 0, 0.02)' }}
                        contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e0e3e5', color: '#191c1e', borderRadius: '8px', fontSize: '11px' }}
                      />
                      <Bar dataKey="aqi" fill="#004ac6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-36 bg-surface-container-low rounded-lg animate-pulse"></div>
              )}
            </div>
            
          </div>
          
          {/* Right Column (4/12 grid span): Accountability timeline */}
          <aside className="lg:col-span-4 flex flex-col">
            <div className="bg-surface-container-high p-5 rounded-xl border border-outline-variant shadow-soft flex-grow flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-on-surface mb-5 flex items-center gap-2 border-b border-outline-variant/30 pb-3">
                  <ShieldAlert className="w-4 h-4 text-primary" />
                  <span>Transparency & Action</span>
                </h3>
                
                {/* Worst Polluter card */}
                {feed && (
                  <div className="bg-white p-4 rounded-xl border border-outline-variant shadow-sm border-l-4 border-error mb-6">
                    <span className="text-[9px] font-bold text-error uppercase tracking-wider">Today's Worst Offender</span>
                    <p className="font-extrabold text-sm text-on-surface mt-1 truncate">{feed.worst_offender.source_name}</p>
                    
                    <div className="flex items-center gap-2 mt-2.5">
                      <div className="flex-grow h-1.5 bg-surface-container-low rounded-full overflow-hidden">
                        <div className="bg-error h-full" style={{ width: `${feed.worst_offender.contribution_pct}%` }}></div>
                      </div>
                      <span className="text-[10px] font-bold text-secondary font-mono">{feed.worst_offender.contribution_pct}%</span>
                    </div>
                    
                    <p className="text-[11px] text-on-surface-variant mt-2 leading-relaxed">
                      Emissions contributing to local particulate thresholds, affecting <span className="font-bold text-on-surface">{Number(feed.worst_offender.people_exposed).toLocaleString()}+ residents</span>.
                    </p>
                  </div>
                )}
                
                {/* Timeline list */}
                <div className="space-y-5">
                  <div className="flex gap-3 items-start">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold">Official Notice Dispatched</p>
                      <p className="text-[11px] text-secondary mt-0.5 leading-relaxed">Legal notice sent to Badarpur power plant demanding secondary emission scrubbing reports.</p>
                      <span className="text-[10px] text-outline font-semibold mt-1 block">45 mins ago</span>
                    </div>
                  </div>
                  
                  <div className="flex gap-3 items-start">
                    <div className="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-secondary shrink-0 border border-outline-variant/30">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold font-semibold">Compliance Report Received</p>
                      <p className="text-[11px] text-secondary mt-0.5 leading-relaxed">Noida Sector 63 Construction site submitted dust control reports (mist cannons active).</p>
                      <span className="text-[10px] text-outline font-semibold mt-1 block">3 hours ago</span>
                    </div>
                  </div>
                  
                  <div className="flex gap-3 items-start">
                    <div className="w-8 h-8 rounded-full bg-tertiary/10 flex items-center justify-center text-tertiary shrink-0">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold font-semibold">Citizen Rerouting Success</p>
                      <p className="text-[11px] text-secondary mt-0.5 leading-relaxed">Traffic diversion near schools during peak times approved based on ward sensor alerts.</p>
                      <span className="text-[10px] text-outline font-semibold mt-1 block">6 hours ago</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <button 
                onClick={() => setIsReportOpen(true)}
                className="w-full mt-8 py-2.5 bg-primary text-white text-xs font-bold rounded-lg shadow-sm hover:brightness-110 active:scale-95 transition-all flex items-center justify-center gap-1.5"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Report Violation</span>
              </button>
            </div>
          </aside>
          
        </div>
        
        {/* Community Resources */}
        <section className="pt-6">
          <h3 className="font-bold text-base text-on-surface mb-4">Community Resources</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Health Center */}
            <div className="bg-white border border-outline-variant p-4 rounded-xl hover:bg-surface-container-low transition-colors shadow-soft group flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                    <HeartPulse className="w-5 h-5" />
                  </div>
                  <span className="text-[9px] px-2 py-0.5 bg-green-100 text-green-700 rounded-full font-bold uppercase">Open</span>
                </div>
                <h4 className="font-bold text-xs text-on-surface">City Health Center</h4>
                <p className="text-[10px] text-secondary mt-0.5">Equipped with active HEPA air filtration safety rooms.</p>
              </div>
              <div className="mt-4 flex items-center justify-between text-primary font-bold text-[10px]">
                <span>0.8 km away</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
            
            {/* Helpline */}
            <div className="bg-white border border-outline-variant p-4 rounded-xl hover:bg-surface-container-low transition-colors shadow-soft group flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center text-error">
                    <PhoneCall className="w-5 h-5" />
                  </div>
                  <span className="text-[9px] px-2 py-0.5 bg-red-100 text-error rounded-full font-bold uppercase">24 Hours</span>
                </div>
                <h4 className="font-bold text-xs text-on-surface">Asthma Helpline</h4>
                <p className="text-[10px] text-secondary mt-0.5">Rapid advice and nebulizer response support team.</p>
              </div>
              <div className="mt-4 flex items-center justify-between text-error font-bold text-[10px]">
                <span>1800-425-VAYU</span>
                <PhoneCall className="w-3.5 h-3.5" />
              </div>
            </div>
            
            {/* Air Hubs */}
            <div className="bg-white border border-outline-variant p-4 rounded-xl hover:bg-surface-container-low transition-colors shadow-soft group flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                    <Wind className="w-5 h-5" />
                  </div>
                </div>
                <h4 className="font-bold text-xs text-on-surface">Citizen Air Hubs</h4>
                <p className="text-[10px] text-secondary mt-0.5">Purified indoor environments and ward warning hubs.</p>
              </div>
              <div className="mt-4 flex items-center justify-between text-primary font-bold text-[10px]">
                <span>3 Locations</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
            
            {/* Masks */}
            <div className="bg-white border border-outline-variant p-4 rounded-xl hover:bg-surface-container-low transition-colors shadow-soft group flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-secondary">
                    <FileText className="w-5 h-5" />
                  </div>
                  <span className="text-[9px] px-2 py-0.5 bg-primary-container/20 text-primary rounded-full font-bold uppercase font-bold">Free</span>
                </div>
                <h4 className="font-bold text-xs text-on-surface">N95 Mask Points</h4>
                <p className="text-[10px] text-secondary mt-0.5">Pick up free N95 filtration masks at your ward office.</p>
              </div>
              <div className="mt-4 flex items-center justify-between text-secondary font-bold text-[10px]">
                <span>Ward Office 142</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
            
          </div>
        </section>
        
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-outline-variant py-8 px-6 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-center md:text-left">
            <span className="font-bold text-primary text-base">VayuSetu</span>
            <p className="text-xs text-secondary mt-0.5">Empowering citizens through environmental transparency.</p>
          </div>
          <div className="flex gap-6 text-[11px] text-secondary font-bold uppercase tracking-wider">
            <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-primary transition-colors">Terms of Use</a>
            <a href="#" className="hover:text-primary transition-colors">Data Sources</a>
            <button onClick={() => onViewSwitch('authority')} className="hover:text-primary transition-colors">Admin Portal</button>
          </div>
          <div className="text-[10px] text-outline">
            © 2024 VayuSetu Urban Intelligence
          </div>
        </div>
      </footer>

      {/* MY WARD DETAILS MODAL */}
      {isWardOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center z-50 p-4">
          <div className="bg-white border border-outline-variant shadow-lg rounded-2xl max-w-lg w-full overflow-hidden p-6 relative">
            <button 
              onClick={() => setIsWardOpen(false)}
              className="absolute top-4 right-4 text-secondary hover:text-on-surface"
            >
              <X className="w-5 h-5" />
            </button>
            
            <div className="space-y-4">
              <div className="border-b border-outline-variant/30 pb-3">
                <h3 className="text-sm font-bold text-on-surface uppercase tracking-wider flex items-center gap-1.5">
                  <Compass className="w-4 h-4 text-primary" />
                  <span>My Ward Profile: {selectedStation.name}</span>
                </h3>
                <p className="text-[10px] text-secondary mt-0.5">Local impact index and vulnerable receptors inside this ward.</p>
              </div>

              <div className="grid grid-cols-2 gap-4 bg-surface-container-low p-4 rounded-xl border border-outline-variant/30">
                <div>
                  <span className="text-[10px] text-secondary font-bold uppercase">Current Ward AQI</span>
                  <div className="text-2xl font-black text-primary mt-1">{selectedStation.aqi}</div>
                  <span className="text-[10px] text-secondary font-medium">Status: {aqiTheme.status}</span>
                </div>
                <div>
                  <span className="text-[10px] text-secondary font-bold uppercase">Associated Health Index</span>
                  <div className="text-2xl font-black text-tertiary mt-1">4.2 / 5.0</div>
                  <span className="text-[10px] text-secondary font-medium">Active warning indicators</span>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-xs text-on-surface flex items-center gap-1.5">
                  <HeartPulse className="w-3.5 h-3.5 text-primary" />
                  <span>Nearby Vulnerable Receptors ({nearbyInstitutions.length})</span>
                </h4>
                {nearbyInstitutions.length === 0 ? (
                  <p className="text-[11px] text-secondary italic">No institutions mapped in immediate downwind proximity.</p>
                ) : (
                  <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                    {nearbyInstitutions.map((ins, i) => (
                      <div key={i} className="flex justify-between items-center bg-surface-container-low p-2.5 rounded-lg border border-outline-variant/20 text-xs">
                        <div>
                          <span className="font-semibold text-on-surface">{ins.name}</span>
                          <p className="text-[10px] text-secondary mt-0.5 uppercase">{ins.type.replace('_', ' ')}</p>
                        </div>
                        <span className="bg-primary/10 text-primary px-2.5 py-0.5 rounded text-[10px] font-bold">Pop: {ins.population}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-outline-variant/30 flex justify-end">
                <button 
                  onClick={() => setIsWardOpen(false)}
                  className="bg-primary text-white text-xs font-bold py-2 px-4 rounded-lg uppercase tracking-wider hover:brightness-110 transition-all"
                >
                  Close Profile
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* HEALTH GUIDE MODAL (ENGLISH / HINDI) */}
      {isHealthOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center z-50 p-4">
          <div className="bg-white border border-outline-variant shadow-lg rounded-2xl max-w-lg w-full overflow-hidden p-6 relative">
            <button 
              onClick={() => setIsHealthOpen(false)}
              className="absolute top-4 right-4 text-secondary hover:text-on-surface"
            >
              <X className="w-5 h-5" />
            </button>
            
            <div className="space-y-4">
              <div className="border-b border-outline-variant/30 pb-3 flex justify-between items-center pr-8">
                <div>
                  <h3 className="text-sm font-bold text-on-surface uppercase tracking-wider flex items-center gap-1.5">
                    <FileCheck2 className="w-4 h-4 text-primary" />
                    <span>Health Advisory & Guide</span>
                  </h3>
                  <p className="text-[10px] text-secondary mt-0.5">Pediatric and elderly health care guidelines.</p>
                </div>
                
                {/* Language Switcher */}
                <div className="flex bg-surface-container-high rounded-lg p-0.5 text-xs">
                  <button 
                    onClick={() => setHealthLang('en')}
                    className={`px-2 py-0.5 rounded font-bold transition-all ${healthLang === 'en' ? 'bg-primary text-white' : 'text-secondary'}`}
                  >
                    EN
                  </button>
                  <button 
                    onClick={() => setHealthLang('hi')}
                    className={`px-2 py-0.5 rounded font-bold transition-all ${healthLang === 'hi' ? 'bg-primary text-white' : 'text-secondary'}`}
                  >
                    HI
                  </button>
                </div>
              </div>

              {healthLang === 'en' ? (
                <div className="space-y-3.5 text-xs leading-relaxed">
                  <div className="bg-primary/5 p-3 rounded-lg border border-primary/20">
                    <h4 className="font-bold text-primary flex items-center gap-1.5 mb-1 text-xs">
                      <Info className="w-4 h-4 shrink-0" />
                      <span>General Advisory</span>
                    </h4>
                    <p className="text-[11px] text-on-surface-variant">
                      Active AQI index suggests caution. Sensitive residents should reduce heavy prolonged outdoor exercise, especially near high-traffic intersections. Keep windows closed during early mornings.
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between border-b border-outline-variant/20 pb-1 text-[11px]">
                      <span className="font-bold text-on-surface">Exercise/Jogging</span>
                      <span className="text-secondary">Avoid peak morning traffic hours (07:00 AM - 10:00 AM)</span>
                    </div>
                    <div className="flex justify-between border-b border-outline-variant/20 pb-1 text-[11px]">
                      <span className="font-bold text-on-surface">Asthma Patients</span>
                      <span className="text-secondary">Keep nebulizers handy, use N95 respirators outdoors</span>
                    </div>
                    <div className="flex justify-between border-b border-outline-variant/20 pb-1 text-[11px]">
                      <span className="font-bold text-on-surface">Children/Schools</span>
                      <span className="text-secondary">Restrict outdoor sports activities when AQI exceeds 200</span>
                    </div>
                  </div>
                  
                  <div className="bg-red-50 p-3 rounded-lg border border-red-200 text-error flex items-start gap-2.5">
                    <PhoneCall className="w-5 h-5 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-xs">Emergency Helpline Contact</p>
                      <p className="text-[10px] mt-0.5">Call <b>1800-425-VAYU</b> or go directly to the nearest City Health Center for respiratory discomfort.</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-3.5 text-xs leading-relaxed font-sans">
                  <div className="bg-primary/5 p-3 rounded-lg border border-primary/20">
                    <h4 className="font-bold text-primary flex items-center gap-1.5 mb-1 text-xs">
                      <Info className="w-4 h-4 shrink-0" />
                      <span>सामान्य स्वास्थ्य परामर्श</span>
                    </h4>
                    <p className="text-[11px] text-on-surface-variant">
                      सक्रिय वायु गुणवत्ता सूचकांक (AQI) सावधानी बरतने का संकेत देता है। संवेदनशील निवासियों को भारी शारीरिक परिश्रम को कम करना चाहिए, विशेषकर व्यस्त चौराहों के समीप। सुबह के समय खिड़कियाँ बंद रखें।
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between border-b border-outline-variant/20 pb-1 text-[11px]">
                      <span className="font-bold text-on-surface">व्यायाम / दौड़</span>
                      <span className="text-secondary">सुबह के व्यस्त समय (07:00 AM - 10:00 AM) में बाहर जाने से बचें</span>
                    </div>
                    <div className="flex justify-between border-b border-outline-variant/20 pb-1 text-[11px]">
                      <span className="font-bold text-on-surface">अस्थमा के रोगी</span>
                      <span className="text-secondary">नेबुलाइज़र साथ रखें, बाहर जाते समय N95 मास्क पहनें</span>
                    </div>
                    <div className="flex justify-between border-b border-outline-variant/20 pb-1 text-[11px]">
                      <span className="font-bold text-on-surface">बच्चे / विद्यालय</span>
                      <span className="text-secondary">AQI 200 से अधिक होने पर बाहरी खेलकूद गतिविधियों को रोकें</span>
                    </div>
                  </div>
                  
                  <div className="bg-red-50 p-3 rounded-lg border border-red-200 text-error flex items-start gap-2.5">
                    <PhoneCall className="w-5 h-5 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-xs">आपातकालीन हेल्पलाइन संपर्क</p>
                      <p className="text-[10px] mt-0.5">सांस में तकलीफ होने पर तुरंत <b>1800-425-VAYU</b> पर कॉल करें या नजदीकी सिटी स्वास्थ्य केंद्र पर जाएँ।</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="pt-2 border-t border-outline-variant/30 flex justify-end">
                <button 
                  onClick={() => setIsHealthOpen(false)}
                  className="bg-primary text-white text-xs font-bold py-2 px-4 rounded-lg uppercase tracking-wider hover:brightness-110 transition-all"
                >
                  ठीक है / Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Violation reporting popup modal */}
      {isReportOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center z-50 p-4">
          <div className="bg-white border border-outline-variant shadow-lg rounded-2xl max-w-md w-full overflow-hidden p-6 relative">
            <button 
              onClick={() => setIsReportOpen(false)}
              className="absolute top-4 right-4 text-secondary hover:text-on-surface"
            >
              <X className="w-5 h-5" />
            </button>
            
            {reportSubmitted ? (
              <div className="py-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto text-green-600">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h4 className="text-sm font-bold text-on-surface">Report Registered Successfully</h4>
                <p className="text-xs text-secondary">The environmental board has logged this concern and assigned ticket #VS-{Math.floor(Math.random() * 9000 + 1000)}.</p>
              </div>
            ) : (
              <form onSubmit={handleReportSubmit} className="space-y-4">
                <div className="border-b border-outline-variant/30 pb-3">
                  <h3 className="text-sm font-bold text-on-surface uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-error" />
                    <span>Report Pollution Violation</span>
                  </h3>
                  <p className="text-[10px] text-secondary mt-0.5">Submit details to trigger authority inspection.</p>
                </div>
                
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-secondary uppercase">Violation Heading</label>
                  <input 
                    type="text" 
                    required 
                    placeholder="e.g., Heavy open dust at construction site"
                    value={reportForm.title}
                    onChange={(e) => setReportForm({...reportForm, title: e.target.value})}
                    className="w-full bg-surface-container-low border border-outline-variant/50 rounded-lg text-xs py-1.5 px-3 focus:ring-1 focus:ring-primary"
                  />
                </div>
                
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-secondary uppercase">Pollution Category</label>
                  <select 
                    value={reportForm.sourceType}
                    onChange={(e) => setReportForm({...reportForm, sourceType: e.target.value})}
                    className="w-full bg-surface-container-low border border-outline-variant/50 rounded-lg text-xs py-1.5 px-2 focus:ring-1 focus:ring-primary cursor-pointer"
                  >
                    <option value="construction">Open Dust / Construction</option>
                    <option value="industrial">Factory Exhaust / Smoke</option>
                    <option value="traffic">Extreme Idle Traffic Corridor</option>
                    <option value="waste_burning">Waste Burning</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-secondary uppercase">Location Description</label>
                  <input 
                    type="text" 
                    required 
                    placeholder="e.g., Near GK Metro Station Gate 2"
                    value={reportForm.location}
                    onChange={(e) => setReportForm({...reportForm, location: e.target.value})}
                    className="w-full bg-surface-container-low border border-outline-variant/50 rounded-lg text-xs py-1.5 px-3 focus:ring-1 focus:ring-primary"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-secondary uppercase">Additional Description</label>
                  <textarea 
                    rows="3" 
                    required
                    placeholder="Provide details about size, duration, visibility impact..."
                    value={reportForm.description}
                    onChange={(e) => setReportForm({...reportForm, description: e.target.value})}
                    className="w-full bg-surface-container-low border border-outline-variant/50 rounded-lg text-xs py-1.5 px-3 focus:ring-1 focus:ring-primary resize-none"
                  />
                </div>
                
                <button 
                  type="submit"
                  className="w-full bg-primary text-white text-xs font-bold py-2 rounded-lg hover:brightness-110 transition-all uppercase tracking-wider"
                >
                  Register Violator
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
