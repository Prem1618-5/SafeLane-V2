import React from 'react';
import { AlertCircle, CheckCircle2, AlertTriangle, Info, BrainCircuit, ShieldAlert, FileSearch, Rocket } from 'lucide-react';
import SafetyBadge from './SafetyBadge';

const moduleIcons = {
  'Change Intelligence': BrainCircuit,
  'Incident Memory': ShieldAlert,
  'Verification Readiness': FileSearch,
  'Release Context': Rocket
};

export default function EvidenceCard({ moduleName, status, riskModifier, findings, recommendation }) {
  const Icon = moduleIcons[moduleName] || Info;
  
  let StatusIcon = Info;
  let statusColor = 'text-blue-500';
  if (status === 'pass') {
    StatusIcon = CheckCircle2;
    statusColor = 'text-emerald-500';
  } else if (status === 'critical') {
    StatusIcon = AlertCircle;
    statusColor = 'text-red-500';
  } else if (status === 'warning') {
    StatusIcon = AlertTriangle;
    statusColor = 'text-amber-500';
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-5 flex flex-col h-full">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-md bg-slate-50 text-slate-600 border border-slate-100`}>
            <Icon className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-800">{moduleName}</h3>
        </div>
        <SafetyBadge status={status} />
      </div>

      <div className="flex-1 space-y-4">
        {findings && findings.length > 0 ? (
          <ul className="space-y-2">
            {findings.map((finding, idx) => (
              <li key={idx} className="flex gap-2 text-sm text-slate-600">
                <StatusIcon className={`w-4 h-4 mt-0.5 shrink-0 ${statusColor}`} />
                <span>{finding}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500 italic">No specific findings.</p>
        )}
      </div>

      {recommendation && (
        <div className="mt-4 pt-4 border-t border-slate-100">
          <div className="text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">Recommendation</div>
          <p className="text-sm text-slate-700">{recommendation}</p>
        </div>
      )}
      
      {riskModifier && (
         <div className="mt-2 text-xs text-right font-mono text-slate-400">
           Risk modifier: {riskModifier > 0 ? '+' : ''}{riskModifier}
         </div>
      )}
    </div>
  );
}
