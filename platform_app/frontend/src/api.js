const getHeaders = () => {
  const token = localStorage.getItem('safelane_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

export const api = {
  getUserRepos: async () => {
    const res = await fetch('/api/github/user-repos', { headers: getHeaders() });
    if (!res.ok) {
      const err = new Error('Failed to fetch repos');
      if (res.status === 401) err.isAuthError = true;
      throw err;
    }
    return res.json();
  },
  
  getDashboardRepos: async () => {
    const res = await fetch('/api/dashboard/repos', { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch dashboard repos');
    return res.json();
  },
  
  getRepoDashboard: async (id) => {
    const res = await fetch(`/api/dashboard/repos/${id}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch repo details');
    return res.json();
  },
  
  getPRDetail: async (id, prNumber) => {
    const res = await fetch(`/api/dashboard/repos/${id}/prs/${prNumber}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch PR details');
    return res.json();
  },
  
  createRegistration: async (owner, repo) => {
    const res = await fetch('/api/registrations/', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ owner, repo })
    });
    if (!res.ok) throw new Error('Failed to register repo');
    return res.json();
  },
  
  enableRegistration: async (id) => {
    const res = await fetch(`/api/registrations/${id}/enable`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to enable repo');
    return res.json();
  },
  
  disableRegistration: async (id) => {
    const res = await fetch(`/api/registrations/${id}/disable`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to disable repo');
    return res.json();
  },
  
  syncRepo: async (id) => {
    const res = await fetch(`/api/dashboard/repos/${id}/sync`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to sync repo');
    return res.json();
  }
};
