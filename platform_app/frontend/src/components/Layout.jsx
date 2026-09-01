import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Shield, LogOut, Github } from 'lucide-react';
import { useAuth } from '../auth';

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col hidden md:flex">
        <div className="p-4 flex items-center gap-2 border-b border-slate-800">
          <Shield className="w-8 h-8 text-blue-500" />
          <span className="font-bold text-xl">SafeLane</span>
        </div>
        
        <nav className="flex-1 p-4">
          <Link to="/repos" className="flex items-center gap-2 p-2 hover:bg-slate-800 rounded text-slate-300 hover:text-white transition-colors">
            <Github className="w-5 h-5" />
            Repositories
          </Link>
        </nav>
        
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center font-bold">
              {user?.github_username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="text-sm truncate">
              {user?.github_username}
            </div>
          </div>
          <button 
            onClick={logout}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors w-full p-2 hover:bg-slate-800 rounded"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="md:hidden bg-slate-900 text-white p-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-blue-500" />
            <span className="font-bold">SafeLane</span>
          </div>
          <button onClick={logout} className="text-slate-400 hover:text-white">
            <LogOut className="w-5 h-5" />
          </button>
        </header>

        <div className="flex-1 overflow-auto p-4 md:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
