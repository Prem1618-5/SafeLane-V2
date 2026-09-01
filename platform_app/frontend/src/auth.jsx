import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('safelane_token'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      localStorage.setItem('safelane_token', token);
      // Fetch user profile
      fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => {
        if (!res.ok) throw new Error('Token invalid');
        return res.json();
      })
      .then(data => setUser(data))
      .catch(() => {
        setToken(null);
        localStorage.removeItem('safelane_token');
      })
      .finally(() => setLoading(false));
    } else {
      localStorage.removeItem('safelane_token');
      setUser(null);
      setLoading(false);
    }
  }, [token]);

  const login = () => {
    window.location.href = '/api/auth/github/login';
  };

  const logout = () => {
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, setToken, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
