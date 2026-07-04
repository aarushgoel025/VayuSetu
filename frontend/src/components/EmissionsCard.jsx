import React, { useEffect, useState } from 'react';
import { getEmissions, getEmissionsSummary } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Leaf } from 'lucide-react';

export default function EmissionsCard({ lat, lng }) {
  const [data, setData] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getEmissionsSummary(lat, lng)
      .then(summaryData => {
        setSummary(summaryData);
        // Find the top emitter from the summary (backend now provides source_id in summary)
        const topId = summaryData.top_emitters.length > 0 ? summaryData.top_emitters[0].source_id : 's1';
        return getEmissions(topId, lat, lng);
      })
      .then(emissionsData => {
        setData(emissionsData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [lat, lng]);

  if (loading) {
    return <div className="h-56 bg-black/20 rounded-lg animate-pulse border border-gray-700"></div>;
  }

  if (!data || !summary) return null;

  return (
    <div className="bg-black/20 p-4 rounded-lg border border-gray-700 mb-8">
      <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 mb-4 border-b border-gray-600 pb-2">
        Carbon Footprint
      </h3>

      <div className="flex items-center justify-between mb-4 bg-white/5 p-3 rounded">
        <div>
          <div className="text-gray-400 text-xs uppercase tracking-wide">CO2 Today</div>
          <div className="text-2xl font-bold text-gray-100">{data.co2_tonnes_today.toLocaleString()} <span className="text-sm font-normal text-gray-400">tonnes</span></div>
        </div>
        <div className="text-right">
          <div className="text-gray-400 text-xs uppercase tracking-wide flex items-center justify-end">
            <Leaf className="w-3 h-3 text-vayu-green mr-1" />
            Trees Needed
          </div>
          <div className="text-xl font-bold text-vayu-green">{data.equivalent_trees_needed.toLocaleString()}</div>
        </div>
      </div>

      <div className="h-32 w-full mb-3">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={summary.top_emitters} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 10, fill: '#888' }} axisLine={false} tickLine={false} />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{ backgroundColor: '#1C2541', borderColor: '#333', color: '#fff', fontSize: '12px' }}
            />
            <Bar dataKey="tonnes" fill="#2E75B6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="text-xs text-gray-400 italic bg-vayu-navy p-2 rounded border border-gray-800">
        {summary.insight_text}
      </div>
    </div>
  );
}
