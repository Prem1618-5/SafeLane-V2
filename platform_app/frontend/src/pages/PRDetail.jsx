import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';
import {
  AlertTriangle,
  ArrowLeft,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  FileCode,
  FileText,
  RefreshCw,
  ShieldCheck,
  FileWarning,
} from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import SafetyBadge from '../components/SafetyBadge';
import EvidenceCard from '../components/EvidenceCard';
import SecurityAlert from '../components/SecurityAlert';
import RollbackPlaybook from '../components/RollbackPlaybook';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';

export default function PRDetail() {
  const { id, pr } = useParams();
  const [data, setData] = useState(null);
  const [repoData, setRepoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showChangedFiles, setShowChangedFiles] = useState(false);
  const [showRiskBrief, setShowRiskBrief] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [prRes, repoRes] = await Promise.all([
          api.getPRDetail(id, pr),
          api.getRepoDashboard(id),
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

  if (loading) {
    return (
      <div className="flex min-h-[16rem] items-center justify-center" role="status" aria-live="polite">
        <RefreshCw className="h-7 w-7 animate-spin text-blue-500" aria-hidden="true" />
        <span className="sr-only">Loading pull request analysis</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800" role="alert">
        <p className="font-semibold">Unable to load this analysis</p>
        <p className="mt-1 text-sm">{error}</p>
      </div>
    );
  }

  if (!data) return <div className="rounded-xl border border-slate-200 bg-white p-6 text-slate-600">Analysis not found.</div>;

  const isGreenlight = data.decision === 'GREENLIGHT';
  const findings = data.security_findings || [];
  const evidence = data.evidence_results || [];
  const criticalCount = findings.filter((finding) => finding.severity === 'critical').length
    + evidence.filter((module) => module.status === 'critical').length;
  const warningCount = findings.filter((finding) => finding.severity === 'warning').length
    + evidence.filter((module) => module.status === 'warning').length;
  const verdictStyles = isGreenlight
    ? 'border-emerald-200 bg-emerald-50/70'
    : 'border-red-200 bg-red-50/70';
  const verdictTextStyles = isGreenlight ? 'text-emerald-800' : 'text-red-800';
  const VerdictIcon = isGreenlight ? ShieldCheck : FileWarning;
  const analysisTitle = data.pr_number === 0
    ? `Commit ${data.head_sha?.substring(0, 7) || ''}`
    : `Pull Request #${data.pr_number}`;
  const verdictSummary = isGreenlight
    ? 'SafeLane found no blocking evidence in this analysis.'
    : criticalCount > 0
      ? `${criticalCount} critical finding${criticalCount === 1 ? '' : 's'} require remediation before this change can proceed.`
      : 'This change needs attention before it can proceed.';

  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.28, ease: 'easeOut' }}
      className="mx-auto max-w-6xl space-y-6 pb-12"
    >
      <nav className="flex flex-wrap items-center gap-y-1 text-sm text-slate-500" aria-label="Breadcrumb">
        <Link to="/repos" className="rounded-sm transition-colors hover:text-blue-600">Repositories</Link>
        <ChevronRight className="mx-1 h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
        <Link to={`/repos/${id}`} className="max-w-full truncate rounded-sm transition-colors hover:text-blue-600">
          {repoData?.full_name || 'Repository'}
        </Link>
        <ChevronRight className="mx-1 h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
        <span className="font-medium text-slate-800">PR #{pr}</span>
      </nav>

      <header className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <Link
                to={`/repos/${id}`}
                className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 active:scale-[0.97]"
                aria-label="Back to repository"
              >
                <ArrowLeft className="h-5 w-5" aria-hidden="true" />
              </Link>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{analysisTitle}</h1>
                  <SafetyBadge status={data.decision} />
                </div>
                <p className="mt-1 text-sm text-slate-500">
                  Analysis completed {data.created_at ? new Date(data.created_at).toLocaleString() : 'recently'}
                </p>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setShowRiskBrief((visible) => !visible)}
            aria-expanded={showRiskBrief}
            aria-controls="risk-brief"
            className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 active:scale-[0.98]"
          >
            <FileText className="h-4 w-4" aria-hidden="true" />
            Analysis details
            {showRiskBrief ? <ChevronUp className="h-4 w-4" aria-hidden="true" /> : <ChevronDown className="h-4 w-4" aria-hidden="true" />}
          </button>
        </div>
      </header>

      <section className={`rounded-2xl border p-5 shadow-sm sm:p-6 ${verdictStyles}`} aria-labelledby="verdict-heading">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
          <div className="min-w-0 max-w-2xl">
            <div className={`flex items-center gap-2 text-sm font-bold uppercase tracking-[0.14em] ${verdictTextStyles}`}>
              <VerdictIcon className="h-5 w-5" aria-hidden="true" />
              Decision
            </div>
            <h2 id="verdict-heading" className={`mt-2 text-2xl font-bold tracking-tight sm:text-3xl ${verdictTextStyles}`}>
              {isGreenlight ? 'Ready for review' : 'Change blocked'}
            </h2>
            <p className="mt-2 text-base leading-7 text-slate-700">{verdictSummary}</p>
            <div className="mt-4 flex flex-wrap gap-2 text-sm">
              <span className="rounded-full border border-slate-300 bg-white/80 px-3 py-1.5 font-medium text-slate-700">
                {evidence.length} evidence module{evidence.length === 1 ? '' : 's'}
              </span>
              {warningCount > 0 && (
                <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 font-medium text-amber-800">
                  {warningCount} warning{warningCount === 1 ? '' : 's'}
                </span>
              )}
              {criticalCount > 0 && (
                <span className="rounded-full border border-red-200 bg-red-50 px-3 py-1.5 font-medium text-red-800">
                  {criticalCount} critical
                </span>
              )}
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-5 rounded-xl border border-white/80 bg-white p-4 shadow-sm sm:px-5">
            <ScoreGauge score={data.confidence_score} size={112} />
            <div className="h-16 w-px bg-slate-200" aria-hidden="true" />
            <div className="min-w-[6.5rem]">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Verdict</div>
              <div className={`mt-1 flex items-center gap-2 text-lg font-bold ${isGreenlight ? 'text-emerald-600' : 'text-red-600'}`}>
                <VerdictIcon className="h-5 w-5" aria-hidden="true" />
                {data.decision}
              </div>
            </div>
          </div>
        </div>
      </section>

      <AnimatePresence initial={false}>
        {showRiskBrief && data.risk_brief && (
          <motion.section
            id="risk-brief"
            initial={shouldReduceMotion ? false : { opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: -4 }}
            transition={{ duration: shouldReduceMotion ? 0 : 0.18 }}
            className="rounded-xl border border-slate-200 bg-white shadow-sm"
            aria-labelledby="risk-brief-heading"
          >
            <div className="border-b border-slate-100 px-5 py-4">
              <h2 id="risk-brief-heading" className="font-semibold text-slate-800">Raw analysis brief</h2>
              <p className="mt-1 text-sm text-slate-500">Full generated analysis kept for audit context.</p>
            </div>
            <pre className="max-h-96 overflow-auto whitespace-pre-wrap p-5 font-mono text-xs leading-6 text-slate-600">
              {data.risk_brief}
            </pre>
          </motion.section>
        )}
      </AnimatePresence>

      {findings.length > 0 && (
        <section className="space-y-4" aria-labelledby="security-heading">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" aria-hidden="true" />
            <h2 id="security-heading" className="text-lg font-bold text-slate-800">Security Preflight</h2>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600">{findings.length}</span>
          </div>
          <div className="grid gap-3">
            {findings.map((finding, idx) => <SecurityAlert key={`${finding.title}-${idx}`} finding={finding} />)}
          </div>
        </section>
      )}

      <section className="space-y-4" aria-labelledby="evidence-heading">
        <div>
          <h2 id="evidence-heading" className="text-lg font-bold text-slate-800">Safety Evidence</h2>
          <p className="mt-1 text-sm text-slate-500">Independent checks behind this decision.</p>
        </div>
        {evidence.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {evidence.map((module, idx) => (
              <EvidenceCard
                key={`${module.module_name}-${idx}`}
                idx={idx}
                moduleName={module.module_name}
                status={module.status}
                riskModifier={module.risk_modifier}
                findings={module.findings}
                recommendation={module.recommendation}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
            No evidence modules reported for this analysis.
          </div>
        )}
      </section>

      {data.rollback_playbook && (
        <section className="space-y-4" aria-labelledby="rollback-heading">
          <div>
            <h2 id="rollback-heading" className="text-lg font-bold text-slate-800">Rollback Playbook</h2>
            <p className="mt-1 text-sm text-slate-500">Suggested recovery commands for this blocked change.</p>
          </div>
          <RollbackPlaybook playbook={data.rollback_playbook} />
        </section>
      )}

      {data.changed_files?.length > 0 && (
        <section className="space-y-3" aria-labelledby="files-heading">
          <button
            type="button"
            onClick={() => setShowChangedFiles((visible) => !visible)}
            aria-expanded={showChangedFiles}
            aria-controls="changed-files"
            className="flex min-h-12 w-full items-center justify-between rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-colors hover:bg-slate-50 active:scale-[0.99]"
          >
            <span className="flex items-center gap-3">
              <FileCode className="h-5 w-5 text-blue-500" aria-hidden="true" />
              <span>
                <span id="files-heading" className="block font-bold text-slate-800">Changed files</span>
                <span className="text-sm text-slate-500">{data.changed_files.length} file{data.changed_files.length === 1 ? '' : 's'} analyzed</span>
              </span>
            </span>
            {showChangedFiles ? <ChevronUp className="h-5 w-5 text-slate-400" aria-hidden="true" /> : <ChevronDown className="h-5 w-5 text-slate-400" aria-hidden="true" />}
          </button>
          <AnimatePresence initial={false}>
            {showChangedFiles && (
              <motion.div
                id="changed-files"
                initial={shouldReduceMotion ? false : { opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: -4 }}
                transition={{ duration: shouldReduceMotion ? 0 : 0.18 }}
                className="overflow-hidden rounded-xl border border-slate-200 bg-white p-2 shadow-sm"
              >
                {data.changed_files.map((file) => (
                  <div key={file} className="flex items-start gap-3 rounded-lg p-3 text-sm text-slate-600 hover:bg-slate-50">
                    <FileCode className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
                    <span className="min-w-0 overflow-wrap-anywhere font-mono">{file}</span>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      )}

      <footer className="border-t border-slate-200 pt-6 text-center text-sm text-slate-400">
        {data.head_sha && <p className="font-mono text-xs">Commit: {data.head_sha}</p>}
      </footer>
    </motion.div>
  );
}
