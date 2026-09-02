const getHeaders = () => {
  return {
    'Content-Type': 'application/json',
  };
};

const fetchWithCredentials = async (url, options = {}) => {
  return fetch(url, {
    ...options,
    credentials: 'include',
  });
};

export const api = {
  getUserRepos: async () => {
    const res = await fetchWithCredentials('/api/github/user-repos');
    if (!res.ok) {
      const err = new Error('Failed to fetch repos');
      if (res.status === 401) err.isAuthError = true;
      throw err;
    }
    return res.json();
  },
  
  getDashboardRepos: async () => {
    const res = await fetchWithCredentials('/api/dashboard/repos');
    if (!res.ok) throw new Error('Failed to fetch dashboard repos');
    return res.json();
  },
  
  getRepoDashboard: async (id) => {
    const res = await fetchWithCredentials(`/api/dashboard/repos/${id}`);
    if (!res.ok) throw new Error('Failed to fetch repo details');
    return res.json();
  },
  
  getPRDetail: async (id, prNumber) => {
    const res = await fetchWithCredentials(`/api/dashboard/repos/${id}/prs/${prNumber}`);
    if (!res.ok) throw new Error('Failed to fetch PR details');
    return res.json();
  },
  
  createRegistration: async (owner, repo) => {
    const res = await fetchWithCredentials('/api/registrations/', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ owner, repo })
    });
    if (!res.ok) throw new Error('Failed to register repo');
    return res.json();
  },
  
  enableRegistration: async (id) => {
    const res = await fetchWithCredentials(`/api/registrations/${id}/enable`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to enable repo');
    return res.json();
  },
  
  disableRegistration: async (id) => {
    const res = await fetchWithCredentials(`/api/registrations/${id}/deactivate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to deactivate repo');
    return res.json();
  },
  
  syncRepo: async (id) => {
    const res = await fetchWithCredentials(`/api/dashboard/repos/${id}/sync`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to sync repo');
    return res.json();
  }
};
