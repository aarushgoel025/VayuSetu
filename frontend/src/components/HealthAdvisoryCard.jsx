import React, { useEffect, useState } from 'react';
import { getHealthAdvisory } from '../api/client';
import { Wind, AlertTriangle, CheckCircle, Info } from 'lucide-react';

// AQI → colour + label helpers
function getAqiBand(aqi) {
  if (aqi <= 50)  return { bg: 'bg-emerald-500/20', border: 'border-emerald-500/40', text: 'text-emerald-400', label: 'Good',     icon: CheckCircle  };
  if (aqi <= 100) return { bg: 'bg-yellow-500/20',  border: 'border-yellow-500/40',  text: 'text-yellow-400', label: 'Satisfactory', icon: Info       };
  if (aqi <= 200) return { bg: 'bg-orange-500/20',  border: 'border-orange-500/40',  text: 'text-orange-400', label: 'Moderate',  icon: Info          };
  if (aqi <= 300) return { bg: 'bg-red-500/20',     border: 'border-red-500/40',     text: 'text-red-400',    label: 'Poor',      icon: AlertTriangle  };
  return           { bg: 'bg-purple-500/20',  border: 'border-purple-500/40',  text: 'text-purple-400', label: 'Severe',    icon: AlertTriangle  };
}

export default function HealthAdvisoryCard({ stationId, lat, lng }) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [lang, setLang]       = useState('english'); // 'english' | 'hinglish'

  useEffect(() => {
    if (!stationId) return;
    setLoading(true);
    getHealthAdvisory(stationId, lat, lng)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [stationId, lat, lng]);

  // ── Loading skeleton ────────────────────────────────────
  if (loading) {
    return (
      <div className="bg-black/20 p-4 rounded-lg border border-gray-700 animate-pulse space-y-3">
        <div className="h-4 bg-gray-600 rounded w-1/3" />
        <div className="h-16 bg-gray-600 rounded w-full" />
        <div className="h-4 bg-gray-600 rounded w-2/3" />
      </div>
    );
  }

  if (!data) return null;

  const band    = getAqiBand(data.current_aqi);
  const Icon    = band.icon;
  const text    = lang === 'english' ? data.english : data.hinglish;
  const isHindi = lang === 'hinglish';

  return (
    <div className={`rounded-lg border ${band.border} ${band.bg} p-4`}>
      {/* ── Header row ───────────────────────────────────── */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Wind className={`w-4 h-4 ${band.text}`} />
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300">
            Health Advisory
          </h3>
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${band.bg} ${band.text} border ${band.border}`}>
            {band.label}
          </span>
        </div>

        {/* ── EN / HI toggle pill ──────────────────────── */}
        <div className="flex items-center bg-black/30 rounded-full p-0.5 border border-gray-700">
          <button
            onClick={() => setLang('english')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all duration-200 ${
              !isHindi
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setLang('hinglish')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all duration-200 ${
              isHindi
                ? 'bg-orange-500 text-white shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            HI
          </button>
        </div>
      </div>

      {/* ── Advisory text ────────────────────────────────── */}
      <div className="flex gap-3">
        <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${band.text}`} />
        <p className={`text-sm leading-relaxed ${isHindi ? 'text-amber-100' : 'text-gray-200'}`}>
          {text}
        </p>
      </div>

      {/* ── Trend footnote ───────────────────────────────── */}
      <div className="mt-3 text-xs text-gray-500 italic border-t border-gray-700/50 pt-2">
        <span className="font-semibold text-gray-400">Forecast: </span>
        {data.forecast_trend}
      </div>

      {/* ── Language label ───────────────────────────────── */}
      <div className="mt-1 text-right">
        <span className="text-[10px] text-gray-600 uppercase tracking-widest">
          {isHindi ? 'Hinglish Advisory' : 'English Advisory'}
        </span>
      </div>
    </div>
  );
}
