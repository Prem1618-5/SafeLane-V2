import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../auth';
import { Loader2 } from 'lucide-react';

export default function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { checkSession } = useAuth();

  useEffect(() => {
    const error = searchParams.get('error');
    if (error) {
      // OAuth failed — redirect to sign-in
      navigate('/', { replace: true });
      return;
    }

    // Cookie is already set by the server redirect — just verify the session
    checkSession().then(() => {
      navigate('/repos', { replace: true });
    }).catch(() => {
      navigate('/', { replace: true });
    });
  }, [searchParams, navigate, checkSession]);

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white">
      <Loader2 className="w-10 h-10 animate-spin text-blue-500 mb-4" />
      <p className="text-slate-400">Authenticating...</p>
    </div>
  );
}
