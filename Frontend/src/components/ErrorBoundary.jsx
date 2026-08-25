import { Component } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from './ui/Button';

/**
 * Catches render-time crashes so one broken page shows a recovery screen
 * instead of unmounting the whole app to a blank white document.
 */
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('Unhandled UI error:', error, info);
  }

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas p-6">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-danger-soft">
            <AlertTriangle className="h-6 w-6 text-danger" />
          </div>
          <h1 className="text-lg font-semibold text-text">Something went wrong</h1>
          <p className="mt-2 text-sm text-text-muted">
            The page hit an unexpected error. Reloading usually clears it.
          </p>
          <pre className="mt-4 max-h-32 overflow-auto rounded-lg bg-surface-sunken p-3 text-left text-[11px] text-text-muted">
            {String(this.state.error?.message || this.state.error)}
          </pre>
          <div className="mt-5 flex justify-center gap-2">
            <Button variant="secondary" onClick={() => this.setState({ error: null })}>
              Dismiss
            </Button>
            <Button onClick={() => window.location.reload()}>Reload page</Button>
          </div>
        </div>
      </div>
    );
  }
}
