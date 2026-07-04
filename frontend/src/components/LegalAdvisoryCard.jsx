import React, { useEffect, useState } from 'react';
import { Scale } from 'lucide-react';
import { getLegalAdvisory } from '../api/client';

export default function LegalAdvisoryCard({ lat, lng }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getLegalAdvisory(lat, lng)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [lat, lng]);

  if (loading) {
    return <div className="h-48 bg-slate-800/40 rounded-lg animate-pulse border border-slate-700"></div>;
  }

  if (!data) return null;

  const getStatusBadge = (status) => {
    switch(status) {
      case 'issued': return <span className="bg-vayu-amber/20 text-vayu-amber border border-vayu-amber/30 px-2 py-0.5 rounded text-xs font-medium tracking-wide uppercase">Notice Issued</span>;
      case 'pending': return <span className="bg-vayu-blue/20 text-vayu-blue border border-vayu-blue/30 px-2 py-0.5 rounded text-xs font-medium tracking-wide uppercase">Pending</span>;
      default: return <span className="bg-gray-700 text-gray-300 px-2 py-0.5 rounded text-xs font-medium tracking-wide uppercase">None</span>;
    }
  };

  return (
    <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700">
      <div className="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center">
          <Scale className="w-4 h-4 mr-2 text-slate-400" />
          Your Rights & How to Act
        </h3>
        {getStatusBadge(data.notice_status)}
      </div>

      <div className="space-y-3 text-sm text-slate-300">
        <p className="leading-relaxed bg-black/20 p-2 rounded">
          {data.citizen_rights_text}
        </p>
        <p className="leading-relaxed bg-black/20 p-2 rounded border-l-2 border-vayu-blue">
          {data.complaint_guidance_text}
        </p>
        
        <div className="flex items-center text-xs mt-3 bg-vayu-blue/10 p-2 rounded">
          <span className="text-slate-400 uppercase tracking-wide mr-2">Relevant Authority:</span>
          <span className="font-semibold text-vayu-blue">{data.relevant_authority}</span>
        </div>

        <p className="text-[10px] text-slate-500 italic mt-4 text-center">
          {data.disclaimer}
        </p>
      </div>
    </div>
  );
}
