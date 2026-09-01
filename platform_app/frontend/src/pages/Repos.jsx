import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { Shield, Github, Plus, RefreshCw, AlertCircle, Database } from 'lucide-react';
import SafetyBadge from '../components/SafetyBadge';

export default function Repos() {
  const [githubRepos, setGithubRepos] = useState([]);
  const [connectedRepos, setConnectedRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [enabling, setEnabling] = useState(null);

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
      setError(err.message);
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
      // 1. Create registration
      const reg = await api.createRegistration(owner, repo);
      // 2. Enable it
      await api.enableRegistration(reg.id);
      // Refresh list
      await fetchData();
    } catch (err) {
      alert(`Failed to enable: ${err.message}`);
    } finally {
      setEnabling(null);
    }
  };

  if (loading) return <div className="flex justify-center p-10"><RefreshCw className="w-8 h-8 animate-spin text-blue-500" /></div>;
  if (error) return <div className="text-red-500 p-4 bg-red-50 rounded-lg flex gap-2"><AlertCircle /> {error}</div>;

  const connectedFullNames = new Set(connectedRepos.map(r => r.full_name));
  const availableRepos = githubRepos.filter(r => !connectedFullNames.has(r.full_name));

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Connected Repositories</h1>
        <p className="text-slate-500 mb-6">Repositories actively monitored by SafeLane.</p>
        
        {connectedRepos.length === 0 ? (
          <div className="bg-white border border-slate-200 border-dashed rounded-xl p-10 text-center flex flex-col items-center">
            <Database className="w-12 h-12 text-slate-300 mb-3" />
            <h3 className="text-lg font-medium text-slate-700">No connected repositories</h3>
            <p className="text-slate-500 mt-1">Enable SafeLane on your GitHub repositories below.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {connectedRepos.map(repo => (
              <Link key={repo.id} to={`/repos/${repo.id}`} className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow p-5 flex flex-col">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2 text-slate-800 font-semibold truncate">
                    <Shield className="w-5 h-5 text-blue-500 shrink-0" />
                    <span className="truncate" title={repo.full_name}>{repo.repo}</span>
                  </div>
                  {repo.latest_decision && <SafetyBadge status={repo.latest_decision} />}
                </div>
                
                <div className="mt-auto pt-4 flex items-end justify-between border-t border-slate-100">
                  <div>
                    <div className="text-xs text-slate-500 mb-1">SAFETY SCORE</div>
                    <div className="text-2xl font-bold text-slate-800">{repo.latest_score !== null ? repo.latest_score : '--'}</div>
                  </div>
                  <div className="text-xs text-slate-400">
                    {repo.last_synced_at ? `Synced ${new Date(repo.last_synced_at).toLocaleDateString()}` : 'Not synced'}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <div className="pt-8 border-t border-slate-200">
        <h2 className="text-xl font-bold text-slate-800 mb-2">Your GitHub Repositories</h2>
        <p className="text-slate-500 mb-6">Available repositories you can connect to SafeLane.</p>
        
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <ul className="divide-y divide-slate-200">
            {availableRepos.map(repo => (
              <li key={repo.full_name} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <Github className="w-6 h-6 text-slate-400" />
                  <div>
                    <h4 className="font-medium text-slate-800">{repo.full_name}</h4>
                    <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                      {repo.language && (
                        <span className="flex items-center gap-1">
                          <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                          {repo.language}
                        </span>
                      )}
                      <span>Updated {new Date(repo.updated_at).toLocaleDateString()}</span>
                      {repo.private ? <span className="bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">Private</span> : null}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleEnable(repo.owner, repo.name)}
                  disabled={enabling === repo.full_name}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-md hover:bg-slate-50 hover:text-blue-600 hover:border-blue-300 transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {enabling === repo.full_name ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                  Connect
                </button>
              </li>
            ))}
            {availableRepos.length === 0 && (
              <li className="p-8 text-center text-slate-500">
                All your GitHub repositories are connected!
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
