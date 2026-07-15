import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getStations, getSources, getVulnerableZones, getSatelliteHotspots } from '../api/client';
import StationMarker from './StationMarker';
import SourceMarker from './SourceMarker';
import ZoneMarker from './ZoneMarker';
import SatelliteHotspotMarker from './SatelliteHotspotMarker';

const MapController = () => {
  const map = useMap();
  useEffect(() => {}, [map]);
  return null;
};

export default function MapView({ layerState, onStationSelect }) {
  const [stations, setStations]   = useState([]);
  const [sources, setSources]     = useState([]);
  const [zones, setZones]         = useState([]);
  const [hotspots, setHotspots]   = useState([]);

  // Ground data: AQI stations, sources, zones — refresh every 60s
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stData, srcData, zoneData] = await Promise.all([
          getStations(), getSources(), getVulnerableZones()
        ]);
        setStations(stData);
        setSources(srcData);
        if (zoneData) setZones(zoneData);
      } catch (err) {
        console.error("Error fetching map data", err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  // Satellite data: NASA FIRMS hotspots — refresh every 5 minutes
  useEffect(() => {
    const fetchHotspots = async () => {
      try {
        const data = await getSatelliteHotspots();
        if (data?.hotspots) setHotspots(data.hotspots);
      } catch (err) {
        console.error("Error fetching satellite hotspots", err);
      }
    };
    fetchHotspots();
    const interval = setInterval(fetchHotspots, 300000); // 5 min
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
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
      />
      <MapController />

      {/* Ground-based AQI Stations */}
      {layerState.stations && stations.map(station => (
        <StationMarker
          key={station.id}
          station={station}
          onClick={() => onStationSelect(station)}
        />
      ))}

      {/* Known Emission Sources */}
      {layerState.sources && sources.map(source => (
        <SourceMarker key={source.id} source={source} />
      ))}

      {/* Vulnerable Zones */}
      {layerState.vulnerableZones && zones.map(zone => (
        <ZoneMarker key={zone.id} zone={zone} />
      ))}

      {/* 🛰 NASA FIRMS Satellite Thermal Hotspots — distinct from ground layers */}
      {layerState.satelliteHotspots && hotspots.map((h, i) => (
        <SatelliteHotspotMarker key={`sat-${i}`} hotspot={h} />
      ))}
    </MapContainer>
  );
}
