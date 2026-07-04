import React, { useState } from 'react';
import MapView from './components/MapView';
import SidePanel from './components/SidePanel';
import EnforcementPanel from './components/EnforcementPanel';
import AccountabilityFeed from './components/AccountabilityFeed';
import LayerToggle from './components/LayerToggle';

export default function App() {
  const [selectedStation, setSelectedStation] = useState(null);
  const [layerState, setLayerState] = useState({
    stations: true,
    sources: true,
    vulnerableZones: false
  });

  return (
    <div className="w-screen h-screen flex flex-col relative overflow-hidden bg-vayu-navy text-white">
      <AccountabilityFeed />
      
      <div className="flex-1 relative flex">
        {/* Map Container */}
        <div className="flex-1 relative z-0">
          <MapView 
            layerState={layerState} 
            onStationSelect={setSelectedStation}
          />
          
          <div className="absolute top-4 right-4 z-[1000]">
            <LayerToggle layerState={layerState} setLayerState={setLayerState} />
          </div>
        </div>
        
        {/* Side Panel Drawer */}
        <div className={`h-full w-[400px] flex-shrink-0 bg-vayu-charcoal border-l border-gray-700 transition-transform duration-300 transform ${selectedStation ? 'translate-x-0' : 'translate-x-full'} absolute right-0 top-0 bottom-0 z-[1001]`}>
          <SidePanel 
            station={selectedStation} 
            onClose={() => setSelectedStation(null)} 
          />
        </div>
      </div>
      
      {/* Bottom Drawer */}
      <div className="absolute bottom-0 left-0 right-0 z-[1002] pointer-events-none">
        <div className="pointer-events-auto">
          <EnforcementPanel />
        </div>
      </div>
    </div>
  );
}
