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
    return <div className="h-40 bg-white rounded-xl border border-outline-variant shadow-soft animate-pulse"></div>;
  }

  if (!history) return null;

  return (
    <div className="bg-white rounded-xl border border-outline-variant shadow-soft overflow-hidden">
      <div className="p-4 border-b border-outline-variant/30 flex justify-between items-center bg-surface-container-low">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-on-surface flex items-center gap-1.5">
            <span>Violation Record</span>
            {history.repeat_offender && (
              <span className="bg-error-container text-on-error-container px-2 py-0.5 rounded text-[9px] uppercase font-bold flex items-center border border-error/20">
                <AlertOctagon className="w-2.5 h-2.5 mr-1" />
                Repeat Offender
              </span>
            )}
          </h3>
          <p className="text-xs text-secondary mt-0.5">Total Notices Issued: <span className="text-on-surface font-bold">{history.total_notices}</span></p>
        </div>
      </div>

      <div className="p-4 max-h-[220px] overflow-y-auto">
        {history.notices.length === 0 ? (
          <div className="text-xs text-secondary italic text-center py-4">No violations on record.</div>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-y-0 before:left-2 before:-translate-x-px before:w-0.5 before:bg-outline-variant/50">
            {history.notices.map((notice, idx) => {
              const date = new Date(notice.generated_at).toLocaleDateString();
              return (
                <div key={idx} className="relative flex items-start pl-6 group">
                  <div className="absolute left-1 top-1.5 w-2 h-2 rounded-full border border-white bg-error shadow shrink-0"></div>
                  <div className="flex-1 bg-surface-container-low p-2.5 rounded-lg border border-outline-variant/20 shadow-sm">
                    <div className="flex items-center justify-between mb-1">
                      <div className="font-bold text-on-surface text-[11px] flex items-center">
                        <FileText className="w-3 h-3 mr-1 text-primary" /> Notice Issued
                      </div>
                      <time className="text-[10px] text-secondary font-medium">{date}</time>
                    </div>
                    <div className="text-[10px] text-on-surface-variant">
                      Contribution: <span className="text-tertiary font-bold">{notice.contribution_pct}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {!hideLeaderboard && offenders && (
        <div className="p-4 bg-surface-container-low border-t border-outline-variant/30">
          <h4 className="text-[10px] font-bold uppercase text-secondary mb-2.5 tracking-wider">NCR Repeat Offenders List</h4>
          <div className="space-y-1.5">
            {offenders.map((off, idx) => (
              <div key={idx} className="flex justify-between items-center bg-white p-2 rounded-lg border border-outline-variant/30 text-xs">
                <span className="text-on-surface font-medium truncate pr-2">{off.source_name}</span>
                <span className="bg-error-container text-on-error-container px-2 py-0.5 rounded text-[10px] font-bold font-mono">{off.notice_count} notices</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
