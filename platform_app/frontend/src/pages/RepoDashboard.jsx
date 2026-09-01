import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';
import { ChevronRight, RefreshCw, GitPullRequest, Activity } from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import SafetyBadge from '../components/SafetyBadge';
import { motion } from 'framer-motion';

export default function RepoDashboard() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    const fetchRepo = async () => {
      try {
        const res = await api.getRepoDashboard(id);
        setData(res);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRepo();
  }, [id]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await api.syncRepo(id);
      // Wait a few seconds then refresh
      setTimeout(async () => {
        const res = await api.getRepoDashboard(id);
        setData(res);
        setSyncing(false);
      }, 3000);
    } catch (e) {
      alert(e.message);
      setSyncing(false);
    }
  };

  if (loading) return <div className="flex justify-center p-10"><RefreshCw className="w-8 h-8 animate-spin text-blue-500" /></div>;
  if (error) return <div className="text-red-500 p-4 bg-red-50 rounded-lg">{error}</div>;
  if (!data) return <div>Not found</div>;

  const prs = data.pull_requests || [];
  const latestAnalysis = data.analyses && data.analyses.length > 0 ? data.analyses[0] : null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="max-w-5xl mx-auto space-y-6"
    >
      {/* Breadcrumbs */}
      <nav className="flex items-center text-sm text-slate-500">
        <Link to="/repos" className="hover:text-blue-600 transition-colors">Repositories</Link>
        <ChevronRight className="w-4 h-4 mx-1" />
        <span className="text-slate-800 font-medium">{data.full_name}</span>
      </nav>

      {/* Header Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Score Card */}
        <motion.div 
          whileHover={{ y: -2 }}
          className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center transition-shadow hover:shadow-md"
        >
          <h2 className="text-sm font-semibold text-slate-500 mb-4 uppercase tracking-wider w-full text-left">Current Safety</h2>
          {latestAnalysis ? (
            <>
              <ScoreGauge score={latestAnalysis.confidence_score} />
              <div className="mt-4">
                <SafetyBadge status={latestAnalysis.decision} />
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
              <Activity className="w-12 h-12 mb-2 opacity-50" />
              <p>No analyses yet</p>
            </div>
          )}
        </motion.div>

        {/* Info Card */}
        <motion.div 
          whileHover={{ y: -2 }}
          className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:col-span-2 flex flex-col justify-between transition-shadow hover:shadow-md relative overflow-hidden"
        >
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-slate-800 mb-2">{data.repo}</h1>
              <p className="text-slate-500">Managed by SafeLane</p>
            </div>
            
            <motion.button 
              whileTap={{ scale: 0.97 }}
              onClick={handleSync}
              disabled={syncing}
              className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium hover:bg-blue-100 transition-colors disabled:opacity-70"
            >
              <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              {syncing ? 'Syncing...' : 'Sync Now'}
            </motion.button>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mt-6 p-4 bg-slate-50 rounded-lg border border-slate-100">
            <div>
              <div className="text-xs text-slate-500 mb-1">STATUS</div>
              <div className="font-medium text-slate-800 flex items-center gap-2">
                {data.is_active ? (
                  <span className="text-emerald-600 flex items-center gap-1">
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                    Active
                  </span>
                ) : 'Disabled'}
              </div>
            </div>
            <div>
              <div className="text-xs text-slate-500 mb-1">LAST SYNCED</div>
              <div className="font-medium text-slate-800">
                {data.last_synced_at ? new Date(data.last_synced_at).toLocaleString() : 'Never'}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* PRs Table */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.3, ease: 'easeOut' }}
        className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden"
      >
        <div className="p-5 border-b border-slate-200 flex items-center gap-2 bg-slate-50/50">
          <GitPullRequest className="w-5 h-5 text-slate-500" />
          <h2 className="text-lg font-semibold text-slate-800">Recent Pull Requests</h2>
        </div>
        
        {prs.length === 0 ? (
          <div className="p-8 text-center text-slate-500 italic">No pull requests analyzed yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                  <th className="p-4 font-medium border-b border-slate-200">PR</th>
                  <th className="p-4 font-medium border-b border-slate-200">Title</th>
                  <th className="p-4 font-medium border-b border-slate-200">Score</th>
                  <th className="p-4 font-medium border-b border-slate-200">Decision</th>
                  <th className="p-4 font-medium border-b border-slate-200">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {prs.map((pr, idx) => {
                  const prAnalysis = data.analyses?.find(a => a.pr_number === pr.pr_number);
                  return (
                    <motion.tr 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.05 * idx }}
                      key={pr.pr_number} 
                      className="hover:bg-slate-50 transition-colors group"
                    >
                      <td className="p-4 font-medium text-blue-600">
                        <Link to={`/repos/${id}/prs/${pr.pr_number}`} className="hover:underline">
                          #{pr.pr_number}
                        </Link>
                      </td>
                      <td className="p-4 text-slate-800 font-medium">
                        <Link to={`/repos/${id}/prs/${pr.pr_number}`} className="block">
                          {pr.title || `Update ${pr.head_sha?.substring(0, 7)}`}
                        </Link>
                      </td>
                      <td className="p-4">
                        {prAnalysis ? (
                          <span className={`font-mono font-bold ${prAnalysis.confidence_score >= 80 ? 'text-emerald-600' : prAnalysis.confidence_score >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
                            {prAnalysis.confidence_score}
                          </span>
                        ) : '--'}
                      </td>
                      <td className="p-4">
                        {prAnalysis ? <SafetyBadge status={prAnalysis.decision} /> : <span className="text-slate-400 italic">Pending</span>}
                      </td>
                      <td className="p-4 text-slate-500 whitespace-nowrap">
                        {new Date(pr.updated_at || pr.created_at).toLocaleDateString()}
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
