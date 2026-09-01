import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';
import { ChevronRight, RefreshCw, AlertTriangle, ShieldCheck, FileWarning, ArrowLeft } from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import SafetyBadge from '../components/SafetyBadge';
import EvidenceCard from '../components/EvidenceCard';
import SecurityAlert from '../components/SecurityAlert';
import RollbackPlaybook from '../components/RollbackPlaybook';

export default function PRDetail() {
  const { id, pr } = useParams();
  const [data, setData] = useState(null);
  const [repoData, setRepoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
    <div className="max-w-6xl mx-auto space-y-6 pb-20">
      {/* Breadcrumbs */}
      <nav className="flex items-center text-sm text-slate-500">
        <Link to="/repos" className="hover:text-blue-600 transition-colors">Repositories</Link>
        <ChevronRight className="w-4 h-4 mx-1" />
        <Link to={`/repos/${id}`} className="hover:text-blue-600 transition-colors">{repoData?.full_name || 'Repo'}</Link>
        <ChevronRight className="w-4 h-4 mx-1" />
        <span className="text-slate-800 font-medium">PR #{pr}</span>
      </nav>

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
    </div>
  );
}
