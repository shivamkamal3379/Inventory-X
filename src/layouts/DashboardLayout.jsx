import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Package, Wallet, Receipt, LogOut, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../lib/utils';
import { Button } from '../components/ui/Button';

export default function DashboardLayout() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();

  const handleLogout = () => {
    // TODO: Clear auth
    navigate('/');
  };

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: Package, label: 'Inventory', path: '/dashboard/inventory' },
    { icon: Wallet, label: 'Ledger', path: '/dashboard/ledger' },
    { icon: Receipt, label: 'Transactions', path: '/dashboard/transactions' },
  ];

  return (
    <div className="min-h-screen bg-background flex text-foreground">
      {/* Sidebar for Desktop */}
      <aside 
        className={cn(
            "hidden md:flex flex-col border-r border-border bg-card/50 backdrop-blur-xl transition-all duration-300",
            isSidebarOpen ? "w-64" : "w-20"
        )}
      >
        <div className="h-16 flex items-center px-6 border-b border-border justify-between">
           {isSidebarOpen && <span className="font-bold text-xl bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent">InventoryX</span>}
           <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!isSidebarOpen)}>
                {isSidebarOpen ? <X size={18} /> : <Menu size={18} />}
           </Button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
            {navItems.map((item) => (
                <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/dashboard'} // Only exact match for dashboard home
                    className={({ isActive }) => cn(
                        "flex items-center gap-3 px-3 py-2 rounded-lg transition-all",
                        isActive 
                            ? "bg-primary/10 text-primary" 
                            : "text-muted-foreground hover:bg-muted hover:text-foreground",
                        !isSidebarOpen && "justify-center"
                    )}
                >
                    <item.icon size={20} />
                    {isSidebarOpen && <span>{item.label}</span>}
                </NavLink>
            ))}
        </nav>

        <div className="p-4 border-t border-border">
            <Button variant="ghost" className={cn("w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10", !isSidebarOpen && "justify-center")} onClick={handleLogout}>
                <LogOut size={20} />
                {isSidebarOpen && <span className="ml-2">Logout</span>}
            </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-16 border-b border-border flex items-center px-6 md:hidden">
            <span className="font-bold text-lg">InventoryX</span>
            {/* Mobile Menu Logic would go here */}
        </header>
        
        <div className="flex-1 overflow-auto p-6 relative">
            {/* Ambient Background */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 opacity-20 pointer-events-none">
                 <div className="absolute top-[10%] left-[20%] w-[30%] h-[30%] rounded-full bg-primary/20 blur-[100px]" />
            </div>
            
            <Outlet />
        </div>
      </main>
    </div>
  );
}
