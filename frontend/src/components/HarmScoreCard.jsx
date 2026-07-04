import React, { useEffect, useState } from 'react';
import { Users, Activity } from 'lucide-react';
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
    return <div className="h-32 bg-black/20 rounded-lg animate-pulse border border-gray-700"></div>;
  }

  if (!data) return null;

  const getColor = (val, threshold1, threshold2) => {
    if (val > threshold2) return 'text-vayu-red';
    if (val > threshold1) return 'text-vayu-amber';
    return 'text-vayu-green';
  };

  return (
    <div className="bg-black/20 p-4 rounded-lg border border-gray-700">
      <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 mb-4 border-b border-gray-600 pb-2 flex justify-between items-center">
        Vulnerability Impact
        <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-white">Score: {data.harm_score}</span>
      </h3>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white/5 p-3 rounded border border-white/10 flex flex-col items-center">
          <Users className="w-5 h-5 text-gray-400 mb-1" />
          <div className={`text-2xl font-bold ${getColor(data.children_exposed, 100, 500)}`}>
            {data.children_exposed.toLocaleString()}
          </div>
          <div className="text-xs text-gray-400 uppercase tracking-wider">Children Exposed</div>
        </div>
        
        <div className="bg-white/5 p-3 rounded border border-white/10 flex flex-col items-center">
          <Activity className="w-5 h-5 text-gray-400 mb-1" />
          <div className={`text-2xl font-bold ${getColor(data.patients_exposed, 100, 500)}`}>
            {data.patients_exposed.toLocaleString()}
          </div>
          <div className="text-xs text-gray-400 uppercase tracking-wider">Patients at Risk</div>
        </div>
      </div>

      <div className="text-xs">
        <div className="text-gray-400 uppercase mb-2 font-medium tracking-wide">Key Affected Zones</div>
        <ul className="space-y-1 max-h-40 overflow-y-auto pr-2 custom-scrollbar">
          {data.affected_zones.map((zone, i) => (
            <li key={i} className="flex justify-between border-b border-gray-800 pb-1">
              <span className="text-gray-200">{zone.name} <span className="text-gray-500 italic text-[10px]">({zone.type.replace('_', ' ')})</span></span>
              <span className="text-vayu-amber">{zone.population}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
