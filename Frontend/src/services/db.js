import apiClient from './apiClient';

/** Strips undefined/'' so optional filters are omitted rather than sent blank. */
function params(obj = {}) {
  const out = {};
  for (const [k, v] of Object.entries(obj)) {
    if (v !== undefined && v !== null && v !== '') out[k] = v;
  }
  return out;
}

export const db = {
  items: {
    list: (q) => apiClient.get('/items/', { params: params(q) }).then((r) => r.data),
    get: (id) => apiClient.get(`/items/${id}`).then((r) => r.data),
    create: (payload) => apiClient.post('/items/', payload).then((r) => r.data),
    update: (id, payload) => apiClient.put(`/items/${id}`, payload).then((r) => r.data),
    remove: (id) => apiClient.delete(`/items/${id}`).then((r) => r.data),
    stock: (id) => apiClient.get(`/items/${id}/stock`).then((r) => r.data),
    setStock: (id, qty) => apiClient.put(`/items/${id}/stock`, { qty }).then((r) => r.data),
  },

  parties: {
    list: (q) => apiClient.get('/parties/', { params: params(q) }).then((r) => r.data),
    get: (id) => apiClient.get(`/parties/${id}`).then((r) => r.data),
    create: (payload) => apiClient.post('/parties/', payload).then((r) => r.data),
    update: (id, payload) => apiClient.put(`/parties/${id}`, payload).then((r) => r.data),
    remove: (id) => apiClient.delete(`/parties/${id}`).then((r) => r.data),
    ledger: (id) => apiClient.get(`/parties/${id}/ledger`).then((r) => r.data),
  },

  agents: {
    list: (q) => apiClient.get('/agents/', { params: params(q) }).then((r) => r.data),
    get: (id) => apiClient.get(`/agents/${id}`).then((r) => r.data),
    create: (payload) => apiClient.post('/agents/', payload).then((r) => r.data),
    update: (id, payload) => apiClient.put(`/agents/${id}`, payload).then((r) => r.data),
    remove: (id) => apiClient.delete(`/agents/${id}`).then((r) => r.data),
  },

  prices: {
    list: (q) => apiClient.get('/prices/', { params: params(q) }).then((r) => r.data),
    get: (itemId) => apiClient.get(`/prices/${itemId}`).then((r) => r.data),
    create: (payload) => apiClient.post('/prices/', payload).then((r) => r.data),
    update: (itemId, payload) => apiClient.put(`/prices/${itemId}`, payload).then((r) => r.data),
    remove: (itemId) => apiClient.delete(`/prices/${itemId}`).then((r) => r.data),
  },

  contracts: {
    list: (q) => apiClient.get('/contracts/', { params: params(q) }).then((r) => r.data),
    get: (id) => apiClient.get(`/contracts/${id}`).then((r) => r.data),
    /**
     * One call carrying every line. Replaces the old loop that fired N separate
     * POST /rent/ requests — which could fail halfway and leave a half-created
     * rental with no way to tell which items went out.
     */
    create: (payload) => apiClient.post('/contracts/', payload).then((r) => r.data),
    /** Price a return without committing it, so the counter can show the bill first. */
    quote: (id, asOf) =>
      apiClient.get(`/contracts/${id}/quote`, { params: params({ asOf }) }).then((r) => r.data),
    returnItems: (id, payload) =>
      apiClient.post(`/contracts/${id}/return`, payload).then((r) => r.data),
    addPayment: (id, payload) =>
      apiClient.post(`/contracts/${id}/payment`, payload).then((r) => r.data),
  },

  returns: {
    list: (q) => apiClient.get('/returns/', { params: params(q) }).then((r) => r.data),
  },

  payments: {
    list: (q) => apiClient.get('/payments/', { params: params(q) }).then((r) => r.data),
  },

  dashboard: {
    stats: () => apiClient.get('/dashboard/stats').then((r) => r.data),
    activity: (limit = 8) =>
      apiClient.get('/dashboard/activity', { params: { limit } }).then((r) => r.data),
    trend: (days = 30) =>
      apiClient.get('/dashboard/trend', { params: { days } }).then((r) => r.data),
    topItems: (limit = 5) =>
      apiClient.get('/dashboard/top-items', { params: { limit } }).then((r) => r.data),
  },
};
