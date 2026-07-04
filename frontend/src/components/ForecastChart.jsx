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
    return <div className="h-48 bg-black/20 rounded-lg animate-pulse"></div>;
  }

  return (
    <div className="bg-black/20 p-4 rounded-lg border border-gray-700">
      <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 mb-4 border-b border-gray-600 pb-2">24-Hour AQI Forecast</h3>
      
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#DC3545" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#28A745" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis 
              dataKey="hour" 
              stroke="#888" 
              fontSize={10} 
              tickMargin={10}
              interval={3}
            />
            <YAxis stroke="#888" fontSize={10} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1C2541', borderColor: '#333', color: '#fff' }}
              itemStyle={{ color: '#fff' }}
            />
            
            <ReferenceLine y={100} stroke="#FFC107" strokeDasharray="3 3" />
            <ReferenceLine y={200} stroke="#DC3545" strokeDasharray="3 3" />
            
            <Area 
              type="monotone" 
              dataKey="aqi" 
              stroke="#DC3545" 
              fillOpacity={1} 
              fill="url(#colorAqi)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
