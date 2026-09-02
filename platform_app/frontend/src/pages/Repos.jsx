import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../auth';
import { Shield, Github, Plus, RefreshCw, AlertCircle, Database } from 'lucide-react';
import { DecisionBadge } from '../components/SafetyBadge';
import { motion, AnimatePresence } from 'framer-motion';

export default function Repos() {
  const [githubRepos, setGithubRepos] = useState([]);
  const [connectedRepos, setConnectedRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [enabling, setEnabling] = useState(null);

  const { login } = useAuth();
  
  const fetchData = async () => {
    setLoading(true);
    try {
      const [ghRes, dashRes] = await Promise.all([
        api.getUserRepos(),
        api.getDashboardRepos()
      ]);
      setGithubRepos(ghRes);
      setConnectedRepos(dashRes);
    } catch (err) {
      if (err.isAuthError) {
        setError("Your GitHub session has expired. Please re-authenticate.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleEnable = async (owner, repo) => {
    setEnabling(`${owner}/${repo}`);
    try {
      const reg = await api.createRegistration(owner, repo);
      await api.enableRegistration(reg.id);
      
      const [ghRes, dashRes] = await Promise.all([
        api.getUserRepos(),
        api.getDashboardRepos()
      ]);
      setGithubRepos(ghRes);
      setConnectedRepos(dashRes);
    } catch (err) {
      alert(`Failed to enable: ${err.message}`);
    } finally {
      setEnabling(null);
    }
  };

  if (loading) return <div className="flex justify-center p-10 mt-20"><RefreshCw className="w-8 h-8 animate-spin text-blue-500" /></div>;
  if (error) {
    if (error.includes("session has expired")) {
      return (
        <div className="text-red-500 p-4 bg-red-50 rounded-lg flex flex-col items-start gap-4 border border-red-200">
          <div className="flex gap-2"><AlertCircle /> {error}</div>
          <button onClick={login} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Re-authenticate with GitHub
          </button>
        </div>
      );
    }
    return <div className="text-red-500 p-4 bg-red-50 rounded-lg flex gap-2 border border-red-200"><AlertCircle /> {error}</div>;
  }

  const connectedFullNames = new Set(connectedRepos.map(r => r.full_name));
  const availableRepos = githubRepos.filter(r => !connectedFullNames.has(r.full_name));

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="space-y-10 max-w-5xl mx-auto pb-10"
    >
      <div>
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Connected Repositories</h1>
        <p className="text-slate-500 mb-6 font-medium">Repositories actively monitored by SafeLane.</p>
        
        {connectedRepos.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white border border-slate-200 border-dashed rounded-xl p-10 text-center flex flex-col items-center"
          >
            <Database className="w-12 h-12 text-slate-300 mb-3" />
            <h3 className="text-lg font-medium text-slate-700">No connected repositories</h3>
            <p className="text-slate-500 mt-1">Enable SafeLane on your GitHub repositories below.</p>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <AnimatePresence>
              {connectedRepos.map((repo, idx) => (
                <motion.div
                  key={repo.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  whileHover={{ y: -4 }}
                  className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col relative overflow-hidden"
                >
                  <Link to={`/repos/${repo.id}`} className="p-5 flex flex-col h-full z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3 text-slate-800 font-semibold truncate">
                        <div className="bg-blue-50 p-2 rounded-lg border border-blue-100">
                          <Shield className="w-5 h-5 text-blue-600 shrink-0" />
                        </div>
                        <span className="truncate tracking-tight" title={repo.full_name}>{repo.repo}</span>
                      </div>
                      {repo.latest_decision && <DecisionBadge decision={repo.latest_decision} />}
                    </div>
                    
                    <div className="mt-auto pt-5 flex items-end justify-between border-t border-slate-100">
                      <div>
                        <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">SAFETY SCORE</div>
                        <div className="text-2xl font-black text-slate-800">{repo.latest_score !== null ? repo.latest_score : '--'}</div>
                      </div>
                      <div className="text-xs font-medium text-slate-400">
                        {repo.last_synced_at ? `Synced ${new Date(repo.last_synced_at).toLocaleDateString()}` : 'Not synced'}
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      <div className="pt-10 border-t border-slate-200">
        <h2 className="text-xl font-bold text-slate-800 mb-2">Your GitHub Repositories</h2>
        <p className="text-slate-500 mb-6 font-medium">Available repositories you can connect to SafeLane.</p>
        
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <ul className="divide-y divide-slate-100">
            <AnimatePresence>
              {availableRepos.map(repo => (
                <motion.li 
                  layout
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0, x: -20 }}
                  key={repo.full_name} 
                  className="p-4 sm:p-5 flex items-center justify-between hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-slate-100 rounded-lg border border-slate-200 text-slate-500">
                      <Github className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-800 text-sm sm:text-base">{repo.full_name}</h4>
                      <div className="flex flex-wrap items-center gap-3 text-xs font-medium text-slate-500 mt-1">
                        {repo.language && (
                          <span className="flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-blue-500 shadow-sm"></span>
                            {repo.language}
                          </span>
                        )}
                        <span>Updated {new Date(repo.updated_at).toLocaleDateString()}</span>
                        {repo.private ? <span className="bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200 shadow-sm">Private</span> : null}
                      </div>
                    </div>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleEnable(repo.owner, repo.name)}
                    disabled={enabling === repo.full_name}
                    className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg shadow-sm hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 transition-colors text-sm font-bold tracking-wide disabled:opacity-50 disabled:shadow-none"
                  >
                    {enabling === repo.full_name ? <RefreshCw className="w-4 h-4 animate-spin text-blue-500" /> : <Plus className="w-4 h-4" />}
                    <span className="hidden sm:inline">Connect</span>
                  </motion.button>
                </motion.li>
              ))}
            </AnimatePresence>
            {availableRepos.length === 0 && (
              <li className="p-10 text-center text-slate-500 font-medium">
                All your GitHub repositories are connected!
              </li>
            )}
          </ul>
        </div>
      </div>
    </motion.div>
  );
}
