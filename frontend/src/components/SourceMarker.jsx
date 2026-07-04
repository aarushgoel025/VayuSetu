import React, { useState } from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import ViolationHistoryPanel from './ViolationHistoryPanel';

const getSourceColor = (type) => {
  switch(type) {
    case 'thermal_plant': return '#DC3545'; // Red
    case 'industrial': return '#FD7E14'; // Orange
    case 'construction': return '#FFC107'; // Amber
    case 'traffic_corridor': return '#2E75B6'; // Blue
    default: return '#6C757D'; // Grey
  }
};

export default function SourceMarker({ source }) {
  const [showHistory, setShowHistory] = useState(false);
  const color = getSourceColor(source.type);

  const createIcon = () => {
    const htmlString = `
      <div style="
        width: 24px;
        height: 24px;
        background-color: ${color};
        transform: rotate(45deg);
        border: 2px solid #ffffff;
        box-shadow: 0 0 8px rgba(0,0,0,0.5);
      "></div>
    `;

    return new L.DivIcon({
      className: 'custom-source-icon',
      html: htmlString,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  };

  return (
    <Marker position={[source.lat, source.lng]} icon={createIcon()}>
      <Popup className="dark-popup" maxWidth={350}>
        <div className="bg-vayu-charcoal p-3 rounded text-white min-w-[200px]">
          <h3 className="font-bold text-lg mb-1">{source.name}</h3>
          <div className="text-xs uppercase tracking-wider text-gray-400 mb-3 border-b border-gray-600 pb-2">
            Type: {source.type.replace('_', ' ')}
          </div>
          
          {!showHistory ? (
            <button 
              onClick={(e) => { e.stopPropagation(); setShowHistory(true); }}
              className="w-full py-1.5 bg-vayu-blue/20 hover:bg-vayu-blue/40 text-vayu-blue rounded transition-colors text-sm font-medium"
            >
              View Violation History
            </button>
          ) : (
            <div className="mt-2">
              <button 
                onClick={(e) => { e.stopPropagation(); setShowHistory(false); }}
                className="text-xs text-gray-400 hover:text-white mb-2"
              >
                ← Back
              </button>
              <ViolationHistoryPanel sourceId={source.id} hideLeaderboard={true} />
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
}
