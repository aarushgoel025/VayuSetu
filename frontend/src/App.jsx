import React, { useState, useEffect, useMemo, useRef } from 'react';
import MapView from './components/MapView';
import LayerToggle from './components/LayerToggle';
import AccountabilityFeed from './components/AccountabilityFeed';
import ForecastChart from './components/ForecastChart';
import FingerprintList from './components/FingerprintList';
import HarmScoreCard from './components/HarmScoreCard';
import LegalAdvisoryCard from './components/LegalAdvisoryCard';
import EmissionsCard from './components/EmissionsCard';
import CitizenDashboard from './components/CitizenDashboard';
import LandingSequence from './components/LandingSequence';
import Login from './components/Login';
import { supabase } from './api/supabase';
import {
  getStations,
  getSources,
  getVulnerableZones,
  generateNotice,
  getStationPanel
} from './api/client';
import {
  ShieldAlert,
  Search,
  Bell,
  User,
  LayoutDashboard,
  Map,
  Radio,
  Scale,
  FileText,
  Settings,
  HelpCircle,
  TrendingUp,
  Plus,
  Download,
  Check,
  Wind,
  X,
  FileCode,
  Activity,
  Heart
} from 'lucide-react';

export default function App() {
  const [currentView, setCurrentView] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('view') === 'citizen' || window.location.hash === '#/citizen' || window.location.pathname === '/citizen') {
      return 'citizen';
    }
    return 'authority';
  });

  const [session, setSession] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setAuthLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => {
      if (subscription) subscription.unsubscribe();
    };
  }, []);

  const handleLogout = async (message = null) => {
    try {
      await supabase.auth.signOut();
      setSession(null);
      if (message && typeof message === 'string') {
        alert(message);
      }
    } catch (err) {
      console.error("Logout error:", err);
    }
  };

  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'explorer', 'sensors', 'enforcement', 'reports'
  const [selectedStation, setSelectedStation] = useState(null);
  const [stations, setStations] = useState([]);
  const [sources, setSources] = useState([]);
  const [zones, setZones] = useState([]);
  // panelData holds the unified response from /api/station-panel
  // ONE Gemini call per station click instead of 5 separate calls
  const [panelData, setPanelData] = useState(null);
  const [panelLoading, setPanelLoading] = useState(false);
  const [layerState, setLayerState] = useState({
    stations: true,
    sources: true,
    vulnerableZones: true,
    satelliteHotspots: true,
  });
  const [searchQuery, setSearchQuery] = useState('');

  // Helper for dynamic wind speed
  const getWindDirection = (deg) => {
    if (deg >= 337.5 || deg < 22.5) return 'N';
    if (deg >= 22.5 && deg < 67.5) return 'NE';
    if (deg >= 67.5 && deg < 112.5) return 'E';
    if (deg >= 112.5 && deg < 157.5) return 'SE';
    if (deg >= 157.5 && deg < 202.5) return 'S';
    if (deg >= 202.5 && deg < 247.5) return 'SW';
    if (deg >= 247.5 && deg < 292.5) return 'W';
    if (deg >= 292.5 && deg < 337.5) return 'NW';
    return 'N';
  };

  const displayWind = useMemo(() => {
    if (selectedStation && selectedStation.wind_speed != null) {
      return `${getWindDirection(selectedStation.wind_deg || 0)} ${selectedStation.wind_speed.toFixed(1)} km/h`;
    } else if (stations.length > 0) {
      const avgSpeed = stations.reduce((acc, st) => acc + (st.wind_speed || 0), 0) / stations.length;
      return `AVG ${avgSpeed.toFixed(1)} km/h`;
    }
    return '-- km/h';
  }, [selectedStation, stations]);

  const [generatingFor, setGeneratingFor] = useState(null);
  const [successFor, setSuccessFor] = useState(null);

  // Reports Modal State
  const [isReportOpen, setIsReportOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stData, srcData, zoneData] = await Promise.all([
          getStations(),
          getSources(),
          getVulnerableZones()
        ]);
        setStations(stData);
        setSources(srcData);
        if (zoneData) setZones(zoneData);
      } catch (err) {
        console.error("Error loading dashboard data", err);
      }
    };
    fetchData();
  }, []);

  // Fetch unified panel data when station changes — ONE call replaces 5
  useEffect(() => {
    if (currentView !== 'authority' || !session) return;
    
    setPanelLoading(true);
    setPanelData(null);
    
    const stationId = selectedStation ? selectedStation.id : 'city_wide';
    const lat = selectedStation ? selectedStation.lat : 28.6139;
    const lng = selectedStation ? selectedStation.lng : 77.2090;

    getStationPanel(stationId, lat, lng)
      .then(data => {
        // Customize the title for city-wide view
        if (!selectedStation && data) {
          data.station_name = 'NCR (City-wide)';
        }
        setPanelData(data);
      })
      .catch(err => {
        console.error('Panel data fetch error:', err);
        if (err.message?.includes('401') || err.message?.toLowerCase().includes('unauthorized')) {
          handleLogout('Your session has expired. Please sign in again.');
        }
      })
      .finally(() => setPanelLoading(false));
  }, [selectedStation?.id, session, currentView]);

  // Handle client-side hash routing
  useEffect(() => {
    const handleHashChange = () => {
      if (window.location.hash === '#/citizen') {
        setCurrentView('citizen');
      } else {
        setCurrentView('authority');
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleGenerateNotice = async (sourceId, sourceName) => {
    setGeneratingFor(sourceId);
    try {
      const blob = await generateNotice(sourceId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Legal_Notice_${sourceName.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setSuccessFor(sourceId);
      setTimeout(() => setSuccessFor(null), 3000);
    } catch (err) {
      console.error("Notice generation error", err);
      alert("Failed to generate notice.");
    } finally {
      setGeneratingFor(null);
    }
  };

  const handleViewChange = (view) => {
    setCurrentView(view);
    window.location.hash = view === 'citizen' ? '#/citizen' : '#/';
  };

  if (currentView === 'citizen') {
    return <CitizenDashboard onViewSwitch={handleViewChange} />;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center gap-4">
        <div className="w-10 h-10 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin"></div>
        <p className="text-emerald-400 font-bold text-xs uppercase tracking-wider animate-pulse">Checking credentials...</p>
      </div>
    );
  }

  if (!session) {
    return <Login onLoginSuccess={(sess) => setSession(sess)} onViewSwitch={handleViewChange} />;
  }


  // Calculate dynamic stats
  const cityAvgAqi = stations.length > 0
    ? Math.round(stations.reduce((sum, s) => sum + s.aqi, 0) / stations.length)
    : 142;

  const currentAqi = selectedStation ? selectedStation.aqi : cityAvgAqi;

  const getAqiCategory = (aqi) => {
    if (aqi <= 50) return { label: 'Good', style: 'bg-green-100 text-green-800' };
    if (aqi <= 100) return { label: 'Moderate', style: 'bg-yellow-100 text-yellow-800' };
    if (aqi <= 200) return { label: 'Poor', style: 'bg-orange-100 text-orange-800' };
    if (aqi <= 300) return { label: 'Severe', style: 'bg-red-100 text-red-800' };
    return { label: 'Critical', style: 'bg-red-200 text-red-950 font-bold' };
  };

  const aqiCat = getAqiCategory(currentAqi);

  const worstSource = sources.length > 0
    ? sources[0]
    : { name: 'Dadri Thermal Plant', activity_level: 'high' };

  // Filter stations & sources by search query
  const filteredStations = stations.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="h-screen w-full overflow-y-auto overflow-x-hidden snap-y snap-mandatory bg-slate-950 text-slate-100 scroll-smooth">
      <LandingSequence />
      
      {/* 5. Main Dashboard Section */}
      <section className="h-screen w-full snap-start relative">
        <div className="w-screen h-screen flex flex-col overflow-hidden bg-background text-on-surface">
      {/* Top Warning Announcement Alert Bar */}
      <AccountabilityFeed />

      {/* Header/Top Navigation */}
      <header className="h-16 border-b border-outline-variant bg-white flex justify-between items-center px-6 z-30 flex-shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-xl font-bold tracking-tight text-primary">VayuSetu</span>
          <div className="relative ml-8 hidden md:block">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-outline" />
            <input
              type="text"
              placeholder="Search monitoring stations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-surface-container-low border-none rounded-lg pl-9 pr-4 py-1.5 text-xs w-64 focus:ring-2 focus:ring-primary focus:bg-white transition-all text-on-surface placeholder:text-outline"
            />
            {searchQuery && (
              <div className="absolute top-10 left-0 w-64 bg-white border border-outline-variant rounded-lg shadow-lg z-50 p-2 max-h-40 overflow-y-auto">
                {filteredStations.length === 0 ? (
                  <div className="p-2 text-xs text-secondary italic">No stations found</div>
                ) : (
                  filteredStations.map(st => (
                    <button
                      key={st.id}
                      onClick={() => {
                        setSelectedStation(st);
                        setSearchQuery('');
                        setActiveTab('dashboard');
                      }}
                      className="w-full text-left p-2 hover:bg-surface-container-low text-xs rounded transition-colors"
                    >
                      {st.name} (AQI: {st.aqi})
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        <nav className="flex items-center gap-6">
          <div className="hidden md:flex gap-6">
            <button onClick={() => setActiveTab('dashboard')} className={`text-xs tracking-wider font-semibold uppercase ${activeTab === 'dashboard' ? 'text-primary border-b-2 border-primary pb-1' : 'text-secondary hover:text-primary transition-colors'}`}>Dashboard</button>
            <button onClick={() => setActiveTab('explorer')} className={`text-xs tracking-wider font-semibold uppercase ${activeTab === 'explorer' ? 'text-primary border-b-2 border-primary pb-1' : 'text-secondary hover:text-primary transition-colors'}`}>Explorer</button>
            <button onClick={() => setActiveTab('reports')} className={`text-xs tracking-wider font-semibold uppercase ${activeTab === 'reports' ? 'text-primary border-b-2 border-primary pb-1' : 'text-secondary hover:text-primary transition-colors'}`}>Report Center</button>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => handleViewChange('citizen')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-primary text-primary hover:bg-primary hover:text-white transition-all text-xs font-bold uppercase tracking-wider"
            >
              <span>Citizen View</span>
            </button>
            <div className="h-4 w-px bg-outline-variant hidden sm:block"></div>
            <button className="p-2 rounded-full hover:bg-surface-container-low transition-colors text-on-surface-variant">
              <Bell className="w-4 h-4" />
            </button>
            <button onClick={() => handleLogout()} className="p-2 rounded-full hover:bg-surface-container-low hover:text-red-500 transition-colors text-on-surface-variant" title="Log Out">
              <User className="w-4 h-4" />
            </button>
          </div>
        </nav>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Side Navigation panel */}
        <aside className="w-sidebar-width border-r border-outline-variant bg-white flex flex-col py-4 z-20 flex-shrink-0">
          <div className="px-4 mb-6">
            <div className="flex items-center gap-3 px-3 py-2 bg-surface-container-low rounded-xl border border-outline-variant/30">
              <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-on-primary-container font-bold">
                VS
              </div>
              <div>
                <p className="text-xs font-bold text-primary">Authority Portal</p>
                <p className="text-[10px] text-secondary">City Management</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 px-3 space-y-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full text-left rounded-lg flex items-center gap-3 px-3 py-2 text-xs transition-all ${activeTab === 'dashboard' ? 'bg-primary/10 text-primary font-bold' : 'text-secondary hover:bg-surface-container-low font-medium'}`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>
            <button
              onClick={() => setActiveTab('explorer')}
              className={`w-full text-left rounded-lg flex items-center gap-3 px-3 py-2 text-xs transition-all ${activeTab === 'explorer' ? 'bg-primary/10 text-primary font-bold' : 'text-secondary hover:bg-surface-container-low font-medium'}`}
            >
              <Map className="w-4 h-4" />
              <span>Map Explorer</span>
            </button>
            <button
              onClick={() => setActiveTab('sensors')}
              className={`w-full text-left rounded-lg flex items-center gap-3 px-3 py-2 text-xs transition-all ${activeTab === 'sensors' ? 'bg-primary/10 text-primary font-bold' : 'text-secondary hover:bg-surface-container-low font-medium'}`}
            >
              <Radio className="w-4 h-4" />
              <span>Sensors List</span>
            </button>
            <button
              onClick={() => setActiveTab('enforcement')}
              className={`w-full text-left rounded-lg flex items-center gap-3 px-3 py-2 text-xs transition-all ${activeTab === 'enforcement' ? 'bg-primary/10 text-primary font-bold' : 'text-secondary hover:bg-surface-container-low font-medium'}`}
            >
              <Scale className="w-4 h-4" />
              <span>Enforcement</span>
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`w-full text-left rounded-lg flex items-center gap-3 px-3 py-2 text-xs transition-all ${activeTab === 'reports' ? 'bg-primary/10 text-primary font-bold' : 'text-secondary hover:bg-surface-container-low font-medium'}`}
            >
              <FileText className="w-4 h-4" />
              <span>Reports</span>
            </button>
          </nav>

          <div className="px-4 py-3 mt-auto border-t border-outline-variant/30 space-y-3">
            <button
              onClick={() => handleGenerateNotice(worstSource.id || 's1', worstSource.name)}
              disabled={generatingFor !== null}
              className="w-full bg-primary text-white text-xs font-bold py-2.5 rounded-lg shadow-sm hover:brightness-110 active:scale-95 transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
            >
              {generatingFor === worstSource.id ? (
                <span className="animate-pulse">Generating...</span>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Generate Notice</span>
                </>
              )}
            </button>
            
            <button
              onClick={() => handleLogout()}
              className="w-full bg-surface-container-high hover:bg-red-500/10 text-red-500 text-xs font-bold py-2 rounded-lg border border-outline-variant/40 hover:border-red-500/20 active:scale-95 transition-all flex items-center justify-center gap-1.5"
            >
              <span>Log Out</span>
            </button>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-grow bg-background overflow-y-auto p-6 z-10">

          {/* TAB 1: DASHBOARD VIEW */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Stats Summary Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-secondary uppercase tracking-wider">Current AQI</span>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-4xl font-extrabold text-primary">{currentAqi}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${aqiCat.style}`}>
                        {aqiCat.label}
                      </span>
                    </div>
                  </div>
                  <div className="mt-4 text-[10px] text-on-surface-variant flex items-center gap-1">
                    <TrendingUp className="w-3.5 h-3.5 text-error" />
                    <span>+12% from previous hour</span>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-secondary uppercase tracking-wider">Worst Source</span>
                    <p className="text-base font-bold text-on-surface mt-1 truncate">{worstSource.name}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-error"></span>
                      <span className="text-xs font-semibold text-on-surface">PM2.5: 284 µg/m³</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-secondary uppercase tracking-wider">Population at Risk</span>
                    <p className="text-4xl font-extrabold text-on-surface mt-1">1.2M</p>
                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex flex-col">
                        <span className="text-[10px] text-secondary font-bold uppercase">Children</span>
                        <span className="text-sm font-bold text-on-surface">820k</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[10px] text-secondary font-bold uppercase">Seniors</span>
                        <span className="text-sm font-bold text-on-surface">380k</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-secondary uppercase tracking-wider">Active Violations</span>
                    <p className="text-4xl font-extrabold text-error mt-1">24</p>
                    <button
                      onClick={() => setActiveTab('enforcement')}
                      className="text-primary text-[11px] font-bold mt-2 hover:underline flex items-center gap-1"
                    >
                      <span>Review cases</span>
                      <Plus className="w-3 h-3 rotate-45" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Map & Detail Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
                {/* Map Canvas (8/12) */}
                <div className="lg:col-span-8 relative bg-white rounded-xl shadow-soft border border-outline-variant overflow-hidden min-h-[500px] flex flex-col">
                  <div className="flex-1 relative z-0">
                    <MapView
                      layerState={layerState}
                      onStationSelect={setSelectedStation}
                    />

                    {/* Floating Layers toggle panel */}
                    <div className="absolute top-4 right-4 z-[1000]">
                      <LayerToggle layerState={layerState} setLayerState={setLayerState} />
                    </div>

                    {/* Floating wind speed data overlay */}
                    <div className="absolute top-4 left-4 z-[1000] glass-panel px-4 py-2.5 rounded-xl shadow-soft">
                      <div className="flex items-center gap-3">
                        <div className="flex flex-col items-center">
                          <Wind className="text-primary w-5 h-5" />
                          <span className="text-[9px] font-bold text-secondary uppercase mt-0.5">Wind</span>
                        </div>
                        <div>
                          <p className="font-mono text-xs font-bold text-on-surface">{displayWind}</p>
                          <p className="text-[9px] text-secondary font-medium">Carrying particulate</p>
                        </div>
                      </div>
                    </div>

                    {/* Floating Legend Overlay */}
                    <div className="absolute bottom-4 left-4 z-[1000] glass-panel px-3 py-2 rounded-xl shadow-soft">
                      <div className="flex flex-col gap-1 w-32">
                        <div className="h-1.5 w-full bg-gradient-to-r from-green-500 via-yellow-400 to-red-600 rounded-full"></div>
                        <div className="flex justify-between text-[9px] font-bold text-secondary">
                          <span>GOOD</span>
                          <span>MOD</span>
                          <span>SEV</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Intelligence Detail Panel (4/12) */}
                <div className="lg:col-span-4 flex flex-col gap-6 overflow-y-auto max-h-[500px] pr-1">
                  {/* Selected Station indicator / City-wide Indicator banner */}
                  <div className="bg-white px-4 py-3 rounded-xl border border-outline-variant shadow-soft flex items-center justify-between">
                    <div>
                      <span className="text-[9px] font-bold text-secondary uppercase tracking-wider">Focus Scope</span>
                      <h4 className="text-sm font-bold text-on-surface mt-0.5 truncate max-w-[180px]">
                        {selectedStation ? selectedStation.name : 'NCR (City-wide)'}
                      </h4>
                    </div>
                    {selectedStation && (
                      <button
                        onClick={() => setSelectedStation(null)}
                        className="p-1 rounded-full hover:bg-surface-container-low transition-colors text-secondary hover:text-on-surface"
                        title="Reset to City-wide View"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <ForecastChart panelData={panelData} panelLoading={panelLoading} stationId={selectedStation ? selectedStation.id : 'delhi_anand_vihar'} />
                  <FingerprintList panelData={panelData} panelLoading={panelLoading} lat={selectedStation ? selectedStation.lat : 28.6} lng={selectedStation ? selectedStation.lng : 77.2} />
                  <HarmScoreCard panelData={panelData} panelLoading={panelLoading} lat={selectedStation ? selectedStation.lat : 28.6} lng={selectedStation ? selectedStation.lng : 77.2} />
                  <LegalAdvisoryCard panelData={panelData} panelLoading={panelLoading} lat={selectedStation ? selectedStation.lat : 28.6} lng={selectedStation ? selectedStation.lng : 77.2} />
                  <EmissionsCard panelData={panelData} panelLoading={panelLoading} lat={selectedStation ? selectedStation.lat : 28.6} lng={selectedStation ? selectedStation.lng : 77.2} />
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: MAP EXPLORER VIEW (FULL-SCREEN GEOGRAPHICAL MODE) */}
          {activeTab === 'explorer' && (
            <div className="w-full h-[calc(100vh-120px)] relative bg-white rounded-xl shadow-soft border border-outline-variant overflow-hidden flex flex-col">
              <div className="flex-grow relative z-0">
                <MapView
                  layerState={layerState}
                  onStationSelect={(st) => {
                    setSelectedStation(st);
                    setActiveTab('dashboard');
                  }}
                />

                {/* Floating Layers toggle panel */}
                <div className="absolute top-4 right-4 z-[1000]">
                  <LayerToggle layerState={layerState} setLayerState={setLayerState} />
                </div>

                {/* Floating Map Legend Overlay */}
                <div className="absolute bottom-4 left-4 z-[1000] glass-panel px-4 py-3 rounded-xl shadow-soft">
                  <span className="text-[10px] font-bold text-secondary uppercase tracking-wider block mb-1.5">Air Quality Legend</span>
                  <div className="flex flex-col gap-1 w-44">
                    <div className="h-2 w-full bg-gradient-to-r from-green-500 via-yellow-400 to-red-650 rounded-full"></div>
                    <div className="flex justify-between text-[9px] font-bold text-secondary mt-0.5">
                      <span>0 (GOOD)</span>
                      <span>150 (POOR)</span>
                      <span>300+ (SEV)</span>
                    </div>
                  </div>
                </div>

                {/* Floating Layer Helper Info Box */}
                <div className="absolute bottom-4 right-4 z-[1000] glass-panel px-4 py-3 rounded-xl shadow-soft max-w-xs text-xs">
                  <span className="font-bold text-primary flex items-center gap-1.5">
                    <Activity className="w-4 h-4" />
                    <span>Geographical Mode</span>
                  </span>
                  <p className="text-[11px] text-secondary mt-1.5 leading-relaxed">
                    Click on any droplet sensor to view detailed forecasted readings, or click on diamond shapes to see industrial emissions sources.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: SENSORS LIST VIEW */}
          {activeTab === 'sensors' && (
            <div className="bg-white rounded-xl shadow-soft border border-outline-variant overflow-hidden flex flex-col">
              <div className="px-6 py-4 border-b border-outline-variant/30 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-base text-on-surface">NCR Monitoring Stations List</h3>
                  <p className="text-xs text-secondary mt-0.5">Showing active telemetry readings from {stations.length} regional sensors.</p>
                </div>
                <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold">
                  {stations.filter(s => s.aqi < 200).length} Healthy / {stations.filter(s => s.aqi >= 200).length} Warning
                </span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-on-surface">
                  <thead className="bg-surface-container-low text-secondary font-bold uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-3.5 border-b border-outline-variant/30">Station Name</th>
                      <th className="px-6 py-3.5 border-b border-outline-variant/30">Coordinates</th>
                      <th className="px-6 py-3.5 border-b border-outline-variant/30">Current AQI</th>
                      <th className="px-6 py-3.5 border-b border-outline-variant/30">PM2.5 & PM10</th>
                      <th className="px-6 py-3.5 border-b border-outline-variant/30">Wind Vector</th>
                      <th className="px-6 py-3.5 border-b border-outline-variant/30 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/30">
                    {stations.map(st => {
                      const color = st.aqi <= 50 ? 'text-green-700 font-bold' : st.aqi <= 100 ? 'text-yellow-700 font-bold' : st.aqi <= 200 ? 'text-orange-700 font-bold' : 'text-red-700 font-bold';
                      return (
                        <tr key={st.id} className="hover:bg-surface-container-lowest transition-colors">
                          <td className="px-6 py-4">
                            <span className="font-bold text-on-surface text-sm">{st.name}</span>
                          </td>
                          <td className="px-6 py-4 font-mono text-[11px] text-secondary">
                            {st.lat.toFixed(4)}° N, {st.lng.toFixed(4)}° E
                          </td>
                          <td className="px-6 py-4">
                            <span className={color}>{st.aqi} AQI</span>
                          </td>
                          <td className="px-6 py-4 text-secondary">
                            PM2.5: <span className="text-on-surface font-semibold">{st.pm25} µg/m³</span> • PM10: <span className="text-on-surface font-semibold">{st.pm10} µg/m³</span>
                          </td>
                          <td className="px-6 py-4 text-secondary font-mono text-[11px]">
                            {st.wind_speed} km/h @ {st.wind_deg}°
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => {
                                setSelectedStation(st);
                                setActiveTab('dashboard');
                              }}
                              className="text-primary hover:underline font-bold text-xs"
                            >
                              Open Details
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: ENFORCEMENT BOARD VIEW */}
          {activeTab === 'enforcement' && (
            <div className="space-y-6">
              {/* Watchlist table */}
              <div className="bg-white rounded-xl shadow-soft border border-outline-variant overflow-hidden flex flex-col">
                <div className="px-6 py-4 border-b border-outline-variant/30 flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-base text-on-surface">Enforcement Watchlist</h3>
                    <p className="text-xs text-secondary mt-0.5">Real-time status of critical pollution emitters and legal compliance actions.</p>
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-on-surface">
                    <thead className="bg-surface-container-low text-secondary font-bold uppercase tracking-wider">
                      <tr>
                        <th className="px-6 py-3.5 border-b border-outline-variant/30">Source Name</th>
                        <th className="px-6 py-3.5 border-b border-outline-variant/30">Location</th>
                        <th className="px-6 py-3.5 border-b border-outline-variant/30">Violation Level</th>
                        <th className="px-6 py-3.5 border-b border-outline-variant/30">Compliance Status</th>
                        <th className="px-6 py-3.5 border-b border-outline-variant/30 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant/30">
                      {sources.map((src, index) => {
                        const violationCount = index % 3 === 0 ? 3 : index % 3 === 1 ? 2 : 1;
                        const complianceLabel = index % 3 === 0 ? 'Critical (24%)' : index % 3 === 1 ? 'Warning (58%)' : 'Good (88%)';
                        const complianceStyle = index % 3 === 0 ? 'bg-error-container text-on-error-container font-bold' : index % 3 === 1 ? 'bg-tertiary-container text-on-tertiary-container font-bold' : 'bg-green-100 text-green-800 font-bold';

                        return (
                          <tr key={src.id} className="hover:bg-surface-container-lowest transition-colors">
                            <td className="px-6 py-4">
                              <p className="font-bold text-on-surface text-sm">{src.name}</p>
                              <span className="text-[10px] text-secondary uppercase font-semibold">{src.type.replace('_', ' ')}</span>
                            </td>
                            <td className="px-6 py-4 text-secondary">{src.address}</td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-1">
                                {Array.from({ length: 5 }).map((_, i) => (
                                  <div
                                    key={i}
                                    className={`w-2 h-2 rounded-full ${i < violationCount ? 'bg-error' : 'bg-surface-container-highest'}`}
                                  />
                                ))}
                                <span className="text-[10px] text-secondary ml-1.5 font-semibold">{violationCount}/5 Active</span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] ${complianceStyle}`}>
                                {complianceLabel}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                              {successFor === src.id ? (
                                <span className="inline-flex items-center text-green-700 text-xs font-bold uppercase px-3 py-1.5">
                                  <Check className="w-3.5 h-3.5 mr-1" /> Notice Downloaded
                                </span>
                              ) : (
                                <button
                                  onClick={() => handleGenerateNotice(src.id, src.name)}
                                  disabled={generatingFor === src.id}
                                  className="bg-primary hover:brightness-110 text-white font-bold px-4 py-2 rounded-lg shadow-sm active:scale-95 transition-all text-xs inline-flex items-center gap-1.5 disabled:opacity-50"
                                >
                                  {generatingFor === src.id ? (
                                    <span className="animate-pulse">Generating...</span>
                                  ) : (
                                    <>
                                      <Download className="w-3.5 h-3.5" />
                                      <span>Dispatch Notice</span>
                                    </>
                                  )}
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: REPORTS CENTER VIEW */}
          {activeTab === 'reports' && (
            <div className="bg-white rounded-xl shadow-soft border border-outline-variant p-6 max-w-3xl mx-auto space-y-6">
              <div className="border-b border-outline-variant/30 pb-4 flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-xl text-on-surface">Executive Air Quality Report</h3>
                  <p className="text-xs text-secondary mt-0.5">National Capital Region (NCR) • Generated on demand</p>
                </div>
                <button
                  onClick={() => alert("Report downloaded successfully in PDF format.")}
                  className="bg-primary text-white font-bold text-xs py-2 px-4 rounded-lg flex items-center gap-2 hover:brightness-110 transition-all"
                >
                  <Download className="w-4 h-4" />
                  <span>Download PDF</span>
                </button>
              </div>

              <div className="grid grid-cols-3 gap-6 text-center">
                <div className="bg-surface-container-low p-4 rounded-xl border border-outline-variant/30">
                  <span className="text-xs text-secondary font-bold uppercase">City Avg AQI</span>
                  <div className="text-3xl font-extrabold text-primary mt-1">{cityAvgAqi}</div>
                </div>
                <div className="bg-surface-container-low p-4 rounded-xl border border-outline-variant/30">
                  <span className="text-xs text-secondary font-bold uppercase">Active Notices</span>
                  <div className="text-3xl font-extrabold text-tertiary mt-1">14</div>
                </div>
                <div className="bg-surface-container-low p-4 rounded-xl border border-outline-variant/30">
                  <span className="text-xs text-secondary font-bold uppercase">Compliance Ratio</span>
                  <div className="text-3xl font-extrabold text-green-700 mt-1">72%</div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-bold text-sm text-on-surface border-b border-outline-variant/30 pb-1.5">Executive Summary</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  During this assessment cycle, the citywide AQI remains elevated at an average reading of <b>{cityAvgAqi}</b>.
                  Gaussian plume dispersion models estimate that local industrial hotspots—principally Badarpur and Dadri power generation yards—remain the dominant point-source contributors, carrying fine particulate downwind along the central secretariat traffic corridor.
                </p>

                <h4 className="font-bold text-sm text-on-surface border-b border-outline-variant/30 pb-1.5 pt-2">Compliance Action Summary</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  A total of 14 notices were issued this week under Section 31A of the Air Act 1981. Four repeats have been registered, triggering active health warnings for downstream institutions. Particulate monitoring indicates Noida construction sites have initiated secondary mist cannons.
                </p>
              </div>

              <div className="flex justify-end gap-3 pt-6 border-t border-outline-variant/30">
                <button
                  onClick={() => alert("Report printed successfully.")}
                  className="px-4 py-2 border border-outline-variant text-secondary font-bold rounded-lg text-xs hover:bg-surface-container-low transition-all"
                >
                  Print Report
                </button>
                <button
                  onClick={() => {
                    alert("Weekly scheduler configured.");
                  }}
                  className="px-4 py-2 bg-surface-container-highest text-on-surface font-bold rounded-lg text-xs hover:brightness-95 transition-all"
                >
                  Schedule Weekly Email
                </button>
              </div>
            </div>
          )}

        </main>
      </div>
        </div>
      </section>
    </div>
  );
}
