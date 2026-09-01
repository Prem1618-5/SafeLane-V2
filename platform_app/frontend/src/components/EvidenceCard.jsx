import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle2, AlertTriangle, Info, BrainCircuit, ShieldAlert, FileSearch, Rocket } from 'lucide-react';

const moduleIcons = {
  'Change Intelligence': BrainCircuit,
  'Incident Memory': ShieldAlert,
  'Verification Readiness': FileSearch,
  'Release Context': Rocket
};

export default function EvidenceCard({ moduleName, status, riskModifier, findings, recommendation, idx = 0 }) {
  const Icon = moduleIcons[moduleName] || Info;
  
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
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.1, duration: 0.4, ease: 'easeOut' }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 flex flex-col h-full transition-shadow hover:shadow-md relative overflow-hidden"
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-slate-50 text-slate-700 border border-slate-100 shadow-sm">
            <Icon className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-800 text-base">{moduleName}</h3>
        </div>
        <div className={`px-2.5 py-1 rounded-md text-xs font-bold tracking-wide border ${badgeClasses}`}>
          {statusText}
        </div>
      </div>

      <div className="flex-1 space-y-4 mt-2">
        {findings && findings.length > 0 ? (
          <ul className="space-y-3">
            {findings.map((finding, index) => (
              <motion.li 
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: (idx * 0.1) + (index * 0.05) + 0.2 }}
                key={index} 
                className="flex gap-3 text-sm text-slate-600 leading-relaxed"
              >
                <StatusIcon className={`w-4 h-4 mt-0.5 shrink-0 ${statusColor}`} />
                <span>{finding}</span>
              </motion.li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500 italic px-2">No specific findings recorded.</p>
        )}
      </div>

      {recommendation && (
        <div className="mt-5 pt-4 border-t border-slate-100 bg-slate-50/50 -mx-5 -mb-5 px-5 pb-5">
          <div className="text-[11px] font-bold text-slate-400 mb-1.5 uppercase tracking-widest">Recommendation</div>
          <p className="text-sm text-slate-700">{recommendation}</p>
        </div>
      )}
      
      {riskModifier !== undefined && riskModifier !== null && (
         <div className="absolute bottom-4 right-4 text-xs font-mono font-medium text-slate-400 bg-white/80 px-2 py-1 rounded border border-slate-100 backdrop-blur-sm">
           Modifier: {riskModifier > 0 ? '+' : ''}{riskModifier}
         </div>
      )}
    </motion.div>
  );
}
