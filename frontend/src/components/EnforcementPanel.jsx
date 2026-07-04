import React, { useState, useEffect } from 'react';
import { ChevronUp, ChevronDown, Download, ShieldAlert, CheckCircle } from 'lucide-react';
import { getSources, generateNotice, getAttribution } from '../api/client';

export default function EnforcementPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [sources, setSources] = useState([]);
  const [generatingFor, setGeneratingFor] = useState(null);
  const [successFor, setSuccessFor] = useState(null);

  useEffect(() => {
    // In a real app, this would get a master list of all sources sorted by current impact.
    // For this mock, we fetch sources and attribution and merge them.
    const fetchData = async () => {
      try {
        const [srcData, attrData] = await Promise.all([
          getSources(),
          getAttribution(28.6, 77.2) // center of Delhi
        ]);
        
        // Merge and sort
        const enriched = srcData.map(src => {
          const match = attrData.fingerprint.find(f => f.source_id === src.id);
          return {
            ...src,
            contribution_pct: match ? match.contribution_pct : (Math.random() * 5).toFixed(1),
            people_exposed: match ? Math.floor(match.contribution_pct * 800) : Math.floor(Math.random() * 1000)
          };
        }).sort((a, b) => b.contribution_pct - a.contribution_pct);
        
        setSources(enriched);
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, []);

  const handleGenerate = async (sourceId, sourceName) => {
    setGeneratingFor(sourceId);
    try {
      const blob = await generateNotice(sourceId);
      // Trigger download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Legal_Notice_${sourceName.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      setSuccessFor(sourceId);
      setTimeout(() => setSuccessFor(null), 3000);
    } catch (err) {
      console.error("Failed to generate notice", err);
      alert("Failed to generate notice.");
    } finally {
      setGeneratingFor(null);
    }
  };

  return (
    <div className={`bg-vayu-charcoal/95 backdrop-blur-md border-t border-gray-700 shadow-[0_-10px_40px_rgba(0,0,0,0.5)] transition-all duration-300 ease-in-out ${isOpen ? 'h-64' : 'h-12'}`}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full h-12 flex items-center justify-center space-x-2 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
      >
        <ShieldAlert className="w-5 h-5 text-vayu-amber" />
        <span className="font-bold uppercase tracking-widest text-sm">Enforcement Action Center</span>
        {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
      </button>

      <div className="h-52 overflow-y-auto px-6 pb-6">
        <table className="w-full text-left text-sm text-gray-300">
          <thead className="text-xs uppercase bg-black/20 text-gray-400 sticky top-0 backdrop-blur-md">
            <tr>
              <th className="px-4 py-3 rounded-tl-lg">Source Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3 text-right">Contribution</th>
              <th className="px-4 py-3 text-right">People Exposed</th>
              <th className="px-4 py-3 text-center rounded-tr-lg">Action</th>
            </tr>
          </thead>
          <tbody>
            {sources.map(src => (
              <tr key={src.id} className="border-b border-gray-800 hover:bg-white/5 transition-colors">
                <td className="px-4 py-3 font-medium text-white">{src.name}</td>
                <td className="px-4 py-3">
                  <span className="bg-gray-700 text-gray-200 px-2 py-1 rounded text-[10px] uppercase">{src.type.replace('_', ' ')}</span>
                </td>
                <td className="px-4 py-3 text-right text-vayu-amber font-bold">{src.contribution_pct}%</td>
                <td className="px-4 py-3 text-right">{Number(src.people_exposed).toLocaleString()}</td>
                <td className="px-4 py-3 text-center">
                  {successFor === src.id ? (
                    <span className="inline-flex items-center text-vayu-green text-xs font-bold uppercase px-3 py-1.5">
                      <CheckCircle className="w-4 h-4 mr-1" /> Sent
                    </span>
                  ) : (
                    <button 
                      onClick={() => handleGenerate(src.id, src.name)}
                      disabled={generatingFor === src.id}
                      className="inline-flex items-center bg-vayu-blue/20 hover:bg-vayu-blue/40 text-vayu-blue border border-vayu-blue/30 px-3 py-1.5 rounded transition-colors text-xs font-bold uppercase tracking-wide disabled:opacity-50"
                    >
                      {generatingFor === src.id ? (
                        <span className="animate-pulse">Generating...</span>
                      ) : (
                        <>
                          <Download className="w-3 h-3 mr-1.5" /> Notice
                        </>
                      )}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
