import React from 'react';
import { Scale } from 'lucide-react';

/**
 * LegalAdvisoryCard — now receives panelData from App.jsx.
 * No longer makes its own API call — data comes from the unified
 * /api/station-panel endpoint (legal text is now hardcoded on backend,
 * no Gemini call needed).
 */
export default function LegalAdvisoryCard({ panelData, panelLoading, lat, lng }) {
  if (panelLoading || !panelData) {
    return <div className="h-48 bg-white rounded-xl border border-outline-variant shadow-soft animate-pulse"></div>;
  }

  const data = panelData.legal || {};

  const getStatusBadge = (status) => {
    switch(status) {
      case 'issued': 
        return <span className="bg-tertiary-container text-on-tertiary-container px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">Notice Issued</span>;
      case 'pending': 
        return <span className="bg-primary-container/20 text-primary px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">Pending</span>;
      default: 
        return <span className="bg-surface-container-high text-secondary px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">None</span>;
    }
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-outline-variant shadow-soft">
      <div className="flex justify-between items-center mb-3.5 border-b border-outline-variant/30 pb-2.5">
        <h3 className="text-sm font-bold uppercase tracking-wider text-on-surface flex items-center">
          <Scale className="w-4 h-4 mr-2 text-primary" />
          Rights &amp; Guidelines
        </h3>
        {getStatusBadge(data.notice_status)}
      </div>

      <div className="space-y-3.5 text-xs text-on-surface-variant">
        <p className="leading-relaxed bg-surface-container-low p-2.5 rounded-lg border border-outline-variant/20">
          {data.citizen_rights_text}
        </p>
        <p className="leading-relaxed bg-surface-container-low p-2.5 rounded-lg border-l-2 border-primary border-y border-r border-outline-variant/20">
          {data.complaint_guidance_text}
        </p>
        
        <div className="flex items-center text-[10px] bg-primary/5 p-2 rounded-lg border border-primary/10">
          <span className="text-secondary uppercase tracking-wider mr-2 font-bold">Relevant Authority:</span>
          <span className="font-semibold text-primary">{data.relevant_authority}</span>
        </div>

        <p className="text-[10px] text-outline italic text-center mt-3">
          {data.disclaimer}
        </p>
      </div>
    </div>
  );
}
