import React from 'react';

export default function LayerToggle({ layerState, setLayerState }) {
  const toggleLayer = (key) => {
    setLayerState(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const layers = [
    { key: 'stations', label: 'AQI Stations' },
    { key: 'sources', label: 'Emission Sources' },
    { key: 'vulnerableZones', label: 'Vulnerable Zones' },
  ];

  return (
    <div className="glass-panel p-4 rounded-xl shadow-soft w-48">
      <p className="text-xs font-bold text-on-surface border-b border-outline-variant/30 pb-1.5 mb-3 uppercase tracking-wider">Map Layers</p>
      
      <div className="space-y-2.5">
        {layers.map(({ key, label }) => (
          <label 
            key={key} 
            className="flex items-center justify-between cursor-pointer group"
          >
            <span className="text-xs font-medium text-on-surface-variant group-hover:text-primary transition-colors">
              {label}
            </span>
            <input
              type="checkbox"
              checked={layerState[key]}
              onChange={() => toggleLayer(key)}
              className="rounded text-primary focus:ring-primary w-4 h-4 border-outline-variant cursor-pointer"
            />
          </label>
        ))}
      </div>
    </div>
  );
}
