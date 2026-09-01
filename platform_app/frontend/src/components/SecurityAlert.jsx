import React from 'react';
import { AlertCircle, AlertTriangle, Info } from 'lucide-react';

export default function SecurityAlert({ finding }) {
  const { severity, title, description } = finding;
  
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
    <div className={`flex gap-3 p-4 rounded-lg border ${colors}`}>
      <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${iconColor}`} />
      <div>
        <h4 className="font-semibold text-sm mb-1">{title}</h4>
        <p className="text-sm opacity-90">{description}</p>
      </div>
    </div>
  );
}
