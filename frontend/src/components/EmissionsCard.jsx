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
        .then((summaryData) => {
            const topId =
                summaryData.top_emitters.length > 0
                    ? summaryData.top_emitters[0].source_id
                    : "s1";

            setSummary(summaryData);
            return getEmissions(topId, lat, lng);
        })
        .then((emissionsData) => {
            setData(emissionsData);
        })
        .catch(console.error)
        .finally(() => setLoading(false));
  }, [lat, lng]);

  if (loading) {
    return <div className="h-56 bg-white rounded-xl border border-outline-variant shadow-soft animate-pulse"></div>;
  }

  if (!data || !summary) return null;

  return (
    <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft">
      <h3 className="font-headline-sm text-base font-bold text-on-surface mb-4">
        Carbon Footprint
      </h3>

      <div className="flex items-center justify-between mb-4 bg-surface-container-low p-3 rounded-lg border border-outline-variant/30">
        <div>
          <div className="text-secondary text-[11px] uppercase tracking-wider font-bold">CO2 Today</div>
          <div className="text-2xl font-bold text-on-surface">
            {data.co2_tonnes_today.toLocaleString()}{' '}
            <span className="text-xs font-normal text-secondary">tonnes</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-secondary text-[11px] uppercase tracking-wider font-bold flex items-center justify-end">
            <Leaf className="w-3 h-3 text-primary mr-1" />
            Trees Needed
          </div>
          <div className="text-2xl font-bold text-primary">{data.equivalent_trees_needed.toLocaleString()}</div>
        </div>
      </div>

      <div className="h-32 w-full mb-3">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={summary.top_emitters} layout="vertical" margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
            <XAxis type="number" hide />
            <YAxis 
              dataKey="name" 
              type="category" 
              width={100} 
              tick={{ fontSize: 9, fill: '#505f76', fontWeight: '500' }} 
              axisLine={false} 
              tickLine={false} 
            />
            <Tooltip 
              cursor={{ fill: 'rgba(0, 0, 0, 0.02)' }}
              contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e0e3e5', color: '#191c1e', borderRadius: '8px', fontSize: '11px' }}
            />
            <Bar dataKey="tonnes" fill="#004ac6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="text-xs text-on-surface-variant italic bg-surface-container-low p-2.5 rounded-lg border border-outline-variant/30">
        {summary.insight_text}
      </div>
    </div>
  );
}
