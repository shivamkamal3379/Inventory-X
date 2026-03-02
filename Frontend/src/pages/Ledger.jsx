import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Edit2, Trash2, CheckCircle2, XCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { db } from '../services/db';

export default function Ledger() {
  const [parties, setParties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingParty, setEditingParty] = useState(null);

  useEffect(() => {
    fetchParties();
  }, []);

  const fetchParties = async () => {
    setLoading(true);
    const data = await db.parties.getAll();
    setParties(data);
    setLoading(false);
  };

  const filteredParties = parties.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (p.mobile && p.mobile.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const openModal = (party = null) => {
    setEditingParty(party);
    setIsModalOpen(true);
  };

  const getStatusBadge = (status) => {
      const styles = {
          'open': 'bg-green-500/10 text-green-500 border-green-500/20',
          'payment_due': 'bg-red-500/10 text-red-500 border-red-500/20',
          'closed': 'bg-blue-500/10 text-blue-500 border-blue-500/20',
          'inactive': 'bg-gray-500/10 text-gray-400 border-gray-500/20',
          'default': 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' // Provisional/Blocked
      };
      
      const labels = {
          'open': 'Open',
          'payment_due': 'Payment Due',
          'closed': 'Closed',
          'inactive': 'Inactive',
          'default': 'Default (Provisional)'
      };

      const key = status?.toLowerCase() || 'inactive';
      
      return (
        <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold", styles[key] || styles['inactive'])}>
            {labels[key] || 'Unknown'}
        </span>
      );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h2 className="text-3xl font-bold tracking-tight">Parties</h2>
            <p className="text-muted-foreground">Monitor party balances and rental status.</p>
        </div>
        <Button onClick={() => openModal()}>
            <Plus className="mr-2 h-4 w-4" /> Add Party
        </Button>
      </div>

      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
                placeholder="Search parties..." 
                className="pl-9 bg-card" 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
        </div>
      </div>

      <div className="rounded-md border border-border bg-card">
        <div className="relative w-full overflow-auto">
            <table className="w-full caption-bottom text-sm text-left">
                <thead className="[&_tr]:border-b">
                    <tr className="border-b transition-colors hover:bg-muted/50">
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Name</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Mobile</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Status</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-center">Active Items</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Balance</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                    {loading ? (
                        <tr><td colSpan={6} className="p-4 text-center">Loading...</td></tr>
                    ) : filteredParties.length === 0 ? (
                        <tr><td colSpan={6} className="p-4 text-center text-muted-foreground">No parties found.</td></tr>
                    ) : (
                        filteredParties.map((party) => (
                            <tr key={party.id} className="border-b transition-colors hover:bg-muted/50">
                                <td className="p-4 align-middle font-medium">{party.name}</td>
                                <td className="p-4 align-middle">{party.mobile}</td>
                                <td className="p-4 align-middle">
                                    {getStatusBadge(party.status)}
                                </td>
                                <td className="p-4 align-middle text-center">
                                    {party.activeItems || 0}
                                </td>
                                <td className="p-4 align-middle text-right font-mono">
                                    ₹{party.balance.toFixed(2)}
                                </td>
                                <td className="p-4 align-middle text-right">
                                    <Button variant="ghost" size="icon" onClick={() => openModal(party)}>
                                        <Edit2 className="h-4 w-4" />
                                    </Button>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
      </div>

       {/* Inline Modal */}
       <AnimatePresence>
        {isModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="w-full max-w-lg"
                >
                    <LedgerForm 
                        party={editingParty} 
                        onClose={() => setIsModalOpen(false)} 
                        onSave={() => { setIsModalOpen(false); fetchParties(); }} 
                    />
                </motion.div>
            </div>
        )}
      </AnimatePresence>
    </div>
  );
}

function LedgerForm({ party, onClose, onSave }) {
    const [formData, setFormData] = useState({
        name: party?.name || '',
        mobile: party?.mobile || '',
        email: party?.email || '',
        status: party?.status || 'inactive',
        id: party?.id || `CUST${Math.floor(Math.random()*10000)}` // Mock id for creation
    });
    const [loading, setLoading] = useState(false);

    const isDefault = formData.status === 'default';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        if (party) {
            await db.parties.update(party.id, formData);
        } else {
            // New parties default to inactive usually, unless overridden immediately
            await db.parties.add(formData);
        }
        setLoading(false);
        onSave();
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>{party ? 'Edit Party' : 'Add New Party'}</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Party Name</label>
                        <Input 
                            value={formData.name} 
                            onChange={e => setFormData({...formData, name: e.target.value})}
                            required 
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Mobile Number</label>
                        <Input 
                            value={formData.mobile} 
                            onChange={e => setFormData({...formData, mobile: e.target.value})}
                            required 
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Email (Optional)</label>
                        <Input 
                            value={formData.email} 
                            onChange={e => setFormData({...formData, email: e.target.value})}
                        />
                    </div>

                    {party && (
                        <div className="pt-4 border-t border-border">
                             <label className="flex items-center gap-2 cursor-pointer">
                                <input 
                                    type="checkbox" 
                                    className="w-4 h-4 rounded border-input"
                                    checked={isDefault}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setFormData(prev => ({ ...prev, status: 'default' }));
                                        } else {
                                            // Revert to inactive (backend will recalculate real status on next transaction or if we persist logic)
                                            // Ideally we shouldn't guess, but 'inactive' is safe fallback that will get auto-corrected if balance exists on next touch.
                                            setFormData(prev => ({ ...prev, status: 'inactive' }));
                                        }
                                    }}
                                />
                                <span className="text-sm font-medium text-yellow-500">
                                    Set as Default / Provisional (Override Status)
                                </span>
                             </label>
                             <p className="text-xs text-muted-foreground mt-1 ml-6">
                                Flag this party to avoid dealing with them. Overrides all other statuses.
                             </p>
                        </div>
                    )}

                    <div className="flex justify-end gap-2 pt-4">
                        <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
                        <Button type="submit" isLoading={loading}>{party ? 'Update' : 'Add'}</Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    );
}

// Helper for conditional classes inside the component file for simplicity
function cn(...inputs) {
  return inputs.filter(Boolean).join(" ");
}
