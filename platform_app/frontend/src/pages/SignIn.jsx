import React from 'react';
import { Shield, Github } from 'lucide-react';
import { useAuth } from '../auth';
import { Navigate } from 'react-router-dom';

export default function SignIn() {
  const { token, login } = useAuth();

  if (token) {
    return <Navigate to="/repos" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-[-20%] left-[-10%] w-96 h-96 bg-blue-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-96 h-96 bg-emerald-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
      
      <div className="z-10 bg-slate-800 p-10 rounded-2xl shadow-2xl border border-slate-700 max-w-md w-full mx-4 flex flex-col items-center text-center">
        <div className="bg-slate-900 p-4 rounded-full border border-slate-700 mb-6 shadow-inner">
          <Shield className="w-16 h-16 text-blue-500" />
        </div>
        
        <h1 className="text-3xl font-bold text-white mb-2">SafeLane</h1>
        <p className="text-slate-400 mb-8">AI-Powered PR Safety for GitHub</p>
        
        <button
          onClick={login}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-3 transition-colors duration-200 shadow-lg shadow-blue-900/50"
        >
          <Github className="w-5 h-5" />
          Sign in with GitHub
        </button>
        
        <p className="text-slate-500 text-xs mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
