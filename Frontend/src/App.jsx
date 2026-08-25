import { lazy, Suspense } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ThemeProvider } from './components/ThemeContext';
import { ToastProvider } from './components/ToastProvider';
import { ErrorBoundary } from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import AuthLayout from './layouts/AuthLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';

// The dashboard is loaded on demand. A visitor who only sees the landing or
// login page never downloads it.
const DashboardLayout = lazy(() => import('./layouts/DashboardLayout'));
const DashboardHome = lazy(() => import('./pages/DashboardHome'));
const Inventory = lazy(() => import('./pages/Inventory'));
const Parties = lazy(() => import('./pages/Parties'));
const PartyDetail = lazy(() => import('./pages/PartyDetail'));
const Contracts = lazy(() => import('./pages/Contracts'));
const ContractDetail = lazy(() => import('./pages/ContractDetail'));
const Agents = lazy(() => import('./pages/Agents'));
const Settings = lazy(() => import('./pages/Settings'));

function RouteFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-line border-t-brand" />
      <span className="sr-only">Loading…</span>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <BrowserRouter>
            <Suspense fallback={<RouteFallback />}>
              <Routes>
                <Route path="/" element={<LandingPage />} />

                <Route element={<AuthLayout />}>
                  <Route path="/login" element={<LoginPage />} />
                </Route>

                <Route element={<ProtectedRoute />}>
                  <Route path="/dashboard" element={<DashboardLayout />}>
                    <Route index element={<DashboardHome />} />
                    <Route path="contracts" element={<Contracts />} />
                    <Route path="contracts/:id" element={<ContractDetail />} />
                    <Route path="inventory" element={<Inventory />} />
                    <Route path="parties" element={<Parties />} />
                    <Route path="parties/:id" element={<PartyDetail />} />
                    <Route path="agents" element={<Agents />} />
                    <Route path="settings" element={<Settings />} />
                  </Route>
                </Route>

                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </BrowserRouter>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
