import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './auth';

import Layout from './components/Layout';
import SignIn from './pages/SignIn';
import AuthCallback from './pages/AuthCallback';
import Repos from './pages/Repos';
import RepoDashboard from './pages/RepoDashboard';
import PRDetail from './pages/PRDetail';

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }
  
  if (!token) {
    return <Navigate to="/" replace />;
  }
  
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        
        <Route path="/repos" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Repos />} />
          <Route path=":id" element={<RepoDashboard />} />
          <Route path=":id/prs/:pr" element={<PRDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
