import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle2, AlertTriangle, Info, BrainCircuit, ShieldAlert, FileSearch, Rocket } from 'lucide-react';

const moduleIcons = {
  'Change Intelligence': BrainCircuit,
  'Incident Memory': ShieldAlert,
  'Verification Readiness': FileSearch,
  'Release Context': Rocket
};

const moduleLabels = {
  change_intelligence: 'Change Intelligence',
  incident_memory: 'Incident Memory',
  verification_readiness: 'Verification Readiness',
  release_context: 'Release Context',
};

export default function EvidenceCard({ moduleName, status, riskModifier, findings, recommendation, idx = 0 }) {
  const displayName = moduleLabels[moduleName] || moduleName || 'Safety evidence';
  const Icon = moduleIcons[displayName] || Info;
  
  let StatusIcon = Info;
  let statusColor = 'text-blue-500';
  let badgeClasses = 'bg-blue-50 text-blue-700 border-blue-200';
  let statusText = 'INFO';
  
  if (status === 'pass') {
    StatusIcon = CheckCircle2;
    statusColor = 'text-emerald-500';
    badgeClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    statusText = 'PASS';
  } else if (status === 'critical') {
    StatusIcon = AlertCircle;
    statusColor = 'text-red-500';
    badgeClasses = 'bg-red-50 text-red-700 border-red-200';
    statusText = 'CRITICAL';
  } else if (status === 'warning') {
    StatusIcon = AlertTriangle;
    statusColor = 'text-amber-500';
    badgeClasses = 'bg-amber-50 text-amber-700 border-amber-200';
    statusText = 'WARNING';
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.05, duration: 0.28, ease: 'easeOut' }}
      whileHover={{ y: -2 }}
      className="relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-2.5 text-slate-700 shadow-sm">
            <Icon className="h-5 w-5" aria-hidden="true" />
          </div>
          <h3 className="text-base font-semibold text-slate-800">{displayName}</h3>
        </div>
        <div className={`shrink-0 rounded-md border px-2.5 py-1 text-xs font-bold tracking-wide ${badgeClasses}`}>
          {statusText}
        </div>
      </div>

      <div className="mt-1 flex-1 space-y-4">
        {findings && findings.length > 0 ? (
          <ul className="space-y-3">
            {findings.map((finding, index) => (
              <motion.li 
                initial={{ opacity: 0, x: -4 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: (idx * 0.05) + (index * 0.04) + 0.12 }}
                key={index} 
                className="flex gap-3 text-sm leading-6 text-slate-600"
              >
                <StatusIcon className={`mt-1 h-4 w-4 shrink-0 ${statusColor}`} aria-hidden="true" />
                <span className="min-w-0 overflow-wrap-anywhere">{finding}</span>
              </motion.li>
            ))}
          </ul>
        ) : (
          <p className="px-2 text-sm italic text-slate-500">No specific findings recorded.</p>
        )}
      </div>

      {recommendation && (
        <div className="-mx-5 -mb-5 mt-5 border-t border-slate-100 bg-slate-50/50 px-5 pb-5 pt-4">
          <div className="mb-1.5 text-[11px] font-bold uppercase tracking-widest text-slate-400">Recommendation</div>
          <p className="text-sm leading-6 text-slate-700">{recommendation}</p>
        </div>
      )}
      
      {riskModifier > 0 && (
         <div className="absolute right-4 top-[4.5rem] rounded border border-slate-100 bg-white/80 px-2 py-1 font-mono text-xs font-medium tabular-nums text-slate-400 backdrop-blur-sm">
           Points: -{Number(riskModifier).toFixed(1).replace(/\.0$/, '')}
         </div>
      )}
    </motion.div>
  );
}
