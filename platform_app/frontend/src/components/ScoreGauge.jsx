import React from 'react';

export default function ScoreGauge({ score }) {
  const normalizedScore = Math.min(100, Math.max(0, score || 0));
  
  // Calculate SVG circle properties
  const size = 120;
  const strokeWidth = 10;
  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let colorClass = 'text-gray-200';
  if (normalizedScore >= 80) colorClass = 'text-emerald-500';
  else if (normalizedScore >= 50) colorClass = 'text-amber-500';
  else colorClass = 'text-red-500';

  return (
    <div className="relative flex flex-col items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={center}
          cy={center}
          r={radius}
          className="text-gray-100"
          strokeWidth={strokeWidth}
          stroke="currentColor"
          fill="transparent"
        />
        <circle
          cx={center}
          cy={center}
          r={radius}
          className={colorClass}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-3xl font-bold text-slate-800">{normalizedScore}</span>
        <span className="text-xs text-slate-500 font-medium">SCORE</span>
      </div>
    </div>
  );
}
