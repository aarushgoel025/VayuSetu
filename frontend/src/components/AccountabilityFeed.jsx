import React, { useState, useEffect } from 'react';
import { getAccountabilityFeed } from '../api/client';
import { AlertTriangle } from 'lucide-react';

export default function AccountabilityFeed() {
  const [feed, setFeed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const data = await getAccountabilityFeed();
        setFeed(data);
        setError(false);
      } catch (err) {
        console.error("Failed to fetch feed", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchFeed();
    const interval = setInterval(fetchFeed, 300000); // 5 mins
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="w-full h-8 bg-surface-container-low border-b border-outline-variant flex items-center px-4 animate-pulse">
        <div className="h-3.5 bg-outline-variant rounded w-1/3"></div>
      </div>
    );
  }

  if (error || !feed) return null;

  return (
    <div className="w-full h-8 bg-error-container border-b border-error/10 flex items-center px-4 overflow-hidden z-50">
      <div className="flex items-center space-x-2 text-on-error-container font-bold text-xs whitespace-nowrap overflow-hidden text-ellipsis">
        <AlertTriangle className="w-3.5 h-3.5 text-error shrink-0" />
        <span className="tracking-wider uppercase">{feed.summary_text}</span>
      </div>
    </div>
  );
}
