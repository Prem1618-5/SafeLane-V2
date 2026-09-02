import React from 'react';
import { AlertCircle, AlertTriangle, Info } from 'lucide-react';

export default function SecurityAlert({ finding }) {
  const { severity, title, description, file, remediation } = finding;
  
  let Icon = Info;
  let colors = 'bg-blue-50 border-blue-200 text-blue-800';
  let iconColor = 'text-blue-500';
  
  if (severity === 'critical') {
    Icon = AlertCircle;
    colors = 'bg-red-50 border-red-200 text-red-800';
    iconColor = 'text-red-500';
  } else if (severity === 'warning') {
    Icon = AlertTriangle;
    colors = 'bg-amber-50 border-amber-200 text-amber-800';
    iconColor = 'text-amber-500';
  }

  return (
    <article className={`rounded-xl border p-4 sm:p-5 ${colors}`}>
      <div className="flex gap-3">
        <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${iconColor}`} aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-bold leading-5">{title}</h3>
            <span className="rounded-full border border-current/20 bg-white/50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.12em]">
              {severity}
            </span>
          </div>
          <p className="mt-1.5 text-sm leading-6 opacity-90">{description}</p>
          {(file || remediation || finding.reference) && (
            <div className="mt-3 space-y-2 border-t border-current/10 pt-3 text-sm leading-5">
              {file && (
                <p className="min-w-0 overflow-wrap-anywhere font-mono text-xs opacity-80">
                  <span className="font-sans font-semibold">File: </span>{file}
                </p>
              )}
              {remediation && (
                <p><span className="font-semibold">Recommended fix: </span>{remediation}</p>
              )}
              {finding.reference && (
                <p>
                  <a 
                    href={finding.reference} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 font-semibold underline underline-offset-2 hover:opacity-80"
                  >
                    Reference ↗
                  </a>
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
