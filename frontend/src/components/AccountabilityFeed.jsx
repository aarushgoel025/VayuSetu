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
      <div className="w-full h-10 bg-vayu-charcoal border-b border-gray-700 flex items-center px-4 animate-pulse">
        <div className="h-4 bg-gray-600 rounded w-1/3"></div>
      </div>
    );
  }

  if (error || !feed) return null;

  return (
    <div className="w-full h-10 bg-vayu-navy border-b border-vayu-blue/30 flex items-center px-4 overflow-hidden z-50">
      <div className="flex items-center space-x-3 text-vayu-blue font-medium text-sm whitespace-nowrap overflow-hidden text-ellipsis">
        <AlertTriangle className="w-4 h-4 text-vayu-amber" />
        <span className="tracking-wide uppercase">{feed.summary_text}</span>
      </div>
    </div>
  );
}
