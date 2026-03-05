import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Edit2, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { db } from '../services/db';

export default function Inventory() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    setLoading(true);
    const data = await db.items.getAll();
    setItems(data);
    setLoading(false);
  };

  const filteredItems = items.filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDelete = async (id) => {
    if (confirm('Are you sure?')) {
        await db.items.delete(id);
        fetchItems();
    }
  };

  const openModal = (item = null) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h2 className="text-3xl font-bold tracking-tight">Inventory</h2>
            <p className="text-muted-foreground">Manage your stock levels and items.</p>
        </div>
        <Button onClick={() => openModal()}>
            <Plus className="mr-2 h-4 w-4" /> Add Item
        </Button>
      </div>

      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
                placeholder="Search items..." 
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
                    <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Name</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Description</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Available</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Total</th>
                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                    {loading ? (
                        <tr><td colSpan={5} className="p-4 text-center">Loading...</td></tr>
                    ) : filteredItems.length === 0 ? (
                        <tr><td colSpan={5} className="p-4 text-center text-muted-foreground">No items found.</td></tr>
                    ) : (
                        filteredItems.map((item) => (
                            <tr key={item.itemId} className="border-b transition-colors hover:bg-muted/50">
                                <td className="p-4 align-middle font-medium">{item.name}</td>
                                <td className="p-4 align-middle">{item.description}</td>
                                <td className="p-4 align-middle">
                                    <span className={item.qty > 0 ? "text-green-500" : "text-red-500"}>
                                        {item.qty}
                                    </span>
                                </td>
                                <td className="p-4 align-middle">{item.qty}</td>
                                <td className="p-4 align-middle text-right">
                                    <Button variant="ghost" size="icon" onClick={() => openModal(item)}>
                                        <Edit2 className="h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => handleDelete(item.itemId)}>
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
      </div>

      {/* Inline Modal (Better to separate component but keeping here for speed) */}
      <AnimatePresence>
        {isModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="w-full max-w-lg"
                >
                    <InventoryForm 
                        item={editingItem} 
                        onClose={() => setIsModalOpen(false)} 
                        onSave={() => { setIsModalOpen(false); fetchItems(); }} 
                    />
                </motion.div>
            </div>
        )}
      </AnimatePresence>
    </div>
  );
}

function InventoryForm({ item, onClose, onSave }) {
    const [formData, setFormData] = useState({
        name: item?.name || '',
        description: item?.description || '',
        qty: item?.qty || 0
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        if (item) {
            await db.items.update(item.itemId, { 
                name: formData.name, 
                description: formData.description,
                qty: formData.qty
            });
        } else {
            await db.items.add(formData);
        }
        setLoading(false);
        onSave();
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>{item ? 'Edit Item' : 'Add New Item'}</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Item Name</label>
                        <Input 
                            value={formData.name} 
                            onChange={e => setFormData({...formData, name: e.target.value})}
                            required 
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Description</label>
                        <Input 
                            value={formData.description} 
                            onChange={e => setFormData({...formData, description: e.target.value})}
                        />
                    </div>
                    {!item && (
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Initial Quantity</label>
                            <Input 
                                type="number"
                                value={formData.qty} 
                                onChange={e => setFormData({...formData, qty: parseInt(e.target.value) || 0})}
                                required 
                            />
                        </div>
                    )}
                    <div className="flex justify-end gap-2 pt-4">
                        <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
                        <Button type="submit" isLoading={loading}>{item ? 'Update' : 'Add'}</Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    );
}
