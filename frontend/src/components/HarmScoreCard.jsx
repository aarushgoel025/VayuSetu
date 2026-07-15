import React, { useState } from 'react';
import { ShieldAlert, Globe } from 'lucide-react';

/**
 * HarmScoreCard — professional health advisory card with EN / हिं language toggle.
 * Reads from panelData prop (unified /api/station-panel endpoint).
 * English is shown by default; Hindi toggle switches to Devanagari text.
 */
export default function HarmScoreCard({ panelData, panelLoading, lat, lng }) {
  const [lang, setLang] = useState('en');

  if (panelLoading || !panelData) {
    return (
      <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft animate-pulse">
        <div className="h-4 bg-surface-container-highest rounded w-2/5 mb-5"></div>
        <div className="grid grid-cols-3 gap-3 mb-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-12 bg-surface-container-highest rounded"></div>
          ))}
        </div>
        <div className="h-16 bg-surface-container-highest rounded"></div>
      </div>
    );
  }

  let data = panelData.harm || {};
  let englishAdvisory = panelData.english_advisory || '';
  let hindiAdvisory = panelData.hindi_advisory || '';
  const aqiLabel = panelData.aqi_label || 'Unknown';
  const currentAqi = panelData.current_aqi || 0;

  // Hardcode values for city-wide tab, removing dynamic/Gemini text for this section
  if (panelData.station_id === 'city_wide') {
    data = {
      ...data,
      children_exposed: 820000,
      patients_exposed: 380000,
      affected_zones: [
        { name: 'Delhi Public Schools (All Branches)', type: 'school', population: 45000 },
        { name: 'AIIMS & Safdarjung Hospital', type: 'hospital', population: 12000 },
        { name: 'Old Age Homes (NCR)', type: 'old_age_home', population: 8500 }
      ]
    };
    englishAdvisory = `Air quality across Delhi NCR is ${aqiLabel} (AQI: ${currentAqi}). People with respiratory conditions, elderly, and children should reduce outdoor exposure. Keep windows closed and avoid heavy outdoor exercise.`;
    hindiAdvisory = `दिल्ली एनसीआर में वायु गुणवत्ता ${aqiLabel} (AQI: ${currentAqi}) है। बच्चों और बुजुर्गों को बाहर जाने से बचना चाहिए। घर की खिड़कियाँ बंद रखें।`;
  }

  const severityConfig = {
    Good:         { bg: 'bg-emerald-50',  border: 'border-emerald-200', badge: 'bg-emerald-100 text-emerald-800',  dot: 'bg-emerald-500' },
    Satisfactory: { bg: 'bg-green-50',    border: 'border-green-200',   badge: 'bg-green-100 text-green-800',      dot: 'bg-green-500'   },
    Moderate:     { bg: 'bg-amber-50',    border: 'border-amber-200',   badge: 'bg-amber-100 text-amber-800',      dot: 'bg-amber-500'   },
    Poor:         { bg: 'bg-orange-50',   border: 'border-orange-200',  badge: 'bg-orange-100 text-orange-800',   dot: 'bg-orange-500'  },
    Severe:       { bg: 'bg-red-50',      border: 'border-red-200',     badge: 'bg-red-100 text-red-800',         dot: 'bg-red-500'     },
  };
  const cfg = severityConfig[aqiLabel] || severityConfig['Moderate'];

  const advisoryText = lang === 'en' ? englishAdvisory : hindiAdvisory;

  return (
    <div className={`${cfg.bg} p-5 rounded-xl border ${cfg.border}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-on-surface-variant" />
          <span className="text-xs font-bold text-on-surface uppercase tracking-wider">
            Health Advisory
          </span>
          <span className={`${cfg.badge} text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1`}>
            <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} inline-block`}></span>
            {aqiLabel}
          </span>
        </div>

        {/* Language toggle */}
        <div className="flex items-center gap-1 bg-white border border-outline-variant rounded-lg p-0.5 shadow-sm">
          <button
            onClick={() => setLang('en')}
            className={`px-2.5 py-1 text-[10px] font-bold rounded-md transition-all duration-200 ${
              lang === 'en'
                ? 'bg-primary text-white shadow-sm'
                : 'text-secondary hover:text-on-surface'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setLang('hi')}
            className={`px-2.5 py-1 text-[10px] font-bold rounded-md transition-all duration-200 ${
              lang === 'hi'
                ? 'bg-primary text-white shadow-sm'
                : 'text-secondary hover:text-on-surface'
            }`}
          >
            हिं
          </button>
        </div>
      </div>

      {/* Exposure Stats */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-center">
        <div className="bg-white/70 rounded-lg py-2.5 px-1 border border-white/80">
          <span className="text-xl font-bold text-on-surface block">
            {data.children_exposed >= 1000
              ? `${(data.children_exposed / 1000).toFixed(0)}k`
              : data.children_exposed || 0}
          </span>
          <span className="text-[9px] text-secondary font-semibold uppercase tracking-wider mt-0.5 block">
            Children
          </span>
        </div>
        <div className="bg-white/70 rounded-lg py-2.5 px-1 border border-white/80">
          <span className="text-xl font-bold text-on-surface block">
            {data.patients_exposed >= 1000
              ? `${(data.patients_exposed / 1000).toFixed(0)}k`
              : data.patients_exposed || 0}
          </span>
          <span className="text-[9px] text-secondary font-semibold uppercase tracking-wider mt-0.5 block">
            Seniors
          </span>
        </div>
        <div className="bg-white/70 rounded-lg py-2.5 px-1 border border-white/80">
          <span className="text-xl font-bold text-on-surface block">
            {(data.affected_zones || []).filter(z => z.type === 'hospital').length || 1}
          </span>
          <span className="text-[9px] text-secondary font-semibold uppercase tracking-wider mt-0.5 block">
            Hospitals
          </span>
        </div>
      </div>

      {/* Advisory Text */}
      {advisoryText ? (
        <div className="bg-white/80 border border-white/90 rounded-lg p-3 mb-3 text-xs text-on-surface leading-relaxed shadow-sm">
          {advisoryText}
        </div>
      ) : null}

      {/* Vulnerable Zones */}
      {(data.affected_zones || []).length > 0 && (
        <div>
          <div className="text-[9px] text-secondary font-bold uppercase tracking-widest mb-2">
            Vulnerable Areas Nearby
          </div>
          <ul className="space-y-1.5 max-h-20 overflow-y-auto pr-1">
            {data.affected_zones.map((zone, i) => (
              <li
                key={i}
                className="flex items-center justify-between bg-white/60 rounded-md px-2 py-1 text-[11px]"
              >
                <span className="truncate max-w-[160px] text-on-surface-variant">{zone.name}</span>
                <span className="font-bold text-on-surface ml-2 shrink-0">
                  {zone.population.toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
