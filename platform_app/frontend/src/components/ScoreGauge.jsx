import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

export default function ScoreGauge({ score, size = 120 }) {
  const normalizedScore = Math.min(100, Math.max(0, score || 0));
  const shouldReduceMotion = useReducedMotion();
  const strokeWidth = Math.max(8, Math.round(size / 12));
  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let colorClass = 'text-gray-200';
  if (normalizedScore >= 80) colorClass = 'text-emerald-500';
  else if (normalizedScore >= 50) colorClass = 'text-amber-500';
  else colorClass = 'text-red-500';

  return (
    <div
      className="relative flex flex-col items-center justify-center"
      role="img"
      aria-label={`${normalizedScore} safety score out of 100`}
    >
      <svg width={size} height={size} className="-rotate-90" aria-hidden="true">
        <circle
          cx={center}
          cy={center}
          r={radius}
          className="text-gray-100"
          strokeWidth={strokeWidth}
          stroke="currentColor"
          fill="transparent"
        />
        <motion.circle
          initial={shouldReduceMotion ? false : { strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={shouldReduceMotion ? { duration: 0 } : { type: 'spring', duration: 1.1, bounce: 0.05 }}
          cx={center}
          cy={center}
          r={radius}
          className={colorClass}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <motion.span
          initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={shouldReduceMotion ? { duration: 0 } : { delay: 0.08, type: 'spring', bounce: 0.12, duration: 0.35 }}
          className="text-3xl font-bold tabular-nums text-slate-800"
        >
          {normalizedScore}
        </motion.span>
        <span className="text-[11px] font-semibold tracking-wide text-slate-500">SCORE</span>
      </div>
    </div>
  );
}
