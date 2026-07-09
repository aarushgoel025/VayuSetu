import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const getZoneColor = (type) => {
  switch(type) {
    case 'school': return '#eab308'; // Yellow/Amber
    case 'hospital': return '#dc2626'; // Red
    case 'old_age_home': return '#ea580c'; // Orange
    default: return '#505f76'; // Grey
  }
};

export default function ZoneMarker({ zone }) {
  const color = getZoneColor(zone.type);

  const createIcon = () => {
    const htmlString = `
      <div style="
        width: 14px;
        height: 14px;
        background-color: ${color};
        border-radius: 4px;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
      "></div>
    `;

    return new L.DivIcon({
      className: 'custom-zone-icon',
      html: htmlString,
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });
  };

  return (
    <Marker position={[zone.lat, zone.lng]} icon={createIcon()}>
      <Popup>
        <div className="p-1 text-on-surface min-w-[160px]">
          <h3 className="font-bold text-sm mb-0.5 text-on-surface">{zone.name}</h3>
          <div className="text-[10px] uppercase tracking-wider text-secondary">
            Type: {zone.type.replace('_', ' ')}
          </div>
          <div className="text-[11px] font-bold text-tertiary mt-1">
            Population: {Number(zone.population).toLocaleString()}
          </div>
        </div>
      </Popup>
    </Marker>
  );
}
