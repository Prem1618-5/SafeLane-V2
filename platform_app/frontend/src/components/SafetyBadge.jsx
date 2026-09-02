import React from 'react';

/**
 * DecisionBadge — displays greenlight/blocked verdict decisions.
 * Use for pipeline-level decisions (PRDetail, RepoDashboard, Repos).
 */
export function DecisionBadge({ decision }) {
  const normalized = (decision || '').toUpperCase();
  const isGreenlight = normalized === 'GREENLIGHT';
  const isBlocked = normalized === 'BLOCKED';
  
  let bgClass = 'bg-slate-100 text-slate-700 border-slate-200';
  let dotClass = 'bg-slate-400';
  
  if (isGreenlight) {
    bgClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    dotClass = 'bg-emerald-500';
  } else if (isBlocked) {
    bgClass = 'bg-red-50 text-red-700 border-red-200';
    dotClass = 'bg-red-500';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold tracking-wide uppercase border ${bgClass}`}>
      <span className="relative flex h-1.5 w-1.5">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotClass}`}></span>
        <span className={`relative inline-flex rounded-full h-1.5 w-1.5 ${dotClass}`}></span>
      </span>
      {normalized}
    </span>
  );
}

/**
 * EvidenceStatusBadge — displays pass/warning/critical evidence module status.
 * Use for individual evidence module results (EvidenceCard).
 */
export function EvidenceStatusBadge({ status }) {
  const normalized = (status || '').toLowerCase();
  const isPass = normalized === 'pass';
  const isCritical = normalized === 'critical';
  const isWarning = normalized === 'warning';
  
  let bgClass = 'bg-slate-100 text-slate-700 border-slate-200';
  let dotClass = 'bg-slate-400';
  
  if (isPass) {
    bgClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    dotClass = 'bg-emerald-500';
  } else if (isCritical) {
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
      {normalized}
    </span>
  );
}

// Backward-compatible default export for any remaining call sites
export default function SafetyBadge({ status }) {
  const upper = (status || '').toUpperCase();
  if (upper === 'GREENLIGHT' || upper === 'BLOCKED') {
    return <DecisionBadge decision={status} />;
  }
  return <EvidenceStatusBadge status={status} />;
}
