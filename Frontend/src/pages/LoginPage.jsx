import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { KeyRound, User } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Field, Input } from '../components/ui/Input';
import { authService } from '../services/auth';
import { errorMessage } from '../services/apiClient';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await authService.login(username.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(errorMessage(err, 'Sign in failed. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-xl font-semibold tracking-tight text-text">Sign in</h1>
      <p className="mt-1.5 text-[13px] text-text-muted">
        Enter your credentials to reach the dashboard.
      </p>

      <form onSubmit={handleSubmit} className="mt-7 space-y-4" noValidate>
        <Field label="Username" required>
          {(props) => (
            <Input
              {...props}
              autoComplete="username"
              autoFocus
              leadingIcon={User}
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              invalid={Boolean(error)}
              required
            />
          )}
        </Field>

        <Field label="Password" required>
          {(props) => (
            <Input
              {...props}
              type="password"
              autoComplete="current-password"
              leadingIcon={KeyRound}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              invalid={Boolean(error)}
              required
            />
          )}
        </Field>

        {error && (
          <div role="alert" className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2.5">
            <p className="text-[13px] text-danger">{error}</p>
          </div>
        )}

        <Button type="submit" size="lg" className="w-full" isLoading={loading}>
          Sign in
        </Button>
      </form>

      {/* The old page printed "Use admin / password to login" on the sign-in
          screen. Real credentials are configured per deployment via
          FIRST_ADMIN_USERNAME / FIRST_ADMIN_PASSWORD. */}
      <p className="mt-6 text-center text-[12px] text-text-subtle">
        Lost access? Ask your administrator to reset your account.
      </p>
    </div>
  );
}
