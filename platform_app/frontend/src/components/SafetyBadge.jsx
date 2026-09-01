import React from 'react';

export default function SafetyBadge({ status }) {
  const isGreenlight = status === 'GREENLIGHT' || status === 'pass';
  const isBlocked = status === 'BLOCKED' || status === 'critical';
  const isWarning = status === 'warning';
  
  let bgClass = 'bg-gray-100 text-gray-800';
  let dotClass = 'bg-gray-400';
  
  if (isGreenlight) {
    bgClass = 'bg-emerald-100 text-emerald-800';
    dotClass = 'bg-emerald-500';
  } else if (isBlocked) {
    bgClass = 'bg-red-100 text-red-800';
    dotClass = 'bg-red-500';
  } else if (isWarning) {
    bgClass = 'bg-amber-100 text-amber-800';
    dotClass = 'bg-amber-500';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${bgClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`}></span>
      {status}
    </span>
  );
}
