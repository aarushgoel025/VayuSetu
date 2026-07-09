import React, { useEffect, useState } from 'react';
import { getHarmScore } from '../api/client';

export default function HarmScoreCard({ lat, lng }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getHarmScore(lat, lng)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [lat, lng]);

  if (loading) {
    return <div className="h-44 bg-primary/5 rounded-xl border border-primary/20 animate-pulse"></div>;
  }

  if (!data) return null;

  return (
    <div className="bg-primary/5 p-5 rounded-xl border border-primary/20 flex flex-col justify-between">
      <div className="mb-4">
        <span className="font-label-md text-xs font-bold text-primary uppercase tracking-wider">Active Health Advisory</span>
      </div>
      
      <div className="grid grid-cols-3 gap-3 mb-4 text-center">
        <div className="flex flex-col items-center">
          <span className="text-2xl font-bold text-on-surface">{data.children_exposed >= 1000 ? `${(data.children_exposed / 1000).toFixed(0)}k` : data.children_exposed}</span>
          <span className="text-[10px] text-secondary font-bold uppercase mt-1">Children</span>
        </div>
        <div className="flex flex-col items-center border-x border-outline-variant/50">
          <span className="text-2xl font-bold text-on-surface">{data.patients_exposed >= 1000 ? `${(data.patients_exposed / 1000).toFixed(0)}k` : data.patients_exposed}</span>
          <span className="text-[10px] text-secondary font-bold uppercase mt-1">Seniors</span>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-2xl font-bold text-on-surface">{data.affected_zones.filter(z => z.type === 'hospital').length || 1}</span>
          <span className="text-[10px] text-secondary font-bold uppercase mt-1">Hospitals</span>
        </div>
      </div>

      <div className="bg-white/50 p-3 rounded-lg border border-outline-variant/30 shadow-sm">
        <p className="text-xs text-primary font-medium italic">
          "Current PM2.5 levels near central district exceed pediatric safety thresholds by 15%."
        </p>
      </div>

      <div className="text-[11px] mt-3">
        <div className="text-secondary font-bold uppercase mb-1.5 tracking-wide">Key Vulnerable Areas</div>
        <ul className="space-y-1 max-h-24 overflow-y-auto pr-1">
          {data.affected_zones.map((zone, i) => (
            <li key={i} className="flex justify-between border-b border-outline-variant/20 pb-1 text-on-surface-variant text-[11px]">
              <span className="truncate max-w-[150px]">{zone.name}</span>
              <span className="font-bold text-on-surface">{zone.population} pop</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
