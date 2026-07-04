import React, { useEffect, useState } from 'react';
import { FileText, AlertOctagon } from 'lucide-react';
import { getViolationHistory, getRepeatOffenders } from '../api/client';

export default function ViolationHistoryPanel({ sourceId, hideLeaderboard = false }) {
  const [history, setHistory] = useState(null);
  const [offenders, setOffenders] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const promises = [getViolationHistory(sourceId)];
    if (!hideLeaderboard) promises.push(getRepeatOffenders());

    Promise.all(promises)
      .then(([historyData, offendersData]) => {
        setHistory(historyData);
        if (offendersData) setOffenders(offendersData.offenders);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [sourceId, hideLeaderboard]);

  if (loading) {
    return <div className="h-40 bg-black/20 rounded-lg animate-pulse border border-gray-700"></div>;
  }

  if (!history) return null;

  return (
    <div className="bg-black/20 rounded-lg border border-gray-700 overflow-hidden">
      <div className="p-4 border-b border-gray-700">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 flex items-center justify-between">
          <span>Violation History</span>
          {history.repeat_offender && (
            <span className="bg-vayu-red text-white px-2 py-0.5 rounded text-[10px] uppercase font-bold flex items-center">
              <AlertOctagon className="w-3 h-3 mr-1" />
              Repeat Offender
            </span>
          )}
        </h3>
        <p className="text-xs text-gray-400 mt-1">Total Legal Notices Issued: <span className="text-white font-bold">{history.total_notices}</span></p>
      </div>

      <div className="p-4 max-h-[250px] overflow-y-auto">
        {history.notices.length === 0 ? (
          <div className="text-sm text-gray-500 italic text-center py-4">No violations on record.</div>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-600 before:to-transparent">
            {history.notices.map((notice, idx) => {
              const date = new Date(notice.generated_at).toLocaleDateString();
              return (
                <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  <div className="flex items-center justify-center w-4 h-4 rounded-full border border-white bg-vayu-charcoal text-slate-500 group-[.is-active]:text-emerald-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 ml-[2px] md:ml-0"></div>
                  <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-white/5 p-3 rounded border border-white/10 shadow">
                    <div className="flex items-center justify-between mb-1">
                      <div className="font-bold text-gray-200 text-xs flex items-center">
                        <FileText className="w-3 h-3 mr-1" /> Notice Issued
                      </div>
                      <time className="text-[10px] text-gray-400 font-medium">{date}</time>
                    </div>
                    <div className="text-[10px] text-gray-400">
                      Contribution: <span className="text-vayu-amber">{notice.contribution_pct}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {!hideLeaderboard && offenders && (
        <div className="p-4 bg-black/40 border-t border-gray-700">
          <h4 className="text-xs font-bold uppercase text-gray-400 mb-3">Repeat Offenders Leaderboard</h4>
          <div className="space-y-2">
            {offenders.map((off, idx) => (
              <div key={idx} className="flex justify-between items-center bg-white/5 p-2 rounded text-xs">
                <span className="text-gray-300 truncate pr-2">{off.source_name}</span>
                <span className="bg-gray-700 px-2 py-0.5 rounded text-white font-mono">{off.notice_count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
