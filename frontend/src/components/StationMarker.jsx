import React from 'react';
import { Marker, Tooltip } from 'react-leaflet';
import L from 'leaflet';

const getAqiColor = (aqi) => {
  if (aqi <= 50) return '#16a34a'; // Green
  if (aqi <= 100) return '#eab308'; // Yellow
  if (aqi <= 200) return '#ea580c'; // Orange
  if (aqi <= 300) return '#dc2626'; // Red
  return '#7f1d1d'; // Dark Red / Maroon
};

export default function StationMarker({ station, onClick }) {
  const color = getAqiColor(station.aqi);
  const isSevere = station.aqi > 200;

  const createIcon = () => {
    const htmlString = `
      <div class="${isSevere ? 'marker-pulse' : ''}" style="
        width: 30px;
        height: 30px;
        background-color: ${color};
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 2px solid #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15), 0 2px 4px -2px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: -15px;
        margin-left: -15px;
      ">
        <span style="
          transform: rotate(45deg);
          color: #ffffff;
          font-size: 10px;
          font-weight: 700;
          font-family: 'Inter', sans-serif;
        ">${station.aqi}</span>
      </div>
    `;

    return new L.DivIcon({
      className: 'custom-station-icon',
      html: htmlString,
      iconSize: [30, 30],
      iconAnchor: [0, 0],
    });
  };

  return (
    <Marker 
      position={[station.lat, station.lng]} 
      icon={createIcon()}
      eventHandlers={{ click: onClick }}
    >
      <Tooltip direction="top" offset={[0, -20]} opacity={1}>
        <div className="font-sans text-xs p-1">
          <div className="font-bold text-on-surface">{station.name}</div>
          <div className="text-secondary mt-0.5">AQI: <span style={{ color }} className="font-bold">{station.aqi}</span></div>
        </div>
      </Tooltip>
    </Marker>
  );
}
