import apiClient from './apiClient';

export const db = {
  items: {
    getAll: async () => {
      const response = await apiClient.get('/items/');
      return response.data;
    },
    add: async (item) => {
      const response = await apiClient.post('/items/', item);
      return response.data;
    },
    update: async (id, updates) => {
      const response = await apiClient.put(`/items/${id}`, updates);
      return response.data;
    },
    delete: async (id) => {
      const response = await apiClient.delete(`/items/${id}`);
      return response.data;
    },
    getStock: async (id) => {
      const response = await apiClient.get(`/items/${id}/stock`);
      return response.data;
    }
  },
  parties: {
    getAll: async () => {
      const response = await apiClient.get('/parties/');
      return response.data;
    },
    add: async (party) => {
      const response = await apiClient.post('/parties/', party);
      return response.data;
    },
    update: async (id, updates) => {
      const response = await apiClient.put(`/parties/${id}`, updates);
      return response.data;
    },
    delete: async (id) => {
      const response = await apiClient.delete(`/parties/${id}`);
      return response.data;
    }
  },
  prices: {
    getAll: async () => {
      const response = await apiClient.get('/prices/');
      return response.data;
    }
  },
  transactions: {
    add: async (transaction) => {
      // transaction.items is expected to be an array of { id, qty }
      const results = [];
      const isRental = transaction.type === 'RENTAL';
      const endpoint = isRental ? '/rent/' : '/returns/';

      for (const item of transaction.items) {
        const payload = {
          partyId: transaction.partyId,
          itemId: item.id,
          itemQty: item.qty,
          agentId: 1, // Default agent if none selected in UI
        };

        if (isRental) {
          payload.paidAmount = transaction.paidAmount || 0;
        } else {
          payload.refundAmount = 0; // Or whatever is applicable for returns
        }

        const response = await apiClient.post(endpoint, payload);
        results.push(response.data);
      }
      return results;
    },
    getRentalsByParty: async (partyId) => {
      const response = await apiClient.get(`/rent/party/${partyId}`);
      return response.data;
    },
    getReturnsByParty: async (partyId) => {
      const response = await apiClient.get(`/returns/party/${partyId}`);
      return response.data;
    }
  },
  dashboard: {
    getStats: async () => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
    getActivity: async () => {
      const response = await apiClient.get('/dashboard/activity');
      return response.data;
    }
  }
};
