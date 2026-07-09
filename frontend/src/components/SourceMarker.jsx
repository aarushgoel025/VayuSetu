import React, { useState } from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import ViolationHistoryPanel from './ViolationHistoryPanel';

const getSourceColor = (type) => {
  switch(type) {
    case 'thermal_plant': return '#ba1a1a'; // Primary Red
    case 'industrial': return '#ea580c'; // Orange
    case 'construction': return '#eab308'; // Yellow/Amber
    case 'traffic_corridor': return '#004ac6'; // Primary Blue
    default: return '#505f76'; // Secondary Grey
  }
};

export default function SourceMarker({ source }) {
  const [showHistory, setShowHistory] = useState(false);
  const color = getSourceColor(source.type);

  const createIcon = () => {
    const htmlString = `
      <div style="
        width: 18px;
        height: 18px;
        background-color: ${color};
        transform: rotate(45deg);
        border: 2px solid #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
      "></div>
    `;

    return new L.DivIcon({
      className: 'custom-source-icon',
      html: htmlString,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    });
  };

  return (
    <Marker position={[source.lat, source.lng]} icon={createIcon()}>
      <Popup maxWidth={350}>
        <div className="p-2 text-on-surface min-w-[220px]">
          <h3 className="font-bold text-base mb-0.5 text-on-surface">{source.name}</h3>
          <div className="text-[10px] uppercase tracking-wider text-secondary mb-2.5 border-b border-outline-variant/30 pb-1">
            Type: {source.type.replace('_', ' ')}
          </div>
          
          {!showHistory ? (
            <button 
              onClick={(e) => { e.stopPropagation(); setShowHistory(true); }}
              className="w-full py-1.5 bg-primary text-white rounded-lg shadow-sm hover:brightness-110 active:scale-95 transition-all text-xs font-bold uppercase tracking-wider"
            >
              Violation History
            </button>
          ) : (
            <div className="mt-1">
              <button 
                onClick={(e) => { e.stopPropagation(); setShowHistory(false); }}
                className="text-[11px] font-bold text-primary hover:underline mb-2 flex items-center"
              >
                ← Back
              </button>
              <div className="max-h-[160px] overflow-y-auto pr-1">
                <ViolationHistoryPanel sourceId={source.id} hideLeaderboard={true} />
              </div>
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
}
