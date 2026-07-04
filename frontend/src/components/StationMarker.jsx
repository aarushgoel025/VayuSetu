import React from 'react';
import { Marker, Tooltip } from 'react-leaflet';
import L from 'leaflet';

const getAqiColor = (aqi) => {
  if (aqi <= 50) return '#28A745'; // Green
  if (aqi <= 100) return '#FFC107'; // Yellow
  if (aqi <= 200) return '#FD7E14'; // Orange
  if (aqi <= 300) return '#DC3545'; // Red
  return '#721C24'; // Maroon
};

export default function StationMarker({ station, onClick }) {
  const color = getAqiColor(station.aqi);
  const isSevere = station.aqi > 200;

  const createIcon = () => {
    const htmlString = `
      <div class="${isSevere ? 'marker-pulse' : ''}" style="
        width: 36px;
        height: 36px;
        background-color: ${color};
        border-radius: 50%;
        border: 2px solid #ffffff;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
      "></div>
    `;

    return new L.DivIcon({
      className: 'custom-station-icon',
      html: htmlString,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
  };

  return (
    <Marker 
      position={[station.lat, station.lng]} 
      icon={createIcon()}
      eventHandlers={{ click: onClick }}
    >
      <Tooltip direction="top" offset={[0, -20]} opacity={1} className="dark-tooltip">
        <div className="font-sans text-sm">
          <div className="font-bold">{station.name}</div>
          <div className="text-gray-300">AQI: <span style={{ color }} className="font-bold">{station.aqi}</span></div>
        </div>
      </Tooltip>
    </Marker>
  );
}
