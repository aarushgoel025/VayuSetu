import React from 'react';
import { X } from 'lucide-react';
import FingerprintList from './FingerprintList';
import ForecastChart from './ForecastChart';
import HarmScoreCard from './HarmScoreCard';
import LegalAdvisoryCard from './LegalAdvisoryCard';
import EmissionsCard from './EmissionsCard';
import ViolationHistoryPanel from './ViolationHistoryPanel';

export default function SidePanel({ station, onClose }) {
  if (!station) return null;

  const getAqiColor = (aqi) => {
    if (aqi <= 50) return 'text-vayu-green';
    if (aqi <= 100) return 'text-vayu-yellow';
    if (aqi <= 200) return 'text-vayu-orange';
    if (aqi <= 300) return 'text-vayu-red';
    return 'text-vayu-maroon';
  };

  return (
    <div className="h-full flex flex-col bg-vayu-charcoal/95 backdrop-blur-lg overflow-hidden">
      <div className="p-5 border-b border-gray-700 flex justify-between items-center bg-black/20">
        <div>
          <h2 className="text-2xl font-bold tracking-wide">{station.name}</h2>
          <div className="text-gray-400 text-sm mt-1">
            Current AQI: <span className={`font-bold text-lg ${getAqiColor(station.aqi)}`}>{station.aqi}</span>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="p-2 hover:bg-white/10 rounded-full transition-colors"
        >
          <X className="w-6 h-6 text-gray-400 hover:text-white" />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        <ForecastChart stationId={station.id} />
        <FingerprintList lat={station.lat} lng={station.lng} />
        <HarmScoreCard lat={station.lat} lng={station.lng} />
        <LegalAdvisoryCard lat={station.lat} lng={station.lng} />
        <EmissionsCard lat={station.lat} lng={station.lng} />
      </div>
    </div>
  );
}
