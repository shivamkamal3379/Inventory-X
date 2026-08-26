import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  Boxes, FileText, LayoutDashboard, LogOut, Menu, Moon, Package,
  Settings, Sun, UserRound, Users, X,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { Button } from '../components/ui/Button';
import { useTheme } from '../components/ThemeContext';
import { authService } from '../services/auth';

const NAV = [
  { to: '/dashboard', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/dashboard/contracts', label: 'Rentals', icon: FileText },
  { to: '/dashboard/inventory', label: 'Inventory', icon: Package },
  { to: '/dashboard/parties', label: 'Parties', icon: Users },
  { to: '/dashboard/agents', label: 'Agents', icon: UserRound },
  { to: '/dashboard/settings', label: 'Settings', icon: Settings },
];

function NavItems({ onNavigate }) {
  return (
    <nav className="space-y-0.5">
      {NAV.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium transition-colors',
              isActive
                ? 'bg-brand-soft text-brand'
                : 'text-text-muted hover:bg-surface-sunken hover:text-text',
            )
          }
        >
          <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

export default function DashboardLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggle } = useTheme();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close the drawer whenever the route changes, or it stays open over the page
  // the user just navigated to. Adjusting state during render (React's
  // documented pattern for "reset when a value changes") rather than in an
  // effect, so there is no extra commit with the drawer still open.
  const [lastPath, setLastPath] = useState(location.pathname);
  if (lastPath !== location.pathname) {
    setLastPath(location.pathname);
    setMobileOpen(false);
  }

  const handleLogout = () => {
    // The previous handler was a literal `// TODO: Clear auth` followed by a
    // redirect, so "Logout" navigated away while leaving the token in
    // localStorage — the next visit walked straight back in.
    authService.logout();
    navigate('/login', { replace: true });
  };

  const brand = (
    <div className="flex items-center gap-2.5">
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand">
        <Boxes className="h-4 w-4 text-brand-text" />
      </span>
      <span className="text-[14px] font-semibold tracking-tight text-text">Inventory X</span>
    </div>
  );

  const footer = (
    <div className="space-y-0.5 border-t border-line pt-3">
      <button
        onClick={toggle}
        className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium text-text-muted transition-colors hover:bg-surface-sunken hover:text-text"
      >
        {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        {theme === 'dark' ? 'Light mode' : 'Dark mode'}
      </button>
      <button
        onClick={handleLogout}
        className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium text-text-muted transition-colors hover:bg-danger-soft hover:text-danger"
      >
        <LogOut className="h-4 w-4" />
        Sign out
      </button>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-canvas">
      {/* Desktop sidebar */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-line bg-surface lg:flex">
        <div className="flex h-14 items-center px-5">{brand}</div>
        <div className="flex-1 overflow-y-auto px-3 py-2">
          <NavItems />
        </div>
        <div className="px-3 pb-4">{footer}</div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-black/45"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />
          <aside className="relative flex h-full w-64 flex-col border-r border-line bg-surface">
            <div className="flex h-14 items-center justify-between px-5">
              {brand}
              <Button variant="ghost" size="icon-sm" onClick={() => setMobileOpen(false)} aria-label="Close menu">
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto px-3 py-2">
              <NavItems onNavigate={() => setMobileOpen(false)} />
            </div>
            <div className="px-3 pb-4">{footer}</div>
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-line bg-surface/85 px-4 backdrop-blur lg:hidden">
          <Button variant="ghost" size="icon-sm" onClick={() => setMobileOpen(true)} aria-label="Open menu">
            <Menu className="h-4.5 w-4.5" />
          </Button>
          {brand}
        </header>

        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <div className="mx-auto w-full max-w-[1400px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
