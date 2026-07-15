import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * ForecastChart — receives panelData from App.jsx.
 * Shows 24h AQI forecast chart + professional English-only AI narrative.
 */
export default function ForecastChart({ panelData, panelLoading, stationId }) {
  if (panelLoading || !panelData) {
    return (
      <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft animate-pulse">
        <div className="h-5 bg-surface-container-highest rounded w-2/5 mb-4"></div>
        <div className="h-36 bg-surface-container-highest rounded"></div>
      </div>
    );
  }

  const data = panelData.forecast_chart || [];
  const narrative = panelData.forecast_narrative || '';
  const trend = panelData.forecast_trend || '';

  // Determine trend icon
  const TrendIcon = trend.includes('worsening') ? TrendingUp
    : trend.includes('improving') ? TrendingDown
    : Minus;
  const trendColor = trend.includes('worsening') ? 'text-red-500'
    : trend.includes('improving') ? 'text-emerald-500'
    : 'text-secondary';

  // Custom X-axis tick — only show HH:MM from ISO timestamps
  const formatHour = (value) => {
    if (!value) return '';
    // Handle both "HH:00" and ISO "2026-07-13T06:00:00" formats
    if (value.includes('T')) {
      const d = new Date(value);
      return `${d.getHours().toString().padStart(2, '0')}:00`;
    }
    return value;
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-on-surface">24h AQI Forecast</h3>
        <div className={`flex items-center gap-1.5 text-[10px] font-semibold ${trendColor}`}>
          <TrendIcon className="w-3.5 h-3.5" />
          <span className="capitalize">{trend.split(' — ')[0] || 'Stable'}</span>
        </div>
      </div>

      {/* Chart */}
      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 0, left: -28, bottom: 0 }}>
            <defs>
              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#004ac6" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#004ac6" stopOpacity={0}    />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8eaed" vertical={false} />
            <XAxis
              dataKey="hour"
              stroke="#9aa0ac"
              fontSize={9}
              tickMargin={8}
              interval={5}
              axisLine={false}
              tickLine={false}
              tickFormatter={formatHour}
            />
            <YAxis
              stroke="#9aa0ac"
              fontSize={9}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e0e3e5',
                borderRadius: '8px',
                fontSize: '11px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
              }}
              itemStyle={{ color: '#004ac6', fontWeight: 600 }}
              labelFormatter={formatHour}
            />
            {/* Reference lines for AQI thresholds */}
            <ReferenceLine y={100} stroke="#f59e0b" strokeDasharray="3 3" strokeWidth={1} />
            <ReferenceLine y={200} stroke="#ef4444" strokeDasharray="3 3" strokeWidth={1} />
            <Area
              type="monotone"
              dataKey="aqi"
              stroke="#004ac6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#areaGrad)"
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0, fill: '#004ac6' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Reference key */}
      <div className="flex items-center gap-4 mt-2 mb-3">
        <div className="flex items-center gap-1.5">
          <div className="w-5 border-t border-dashed border-amber-500"></div>
          <span className="text-[9px] text-secondary">Moderate (100)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-5 border-t border-dashed border-red-500"></div>
          <span className="text-[9px] text-secondary">Unhealthy (200)</span>
        </div>
      </div>

      {/* AI Narrative — English only, professional */}
      {narrative && (
        <p className="text-xs text-on-surface-variant leading-relaxed bg-surface-container-low px-3 py-2.5 rounded-lg border border-outline-variant/30">
          {narrative}
        </p>
      )}
    </div>
  );
}
