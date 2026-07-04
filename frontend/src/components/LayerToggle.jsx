import React from 'react';
import { Layers } from 'lucide-react';

export default function LayerToggle({ layerState, setLayerState }) {
  const toggleLayer = (key) => {
    setLayerState(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const layers = [
    { key: 'stations', label: 'AQI Stations' },
    { key: 'sources', label: 'Pollution Sources' },
    { key: 'vulnerableZones', label: 'Vulnerable Zones' },
  ];

  return (
    <div className="bg-vayu-charcoal/80 backdrop-blur-md border border-gray-700 rounded-lg shadow-xl p-3 w-48 text-sm">
      <div className="flex items-center space-x-2 text-gray-300 mb-3 border-b border-gray-600 pb-2">
        <Layers className="w-4 h-4" />
        <span className="font-semibold uppercase tracking-wide text-xs">Map Layers</span>
      </div>
      
      <div className="space-y-2">
        {layers.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => toggleLayer(key)}
            className={`w-full flex items-center px-3 py-1.5 rounded transition-colors duration-200 ${
              layerState[key] 
                ? 'bg-vayu-blue/20 text-vayu-blue border border-vayu-blue/50' 
                : 'bg-transparent text-gray-400 hover:bg-white/5 border border-transparent'
            }`}
          >
            <div className={`w-2 h-2 rounded-full mr-2 ${layerState[key] ? 'bg-vayu-blue' : 'bg-gray-600'}`} />
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
