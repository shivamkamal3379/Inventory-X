import { useState } from 'react';
import { Monitor, Moon, Sun } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Field, Input } from '../components/ui/Input';
import { useTheme } from '../components/ThemeContext';
import { useToast } from '../components/ToastProvider';
import { useAsync } from '../hooks/useAsync';
import { authService } from '../services/auth';
import { errorMessage, API_BASE_URL } from '../services/apiClient';
import { cn, formatDate } from '../lib/utils';

const THEME_OPTIONS = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
];

export default function Settings() {
  const { preference, setPreference } = useTheme();
  const me = useAsync(() => authService.me(), []);

  return (
    <div className="max-w-2xl">
      <PageHeader title="Settings" description="Your account and how the app looks." />

      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
          </CardHeader>
          <CardContent>
            {me.loading ? (
              <p className="text-[13px] text-text-muted">Loading…</p>
            ) : me.error ? (
              <p className="text-[13px] text-danger">{me.error}</p>
            ) : (
              <dl className="grid gap-3 sm:grid-cols-2">
                <div>
                  <dt className="text-[12px] text-text-muted">Signed in as</dt>
                  <dd className="mt-0.5 text-[14px] font-medium text-text">{me.data.username}</dd>
                </div>
                <div>
                  <dt className="text-[12px] text-text-muted">Member since</dt>
                  <dd className="mt-0.5 text-[14px] text-text">{formatDate(me.data.created_at)}</dd>
                </div>
              </dl>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>
              System follows whatever your device is set to, and switches with it.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-2">
              {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  onClick={() => setPreference(value)}
                  className={cn(
                    'flex flex-col items-center gap-2 rounded-lg border px-3 py-4 transition-colors',
                    preference === value
                      ? 'border-brand bg-brand-soft text-brand'
                      : 'border-line text-text-muted hover:border-line-strong hover:text-text',
                  )}
                  aria-pressed={preference === value}
                >
                  <Icon className="h-4.5 w-4.5" />
                  <span className="text-[13px] font-medium">{label}</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <ChangePasswordCard />

        <Card>
          <CardHeader>
            <CardTitle>Connection</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-2">
              <div className="flex justify-between text-[13px]">
                <dt className="text-text-muted">API endpoint</dt>
                <dd className="font-mono text-text">{API_BASE_URL}</dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function ChangePasswordCard() {
  const toast = useToast();
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [saving, setSaving] = useState(false);

  const mismatch = confirm.length > 0 && next !== confirm;
  const tooShort = next.length > 0 && next.length < 8;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (mismatch || tooShort) return;
    setSaving(true);
    try {
      await authService.changePassword(current, next);
      toast.success('Password changed.');
      setCurrent('');
      setNext('');
      setConfirm('');
    } catch (err) {
      toast.error(errorMessage(err, 'Could not change the password.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change password</CardTitle>
        <CardDescription>At least 8 characters.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Current password" required>
            {(p) => (
              <Input
                {...p}
                type="password"
                autoComplete="current-password"
                value={current}
                onChange={(e) => setCurrent(e.target.value)}
                required
              />
            )}
          </Field>
          <Field label="New password" required error={tooShort ? 'Must be at least 8 characters.' : undefined}>
            {(p) => (
              <Input
                {...p}
                type="password"
                autoComplete="new-password"
                value={next}
                onChange={(e) => setNext(e.target.value)}
                invalid={tooShort}
                required
              />
            )}
          </Field>
          <Field label="Confirm new password" required error={mismatch ? 'Passwords do not match.' : undefined}>
            {(p) => (
              <Input
                {...p}
                type="password"
                autoComplete="new-password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                invalid={mismatch}
                required
              />
            )}
          </Field>
          <Button type="submit" isLoading={saving} disabled={mismatch || tooShort || !current || !next}>
            Change password
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
