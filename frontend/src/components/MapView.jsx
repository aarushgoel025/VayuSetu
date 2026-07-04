import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getStations, getSources, getVulnerableZones } from '../api/client';
import StationMarker from './StationMarker';
import SourceMarker from './SourceMarker';
import ZoneMarker from './ZoneMarker';

const MapController = () => {
  const map = useMap();
  useEffect(() => {
    // Custom dark mode map controls or attributions can go here
  }, [map]);
  return null;
};

export default function MapView({ layerState, onStationSelect }) {
  const [stations, setStations] = useState([]);
  const [sources, setSources] = useState([]);
  const [zones, setZones] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stData, srcData, zoneData] = await Promise.all([getStations(), getSources(), getVulnerableZones()]);
        setStations(stData);
        setSources(srcData);
        if (zoneData) setZones(zoneData);
      } catch (err) {
        console.error("Error fetching map data", err);
      }
    };
    fetchData();
    // Refresh every 60s to pick up new AQI readings
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <MapContainer 
      center={[28.6, 77.2]} 
      zoom={10} 
      style={{ height: '100%', width: '100%' }}
      zoomControl={false}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
      />
      <MapController />
      
      {layerState.stations && stations.map(station => (
        <StationMarker 
          key={station.id} 
          station={station} 
          onClick={() => onStationSelect(station)}
        />
      ))}

      {layerState.sources && sources.map(source => (
        <SourceMarker 
          key={source.id} 
          source={source} 
        />
      ))}

      {layerState.vulnerableZones && zones.map(zone => (
        <ZoneMarker 
          key={zone.id} 
          zone={zone} 
        />
      ))}
    </MapContainer>
  );
}
