import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Shield, LogOut, Github } from 'lucide-react';
import { useAuth } from '../auth';
import { motion } from 'framer-motion';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="flex min-h-dvh bg-slate-50 font-sans text-slate-800 selection:bg-blue-100">
      {/* Sidebar - Light Theme */}
      <aside className="relative z-10 hidden w-64 flex-col border-r border-slate-200 bg-white shadow-sm md:flex">
        <div className="flex items-center gap-3 border-b border-slate-100 p-6">
          <div className="rounded-xl bg-blue-500 p-2 shadow-inner shadow-blue-600/50">
            <Shield className="h-6 w-6 text-white" aria-hidden="true" />
          </div>
          <span className="font-extrabold text-xl tracking-tight text-slate-900">SafeLane</span>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-1">
          <Link to="/repos" aria-current={location.pathname.includes('/repos') ? 'page' : undefined} className="relative block">
            {location.pathname.includes('/repos') && (
              <motion.div 
                layoutId="nav-pill"
                className="absolute inset-0 bg-blue-50 border border-blue-100 rounded-lg"
                transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
              />
            )}
            <div className={`relative flex min-h-11 items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${location.pathname.includes('/repos') ? 'text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}>
              <Github className="h-5 w-5" aria-hidden="true" />
              Repositories
            </div>
          </Link>
        </nav>
        
        <div className="border-t border-slate-100 bg-slate-50/50 p-6">
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
            className="flex min-h-11 w-full items-center gap-2 rounded-lg p-2 text-sm font-medium text-slate-500 transition-colors hover:bg-red-50 hover:text-red-600 active:scale-[0.98]"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main id="main-content" className="relative flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="z-10 flex items-center justify-between border-b border-slate-200 bg-white p-4 shadow-sm md:hidden">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-blue-500" aria-hidden="true" />
            <span className="font-bold text-slate-900">SafeLane</span>
          </div>
          <button onClick={logout} aria-label="Sign out" className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-50 text-slate-500 transition-colors hover:text-slate-900 active:scale-[0.97]">
            <LogOut className="h-5 w-5" aria-hidden="true" />
          </button>
        </header>

        <div className="flex-1 overflow-auto bg-slate-50/50 p-4 sm:p-6 md:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
