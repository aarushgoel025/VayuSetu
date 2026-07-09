import React, { useEffect, useState } from 'react';
import { getAttribution } from '../api/client';
import { Info } from 'lucide-react';

export default function FingerprintList({ lat, lng }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getAttribution(lat, lng)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [lat, lng]);

  if (loading) {
    return (
      <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft animate-pulse">
        <div className="h-5 bg-surface-container-highest rounded w-1/2 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-8 bg-surface-container-highest rounded w-full"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!data) return null;

  const getBarColor = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes('construction')) return 'bg-primary';
    if (lower.includes('traffic') || lower.includes('isbt')) return 'bg-secondary';
    if (lower.includes('power') || lower.includes('industrial') || lower.includes('thermal')) return 'bg-tertiary';
    return 'bg-primary-container';
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-headline-sm text-base font-bold text-on-surface">Pollution Fingerprint</h3>
        <Info className="w-4 h-4 text-outline" />
      </div>
      
      <div className="space-y-4 mb-4">
        {data.fingerprint.sort((a,b) => b.contribution_pct - a.contribution_pct).map((item, idx) => (
          <div key={idx} className="w-full">
            <div className="flex justify-between text-xs mb-1.5 font-medium text-on-surface-variant">
              <span className="truncate pr-2">{item.source_name}</span>
              <span className="font-bold text-on-surface">{item.contribution_pct}%</span>
            </div>
            <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${getBarColor(item.source_name)}`}
                style={{ width: `${item.contribution_pct}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="text-xs text-on-surface-variant italic bg-surface-container-low p-3 rounded-lg border-l-2 border-primary">
        {data.explanation}
      </div>
    </div>
  );
}
