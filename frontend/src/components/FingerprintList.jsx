import React, { useEffect, useState } from 'react';
import { getAttribution } from '../api/client';

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
      <div className="bg-black/20 p-4 rounded-lg border border-gray-700 animate-pulse">
        <div className="h-5 bg-gray-600 rounded w-1/2 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-8 bg-gray-600 rounded w-full"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-black/20 p-4 rounded-lg border border-gray-700">
      <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 mb-3 border-b border-gray-600 pb-2">Pollution Sources Right Now</h3>
      
      <div className="space-y-3 mb-4">
        {data.fingerprint.sort((a,b) => b.contribution_pct - a.contribution_pct).map((item, idx) => (
          <div key={idx} className="w-full">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-medium text-gray-200 truncate pr-2">{item.source_name}</span>
              <span className="text-vayu-amber font-bold">{item.contribution_pct}%</span>
            </div>
            <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-vayu-amber rounded-full" 
                style={{ width: `${item.contribution_pct}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="text-xs text-gray-400 italic bg-white/5 p-2 rounded border-l-2 border-vayu-amber">
        {data.explanation}
      </div>
    </div>
  );
}
