const STORAGE_KEY = 'inventoryx_db_v1';

const initialData = {
  items: [
    { id: '1', name: 'Canon Printer', description: 'Color Laser Printer', quantity: 10, totalQuantity: 10, price: 50 },
    { id: '2', name: 'Dell Monitor', description: '24 inch IPS', quantity: 5, totalQuantity: 5, price: 30 },
    { id: '3', name: 'Conference Chair', description: 'Black ergonomic', quantity: 50, totalQuantity: 50, price: 10 },
  ],
  parties: [
    { id: '1', name: 'John Doe', contact: '555-0101', email: 'john@example.com', balance: 0, status: 'inactive' },
    { id: '2', name: 'Acme Corp', contact: '555-0102', email: 'info@acme.com', balance: 150, status: 'active' },
  ],
  transactions: []
};

const getDB = () => {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : initialData;
};

const saveDB = (data) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
};

export const db = {
  items: {
    getAll: async () => {
      // Simulate network delay
      await new Promise(r => setTimeout(r, 500));
      return getDB().items;
    },
    add: async (item) => {
      await new Promise(r => setTimeout(r, 500));
      const data = getDB();
      const newItem = { ...item, id: Math.random().toString(36).substr(2, 9), quantity: parseInt(item.quantity) || 0, totalQuantity: parseInt(item.quantity) || 0 };
      data.items.push(newItem);
      saveDB(data);
      return newItem;
    },
    update: async (id, updates) => {
      await new Promise(r => setTimeout(r, 500));
      const data = getDB();
      const index = data.items.findIndex(i => i.id === id);
      if (index === -1) throw new Error("Item not found");
      data.items[index] = { ...data.items[index], ...updates };
      
      // Update quantity logic if max total changes? For now simple update.
      if (updates.totalQuantity) {
          // Adjust current quantity based on diff (logic can be complex if items are out, assuming simple for now)
      }
      
      saveDB(data);
      return data.items[index];
    },
    delete: async (id) => {
      await new Promise(r => setTimeout(r, 500));
      const data = getDB();
      data.items = data.items.filter(i => i.id !== id);
      saveDB(data);
    }
  },
  parties: {
    getAll: async () => {
        await new Promise(r => setTimeout(r, 500));
        return getDB().parties;
    },
    add: async (party) => {
        await new Promise(r => setTimeout(r, 500));
        const data = getDB();
        const newParty = { ...party, id: Math.random().toString(36).substr(2, 9), balance: 0, status: 'inactive' };
        data.parties.push(newParty);
        saveDB(data);
        return newParty;
    },
    update: async (id, updates) => {
        await new Promise(r => setTimeout(r, 500));
        const data = getDB();
        const index = data.parties.findIndex(p => p.id === id);
        if (index === -1) throw new Error("Party not found");
        data.parties[index] = { ...data.parties[index], ...updates };
        saveDB(data);
        return data.parties[index];
    }
  },
  transactions: {
    add: async (transaction) => {
        await new Promise(r => setTimeout(r, 800));
        const data = getDB();
        const newTx = { ...transaction, id: Math.random().toString(36).substr(2, 9), date: new Date().toISOString() };
        data.transactions.push(newTx);
        
        // Update Party Balance and Status
        const partIdx = data.parties.findIndex(p => p.id === transaction.partyId);
        if (partIdx !== -1) {
             const party = data.parties[partIdx];
             
             if (transaction.type === 'RENTAL') {
                party.balance += transaction.totalAmount - (transaction.paidAmount || 0);
                party.status = 'active'; // Has active transaction
                
                // Deduct stock
                transaction.items.forEach(txItem => {
                    const itemIdx = data.items.findIndex(i => i.id === txItem.id);
                    if (itemIdx !== -1) {
                        data.items[itemIdx].quantity -= txItem.qty;
                    }
                });
             }
        }

        saveDB(data);
        return newTx;
    }
  }
};
