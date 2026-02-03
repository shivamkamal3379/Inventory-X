import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, FileText, Check, Trash2, ArrowRightLeft } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { db } from '../services/db';

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState('rental'); // 'rental' or 'return'

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    setLoading(true);
    // Since we didn't implement getAll in db for transactions, assuming we persist them or user just adds.
    // For now, let's just show local state or mock if db.js doesn't have getAll.
    // Let's rely on adding new ones mostly. 
    // Ideally we add db.transactions.getAll() but for now let's just show empty or "Recent".
    setTransactions(db.parties.getAll().then(() => [])); // Placeholder
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h2 className="text-3xl font-bold tracking-tight">Transactions</h2>
            <p className="text-muted-foreground">Create new rentals and process returns.</p>
        </div>
        <div className="flex gap-2">
            <Button onClick={() => { setModalMode('return'); setIsModalOpen(true); }} variant="secondary">
                <ArrowRightLeft className="mr-2 h-4 w-4" /> Return Items
            </Button>
            <Button onClick={() => { setModalMode('rental'); setIsModalOpen(true); }}>
                <Plus className="mr-2 h-4 w-4" /> New Rental
            </Button>
        </div>
      </div>

      <div className="rounded-md border border-border bg-card p-12 text-center text-muted-foreground">
        <FileText className="mx-auto h-12 w-12 opacity-50 mb-4" />
        <h3 className="text-lg font-medium">Transaction History</h3>
        <p>Your recent transactions will appear here.</p>
        <p className="text-xs text-muted-foreground mt-2">(History View Not Implemented in this Demo Step)</p>
      </div>

      {/* Transaction Modal */}
      <AnimatePresence>
        {isModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="w-full max-w-4xl my-8"
                >
                    <TransactionForm 
                        mode={modalMode}
                        onClose={() => setIsModalOpen(false)} 
                        onSave={() => { setIsModalOpen(false); fetchTransactions(); }} 
                    />
                </motion.div>
            </div>
        )}
      </AnimatePresence>
    </div>
  );
}

