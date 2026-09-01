import React, { useState } from 'react';
import { Terminal, Copy, Check } from 'lucide-react';

export default function RollbackPlaybook({ playbook }) {
  const [copied, setCopied] = useState(false);

  if (!playbook) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(playbook);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-700 shadow-lg">
      <div className="bg-slate-800 px-4 py-2 flex justify-between items-center border-b border-slate-700">
        <div className="flex items-center gap-2 text-slate-300 text-sm font-medium">
          <Terminal className="w-4 h-4" />
          Rollback Commands
        </div>
        <button 
          onClick={handleCopy}
          className="text-slate-400 hover:text-white transition-colors p-1 rounded hover:bg-slate-700"
          title="Copy to clipboard"
        >
          {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="text-slate-300 font-mono text-sm whitespace-pre-wrap">
          {playbook}
        </pre>
      </div>
    </div>
  );
}
