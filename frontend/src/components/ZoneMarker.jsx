import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const getZoneColor = (type) => {
  switch(type) {
    case 'school': return '#FFC107'; // Yellow
    case 'hospital': return '#DC3545'; // Red
    case 'old_age_home': return '#FD7E14'; // Orange
    default: return '#6C757D'; // Grey
  }
};

export default function ZoneMarker({ zone }) {
  const color = getZoneColor(zone.type);

  const createIcon = () => {
    const htmlString = `
      <div style="
        width: 16px;
        height: 16px;
        background-color: ${color};
        border-radius: 4px;
        border: 1px solid #ffffff;
        box-shadow: 0 0 5px rgba(0,0,0,0.5);
      "></div>
    `;

    return new L.DivIcon({
      className: 'custom-zone-icon',
      html: htmlString,
      iconSize: [16, 16],
      iconAnchor: [8, 8],
    });
  };

  return (
    <Marker position={[zone.lat, zone.lng]} icon={createIcon()}>
      <Popup className="dark-popup">
        <div className="bg-vayu-charcoal p-2 rounded text-white min-w-[150px]">
          <h3 className="font-bold text-sm mb-1">{zone.name}</h3>
          <div className="text-[10px] uppercase tracking-wider text-gray-400">
            Type: {zone.type.replace('_', ' ')}
          </div>
          <div className="text-[10px] text-vayu-amber mt-1">
            Population: {zone.population}
          </div>
        </div>
      </Popup>
    </Marker>
  );
}
