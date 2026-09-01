import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';
import { ChevronRight, RefreshCw, AlertTriangle, ShieldCheck, FileWarning, ArrowLeft, FileCode, ChevronDown, ChevronUp } from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import SafetyBadge from '../components/SafetyBadge';
import EvidenceCard from '../components/EvidenceCard';
import SecurityAlert from '../components/SecurityAlert';
import RollbackPlaybook from '../components/RollbackPlaybook';
import { motion, AnimatePresence } from 'framer-motion';

export default function PRDetail() {
  const { id, pr } = useParams();
  const [data, setData] = useState(null);
  const [repoData, setRepoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showChangedFiles, setShowChangedFiles] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [prRes, repoRes] = await Promise.all([
          api.getPRDetail(id, pr),
          api.getRepoDashboard(id)
        ]);
        setData(prRes);
        setRepoData(repoRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id, pr]);

  if (loading) return <div className="flex justify-center p-10"><RefreshCw className="w-8 h-8 animate-spin text-blue-500" /></div>;
  if (error) return <div className="text-red-500 p-4 bg-red-50 rounded-lg">{error}</div>;
  if (!data) return <div>Not found</div>;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="max-w-6xl mx-auto space-y-6 pb-20"
    >
      {/* Breadcrumbs */}
      <nav className="flex items-center text-sm text-slate-500">
        <Link to="/repos" className="hover:text-blue-600 transition-colors">Repositories</Link>
        <ChevronRight className="w-4 h-4 mx-1" />
        <Link to={`/repos/${id}`} className="hover:text-blue-600 transition-colors">{repoData?.full_name || 'Repo'}</Link>
        <ChevronRight className="w-4 h-4 mx-1" />
        <span className="text-slate-800 font-medium">PR #{pr}</span>
      </nav>

      {/* Summary Banner */}
      <div className={`rounded-xl shadow-sm border p-6 md:p-8 flex flex-col md:flex-row justify-between items-center gap-6 ${data.decision === 'GREENLIGHT' ? 'bg-emerald-50 border-emerald-100' : 'bg-red-50 border-red-100'}`}>
        <div className="flex-1">
          <h2 className={`text-2xl md:text-3xl font-bold leading-tight ${data.decision === 'GREENLIGHT' ? 'text-emerald-900' : 'text-red-900'}`}>
            {data.risk_brief}
          </h2>
        </div>
        <div className="shrink-0 flex items-center gap-6 bg-white p-4 rounded-xl shadow-sm border border-slate-100">
          <div className="flex flex-col items-center">
            <div className="text-xs text-slate-500 font-medium mb-2">CONFIDENCE</div>
            <ScoreGauge score={data.confidence_score} />
          </div>
          <div className="w-px h-16 bg-slate-200"></div>
          <div className="flex flex-col items-center min-w-[120px]">
             <div className="text-xs text-slate-500 font-medium mb-2">VERDICT</div>
             <div className={`text-2xl font-black flex items-center gap-2 ${data.decision === 'GREENLIGHT' ? 'text-emerald-600' : 'text-red-600'}`}>
               {data.decision === 'GREENLIGHT' ? <ShieldCheck className="w-8 h-8" /> : <FileWarning className="w-8 h-8" />}
               <span className="uppercase">{data.decision}</span>
             </div>
          </div>
        </div>
      </div>

      {/* Header section */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link to={`/repos/${id}`} className="text-slate-400 hover:text-slate-600 transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-2xl font-bold text-slate-800">Pull Request #{data.pr_number}</h1>
            <SafetyBadge status={data.decision} />
          </div>
          <p className="text-slate-500">
            Analysis completed for PR #{data.pr_number} • {data.risk_brief}
          </p>
        </div>
        
        <div className="shrink-0 bg-slate-50 p-4 rounded-xl border border-slate-100 flex items-center gap-6">
          <ScoreGauge score={data.confidence_score} />
          <div className="w-px h-16 bg-slate-200"></div>
          <div>
            <div className="text-xs text-slate-500 font-medium mb-1">DECISION</div>
            <div className={`text-lg font-bold flex items-center gap-2 ${data.decision === 'GREENLIGHT' ? 'text-emerald-600' : 'text-red-600'}`}>
              {data.decision === 'GREENLIGHT' ? <ShieldCheck className="w-5 h-5" /> : <FileWarning className="w-5 h-5" />}
              {data.decision}
            </div>
          </div>
        </div>
      </div>

      {/* Security Preflight */}
      {data.security_findings && data.security_findings.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            Security Preflight
          </h2>
          <div className="grid gap-3">
            {data.security_findings.map((finding, idx) => (
              <SecurityAlert key={idx} finding={finding} />
            ))}
          </div>
        </section>
      )}

      {/* Evidence Modules Grid */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-800">Safety Evidence</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.evidence_results?.map((module, idx) => (
            <EvidenceCard 
              key={idx}
              idx={idx}
              moduleName={module.module_name}
              status={module.status}
              riskModifier={module.risk_modifier}
              findings={module.findings}
              recommendation={module.recommendation}
            />
          ))}
          {(!data.evidence_results || data.evidence_results.length === 0) && (
            <div className="col-span-2 p-8 text-center text-slate-500 bg-slate-50 rounded-xl border border-slate-200 border-dashed">
              No evidence modules reported for this analysis.
            </div>
          )}
        </div>
      </section>

      {/* Rollback Playbook */}
      {data.rollback_playbook && (
        <section className="space-y-4">
          <h2 className="text-lg font-bold text-slate-800">Rollback Playbook</h2>
          <RollbackPlaybook playbook={data.rollback_playbook} />
        </section>
      )}

      {/* Changed Files */}
      {data.changed_files && data.changed_files.length > 0 && (
        <section className="space-y-4">
          <button 
            onClick={() => setShowChangedFiles(!showChangedFiles)}
            className="w-full flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors active:scale-[0.97]"
          >
            <div className="flex items-center gap-2">
              <FileCode className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-bold text-slate-800">Changed Files ({data.changed_files.length})</h2>
            </div>
            {showChangedFiles ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          
          <AnimatePresence>
            {showChangedFiles && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
                className="overflow-hidden"
              >
                <div className="bg-white border border-slate-200 rounded-xl p-2 space-y-1">
                  {data.changed_files.map((file, idx) => (
                    <motion.div 
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.03, duration: 0.2 }}
                      className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-lg text-sm text-slate-600"
                    >
                      <FileCode className="w-4 h-4 text-slate-400" />
                      <span className="font-mono">{file}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      )}

      {/* Analysis Metadata Footer */}
      <footer className="pt-8 mt-8 border-t border-slate-200 flex flex-col items-center justify-center text-sm text-slate-400 space-y-1">
        <p>Analysis ran at {new Date(data.analyzed_at || data.created_at).toLocaleString()}</p>
        {data.head_sha && (
          <p className="font-mono text-xs">Commit: {data.head_sha}</p>
        )}
      </footer>
    </motion.div>
  );
}
