import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Shield, LogOut, Github } from 'lucide-react';
import { useAuth } from '../auth';
import { motion } from 'framer-motion';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans text-slate-800 selection:bg-blue-100">
      {/* Sidebar - Light Theme */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col hidden md:flex z-10 shadow-sm relative">
        <div className="p-6 flex items-center gap-3 border-b border-slate-100">
          <div className="bg-blue-500 p-2 rounded-xl shadow-inner shadow-blue-600/50">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <span className="font-extrabold text-xl tracking-tight text-slate-900">SafeLane</span>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-1">
          <Link to="/repos" className="relative block">
            {location.pathname.includes('/repos') && (
              <motion.div 
                layoutId="nav-pill"
                className="absolute inset-0 bg-blue-50 border border-blue-100 rounded-lg"
                transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
              />
            )}
            <div className={`relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${location.pathname.includes('/repos') ? 'text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'}`}>
              <Github className="w-5 h-5" />
              Repositories
            </div>
          </Link>
        </nav>
        
        <div className="p-6 border-t border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold shadow-sm border border-blue-200">
              {user?.github_username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="text-sm font-medium truncate text-slate-700">
              {user?.github_username}
            </div>
          </div>
          <button 
            onClick={logout}
            className="flex items-center gap-2 text-sm text-slate-500 hover:text-red-600 transition-colors w-full p-2 hover:bg-red-50 rounded-lg font-medium"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Mobile Header */}
        <header className="md:hidden bg-white border-b border-slate-200 p-4 flex justify-between items-center z-10 shadow-sm">
          <div className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-blue-500" />
            <span className="font-bold text-slate-900">SafeLane</span>
          </div>
          <button onClick={logout} className="text-slate-500 hover:text-slate-900 p-2 bg-slate-50 rounded-lg">
            <LogOut className="w-5 h-5" />
          </button>
        </header>

        <div className="flex-1 overflow-auto p-4 md:p-8 bg-slate-50/50">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
