import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { getForecast } from '../api/client';

export default function ForecastChart({ stationId }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getForecast(stationId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [stationId]);

  if (loading) {
    return <div className="h-56 bg-white rounded-xl border border-outline-variant shadow-soft animate-pulse"></div>;
  }

  return (
    <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-headline-sm text-base font-bold text-on-surface">AQI Forecast</h3>
        <div className="flex gap-1">
          <span className="w-2 h-2 rounded-full bg-primary"></span>
          <span className="w-2 h-2 rounded-full bg-surface-container-highest"></span>
        </div>
      </div>
      
      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 0, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#004ac6" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#004ac6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e3e5" vertical={false} />
            <XAxis 
              dataKey="hour" 
              stroke="#737686" 
              fontSize={10} 
              tickMargin={10}
              interval={4}
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              stroke="#737686" 
              fontSize={10} 
              axisLine={false}
              tickLine={false}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e0e3e5', color: '#191c1e', borderRadius: '8px', fontSize: '12px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}
              itemStyle={{ color: '#004ac6', fontWeight: 'bold' }}
            />
            
            <ReferenceLine y={100} stroke="#eab308" strokeDasharray="3 3" />
            <ReferenceLine y={200} stroke="#ba1a1a" strokeDasharray="3 3" />
            
            <Area 
              type="monotone" 
              dataKey="aqi" 
              stroke="#004ac6" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorAqi)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
