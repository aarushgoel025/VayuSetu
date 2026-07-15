import React from 'react';
import { CircleMarker, Tooltip } from 'react-leaflet';

/**
 * Renders a single NASA FIRMS satellite thermal hotspot.
 * Deliberately styled differently from AQI stations and emission sources:
 *   - AQI Stations:    Blue rounded pins
 *   - Emission Sources: Red/orange icons
 *   - Satellite Hotspots: Pulsing amber circles with dashed border
 *                         (space-detected, not ground-based)
 */
export default function SatelliteHotspotMarker({ hotspot }) {
  // Colour and size scale by confidence + fire radiative power
  const getStyle = (confidenceLevel, frp) => {
    const radius = Math.max(6, Math.min(20, 6 + (frp / 3)));
    if (confidenceLevel === 3) {
      // High confidence: bright amber
      return { color: '#FF6B00', fillColor: '#FF9500', fillOpacity: 0.75, radius };
    } else if (confidenceLevel === 2) {
      // Nominal: orange-yellow
      return { color: '#FFB300', fillColor: '#FFD54F', fillOpacity: 0.65, radius: radius * 0.85 };
    } else {
      // Low confidence: muted yellow
      return { color: '#FDD835', fillColor: '#FFF176', fillOpacity: 0.50, radius: radius * 0.7 };
    }
  };

  const style = getStyle(hotspot.confidence_level, hotspot.frp);

  return (
    <CircleMarker
      center={[hotspot.lat, hotspot.lng]}
      radius={style.radius}
      pathOptions={{
        color: style.color,
        fillColor: style.fillColor,
        fillOpacity: style.fillOpacity,
        weight: 1.5,
        dashArray: '4 3',         // dashed border = "not a ground sensor"
      }}
    >
      <Tooltip direction="top" offset={[0, -6]} opacity={0.95}>
        <div style={{ fontFamily: 'monospace', fontSize: '11px', lineHeight: '1.6' }}>
          <div style={{ fontWeight: 'bold', color: '#FF6B00', marginBottom: 4 }}>
            🛰 NASA FIRMS Satellite Detection
          </div>
          <div><b>Brightness:</b> {hotspot.brightness} K</div>
          <div><b>Fire Radiative Power:</b> {hotspot.frp} MW</div>
          <div><b>Confidence:</b> {hotspot.confidence}</div>
          <div><b>Acquired:</b> {hotspot.acq_date} {hotspot.acq_time}</div>
          <div><b>Satellite:</b> {hotspot.satellite}</div>
          <div style={{ marginTop: 4, color: '#888', fontSize: '10px' }}>
            Lat {hotspot.lat}, Lng {hotspot.lng}
          </div>
        </div>
      </Tooltip>
    </CircleMarker>
  );
}
