import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Box, Layers, Zap, CheckCircle2, Sun, Moon } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useTheme } from '../components/ThemeContext';

export default function LandingPage() {
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background relative overflow-hidden text-foreground selection:bg-primary/20">
      {/* Abstract Background Shapes - Updated Colors */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
         <div className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[150px]" />
         <div className="absolute top-[40%] -right-[10%] w-[40%] h-[40%] rounded-full bg-blue-600/5 blur-[150px]" />
         <div className="absolute bottom-[0%] left-[20%] w-[30%] h-[30%] rounded-full bg-cyan-600/5 blur-[120px]" />
      </div>

      {/* Navbar */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-tr from-primary to-blue-500 rounded-lg flex items-center justify-center shadow-lg shadow-primary/20">
                <Box className="text-black w-5 h-5" />
            </div>
            <span className="font-bold text-xl tracking-tight">InventoryX</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Features</a>
            <Button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} variant="ghost" size="icon" className="text-muted-foreground hover:text-primary">
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </Button>
            <Button onClick={() => navigate('/login')} variant="outline" className="rounded-full px-6 border-white/10 hover:bg-white/5 hover:text-primary">
                Login
            </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-10 flex flex-col items-center text-center">
         <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
         >
             <span className="inline-block py-1 px-3 rounded-full bg-primary/10 text-primary text-xs font-semibold tracking-wide mb-6 border border-primary/20">
                PRO VERSION 2.0
             </span>
             <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent">
                Master Your <br />
                <span className="bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">Inventory & Rentals</span>
             </h1>
             <p className="max-w-2xl mx-auto text-lg md:text-xl text-muted-foreground mb-10 leading-relaxed">
                The most intuitive platform for modern business. Track stock, manage parties, and generate rental bills in seconds.
             </p>
             
             <div className="flex flex-col md:flex-row items-center gap-4 justify-center mb-24">
                 <Button size="lg" className="rounded-full px-8 h-12 text-md shadow-lg shadow-primary/25" onClick={() => navigate('/login')}>
                    Get Started Now <ArrowRight className="ml-2 w-4 h-4" />
                 </Button>
             </div>
         </motion.div>

         {/* Feature Preview Section: Inventory Dashboard Component */}
         <motion.div 
            className="w-full max-w-5xl mx-auto relative perspective-1000"
            initial={{ opacity: 0, y: 50, rotateX: 10 }}
            whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
         >
            <div className="relative rounded-xl border border-white/10 bg-card/50 backdrop-blur-xl shadow-2xl overflow-hidden">
                {/* Window Header */}
                <div className="h-10 border-b border-white/10 bg-black/20 flex items-center px-4 gap-2">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-green-500/80" />
                    </div>
                    <div className="ml-4 px-3 py-1 bg-white/5 rounded-md text-[10px] text-muted-foreground font-mono">
                        dashboard/inventory
                    </div>
                </div>

                {/* Dashboard Preview Content */}
                <div className="p-6 md:p-8 grid gap-8 md:grid-cols-4">
                    {/* Stats Sidebar */}
                    <div className="space-y-4">
                        <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                            <div className="text-xs text-muted-foreground mb-1">Total Stock</div>
                            <div className="text-2xl font-bold text-primary">1,248</div>
                        </div>
                        <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                            <div className="text-xs text-muted-foreground mb-1">Active Rentals</div>
                            <div className="text-2xl font-bold text-blue-400">86</div>
                        </div>
                        <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
                             <div className="text-xs text-muted-foreground mb-1">Revenue</div>
                            <div className="text-2xl font-bold text-purple-400">₹8.4L</div>
                        </div>
                    </div>

                    {/* Main Table Area */}
                    <div className="md:col-span-3 space-y-4">
                        <div className="flex items-center justify-between pb-4 border-b border-white/5">
                            <h3 className="font-semibold text-lg">Live Inventory Status</h3>
                            <button className="text-xs bg-primary text-black px-3 py-1.5 rounded-md font-medium">
                                + Add Item
                            </button>
                        </div>
                        
                        <div className="space-y-3">
                            {[
                                { name: 'Canon ImageClass', cat: 'Printers', stock: 12, status: 'Available' },
                                { name: 'Dell UltraSharp 24"', cat: 'Monitors', stock: 8, status: 'Low Stock' },
                                { name: 'ErgoChair Pro', cat: 'Furniture', stock: 45, status: 'Available' },
                                { name: 'MacBook Pro M3', cat: 'Laptops', stock: 0, status: 'Out of Stock' },
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-white/5">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center text-xs font-bold text-gray-400">
                                            {item.name[0]}
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium">{item.name}</div>
                                            <div className="text-xs text-muted-foreground">{item.cat}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4 text-sm">
                                        <span className="font-mono text-muted-foreground">{item.stock}</span>
                                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                                            item.status === 'Available' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                                            item.status === 'Low Stock' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                            'bg-red-500/10 text-red-400 border-red-500/20'
                                        }`}>
                                            {item.status}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
            
             {/* Floating Badge */}
            <motion.div 
                className="absolute -top-6 -right-6 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-bold shadow-xl rotate-12 hidden md:block"
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            >
                Real-time Sync
            </motion.div>
         </motion.div>

         <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
            <div className="p-6 rounded-2xl bg-card border border-white/5 hover:border-primary/50 transition-colors group">
                <Box className="w-10 h-10 text-primary mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-xl font-bold mb-2">Smart Inventory</h3>
                <p className="text-muted-foreground">Track every item in real-time. Automated alerts for low stock levels.</p>
            </div>
            <div className="p-6 rounded-2xl bg-card border border-white/5 hover:border-blue-500/50 transition-colors group">
                <Layers className="w-10 h-10 text-blue-400 mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-xl font-bold mb-2">Party Ledger</h3>
                <p className="text-muted-foreground">Manage client relationships, track balances, and active rentals.</p>
            </div>
            <div className="p-6 rounded-2xl bg-card border border-white/5 hover:border-purple-500/50 transition-colors group">
                <Zap className="w-10 h-10 text-purple-400 mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-xl font-bold mb-2">Instant Billing</h3>
                <p className="text-muted-foreground">Generate professional invoices in seconds. Support for ₹ INR Currency.</p>
            </div>
         </div>
      </main>
    </div>
  );
}
