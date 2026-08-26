import { useEffect } from 'react';
import { Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';
import { onUnauthorized } from '../services/apiClient';

export default function ProtectedRoute() {
  const location = useLocation();
  const navigate = useNavigate();

  // If the API rejects our token mid-session, route to /login through the
  // router rather than by assigning window.location, which would hard-reload
  // the app and lose any unsaved form state.
  useEffect(
    () =>
      onUnauthorized(() => {
        navigate('/login', { replace: true, state: { from: location.pathname } });
      }),
    [navigate, location.pathname],
  );

  if (!authService.isAuthenticated()) {
    // Remember where they were headed so login can send them back there.
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
