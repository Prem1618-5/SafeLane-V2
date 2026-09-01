import React from 'react';

export default function SafetyBadge({ status }) {
  const isGreenlight = status === 'GREENLIGHT' || status === 'pass';
  const isBlocked = status === 'BLOCKED' || status === 'critical';
  const isWarning = status === 'warning';
  
  let bgClass = 'bg-slate-100 text-slate-700 border-slate-200';
  let dotClass = 'bg-slate-400';
  
  if (isGreenlight) {
    bgClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    dotClass = 'bg-emerald-500';
  } else if (isBlocked) {
    bgClass = 'bg-red-50 text-red-700 border-red-200';
    dotClass = 'bg-red-500';
  } else if (isWarning) {
    bgClass = 'bg-amber-50 text-amber-700 border-amber-200';
    dotClass = 'bg-amber-500';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold tracking-wide uppercase border ${bgClass}`}>
      <span className="relative flex h-1.5 w-1.5">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotClass}`}></span>
        <span className={`relative inline-flex rounded-full h-1.5 w-1.5 ${dotClass}`}></span>
      </span>
      {status}
    </span>
  );
}