function TransactionForm({ mode, onClose, onSave }) {
    const [step, setStep] = useState(1);
    const [parties, setParties] = useState([]);
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    
    // Form State
    const [selectedParty, setSelectedParty] = useState('');
    const [lineItems, setLineItems] = useState([{ id: Date.now(), itemId: '', qty: 1, price: 0, name: '' }]);
    const [paidAmount, setPaidAmount] = useState(0);
    const [billSummary, setBillSummary] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            const [p, i] = await Promise.all([db.parties.getAll(), db.items.getAll()]);
            setParties(p);
            setItems(i);
        };
        loadData();
    }, []);

    const grandTotal = lineItems.reduce((sum, item) => sum + (item.price * item.qty), 0);

    const handleAddItem = () => {
        setLineItems([...lineItems, { id: Date.now(), itemId: '', qty: 1, price: 0, name: '' }]);
    };

    const handleRemoveItem = (id) => {
        if (lineItems.length > 1) {
            setLineItems(lineItems.filter(i => i.id !== id));
        }
    };

    const updateLineItem = (id, field, value) => {
        const newItems = lineItems.map(item => {
            if (item.id === id) {
                const updates = { [field]: value };
                if (field === 'itemId') {
                    const dbItem = items.find(i => i.id === value);
                    if (dbItem) {
                        // For rentals, use price. For returns, usually price is 0 unless restocking fee?
                        // Let's keep price logic for now so "Total Value" is tracked, but for Returns maybe we don't charge?
                        // Or maybe we treat "Total" as "Refund Amount"?
                        // Use Case: Simple Return -> Just restocking.
                        updates.price = mode === 'rental' ? dbItem.price : 0; 
                        updates.name = dbItem.name;
                    }
                }
                return { ...item, ...updates };
            }
            return item;
        });
        setLineItems(newItems);
    };

    const handleSubmit = async () => {
        setLoading(true);
        const transaction = {
            partyId: selectedParty,
            items: lineItems.filter(i => i.itemId), // save items
            totalAmount: grandTotal,
            paidAmount: Number(paidAmount),
            type: mode === 'rental' ? 'RENTAL' : 'RETURN'
        };
        
        await db.transactions.add(transaction);
        setBillSummary(transaction);
        setLoading(false);
        setStep(2); // Show Bill
    };

    if (step === 2 && billSummary) {
        return (
            <Card className="bg-white text-black">
                <CardHeader className="border-b">
                    <CardTitle className="flex justify-between items-center text-black">
                        <span>{mode === 'rental' ? 'Invoice Generated' : 'Return Processed'}</span>
                        <Check className="h-6 w-6 text-green-500" />
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6 pt-6 text-black">
                    <div className="flex justify-between text-sm">
                        <span className="font-bold">Summary</span>
                        <span>{new Date().toLocaleDateString()}</span>
                    </div>
                    <div className="space-y-2 border-b pb-4">
                         {lineItems.map((item, idx) => (
                             item.itemId && (
                                <div key={idx} className="flex justify-between text-sm">
                                    <span>{item.name} (x{item.qty})</span>
                                    <span>{mode === 'rental' ? `₹${(item.price * item.qty).toFixed(2)}` : '-'}</span>
                                </div>
                             )
                         ))}
                    </div>
                    {mode === 'rental' && (
                        <>
                            <div className="flex justify-between font-bold text-lg">
                                <span>Total</span>
                                <span>₹{grandTotal.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-muted-foreground text-sm">
                                <span>Paid</span>
                                <span>₹{parseFloat(paidAmount).toFixed(2)}</span>
                            </div>
                             <div className="flex justify-between font-bold text-primary">
                                <span>Balance Due</span>
                                <span>₹{(grandTotal - paidAmount).toFixed(2)}</span>
                            </div>
                        </>
                    )}
                    {mode === 'return' && (
                         <div className="flex justify-between font-bold text-lg">
                            <span>Balance Adjustment</span>
                            <span>-{parseFloat(paidAmount).toFixed(2)} (Paid)</span>
                        </div>
                    )}

                    <div className="flex justify-end pt-4 no-print">
                        <Button onClick={onSave}>Close</Button>
                    </div>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>{mode === 'rental' ? 'Create New Rental' : 'Return Items'}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    {/* Party Selection */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Select Party</label>
                        <select 
                            className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                            value={selectedParty}
                            onChange={(e) => setSelectedParty(e.target.value)}
                        >
                            <option value="" className="text-black">-- Select a Party --</option>
                            {parties.map(p => (
                                <option key={p.id} value={p.id} className="text-black">
                                    {p.name} {p.activeItems > 0 ? `(Has ${p.activeItems} items)` : ''}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Line Items */}
                    <div className="space-y-4">
                        <label className="text-sm font-medium">Items</label>
                        {lineItems.map((item, index) => (
                            <div key={item.id} className="flex gap-2 items-start">
                                <select 
                                    className="flex-1 h-10 rounded-md border border-input bg-transparent px-3 py-2 text-sm text-foreground"
                                    value={item.itemId}
                                    onChange={(e) => updateLineItem(item.id, 'itemId', e.target.value)}
                                >
                                    <option value="" className="text-black">Select Item</option>
                                    {items.map(i => (
                                        <option key={i.id} value={i.id} className="text-black" disabled={mode === 'rental' && i.quantity <= 0}>
                                            {i.name} {mode === 'rental' ? `(Avail: ${i.quantity})` : ''}
                                        </option>
                                    ))}
                                </select>
                                <Input 
                                    type="number" 
                                    className="w-20" 
                                    placeholder="Qty"
                                    min="1"
                                    value={item.qty}
                                    onChange={(e) => updateLineItem(item.id, 'qty', parseInt(e.target.value))}
                                />
                                {mode === 'rental' && (
                                    <div className="h-10 flex items-center px-3 border border-input rounded-md min-w-[80px] justify-end bg-muted/50">
                                        ₹{(item.price * item.qty).toFixed(2)}
                                    </div>
                                )}
                                <Button variant="ghost" size="icon" className="text-destructive h-10 w-10" onClick={() => handleRemoveItem(item.id)}>
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        ))}
                        <Button variant="outline" size="sm" onClick={handleAddItem} className="w-full border-dashed">
                            <Plus className="mr-2 h-4 w-4" /> Add Item
                        </Button>
                    </div>

                    {/* Payment */}
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
                        <div className="space-y-2">
                             <label className="text-sm font-medium">{mode === 'rental' ? 'Payment Received' : 'Settlement Amount (e.g. Refund/Payoff)'}</label>
                             <Input 
                                type="number" 
                                value={paidAmount} 
                                onChange={(e) => setPaidAmount(e.target.value)}
                             />
                        </div>
                        {mode === 'rental' && (
                            <div className="text-right space-y-1">
                                <div className="text-sm text-muted-foreground">Grand Total</div>
                                <div className="text-2xl font-bold">₹{grandTotal.toFixed(2)}</div>
                            </div>
                        )}
                    </div>

                    <div className="flex justify-end gap-2 pt-4">
                        <Button variant="outline" onClick={onClose}>Cancel</Button>
                        <Button 
                            onClick={handleSubmit} 
                            isLoading={loading}
                            disabled={!selectedParty || lineItems.every(i => !i.itemId)}
                        >
                            {mode === 'rental' ? 'Generate Bill' : 'Process Return'}
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
