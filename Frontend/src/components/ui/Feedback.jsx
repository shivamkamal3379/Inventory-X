import { AlertCircle, Inbox, Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

/** Grey block that mimics the shape of content while it loads. */
export function Skeleton({ className }) {
  return <div className={cn('animate-pulse rounded bg-line', className)} aria-hidden="true" />;
}

export function SkeletonRows({ rows = 5, cols = 4 }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, r) => (
        <tr key={r} className="border-b border-line last:border-0">
          {Array.from({ length: cols }).map((__, c) => (
            <td key={c} className="px-4 py-3.5">
              <Skeleton className={cn('h-3.5', c === 0 ? 'w-2/5' : 'w-3/5')} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

export function Spinner({ className }) {
  return <Loader2 className={cn('h-4 w-4 animate-spin', className)} aria-hidden="true" />;
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-4">
      <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-surface-sunken">
        <Icon className="h-5 w-5 text-text-subtle" aria-hidden="true" />
      </div>
      <p className="text-sm font-medium text-text">{title}</p>
      {description && <p className="mt-1 max-w-sm text-[13px] text-text-muted">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

/**
 * Shown when a fetch fails. Always offers a retry — the previous pages logged
 * the error to the console and rendered an empty table, which is
 * indistinguishable from "you have no data".
 */
export function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-4">
      <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-danger-soft">
        <AlertCircle className="h-5 w-5 text-danger" aria-hidden="true" />
      </div>
      <p className="text-sm font-medium text-text">Could not load this</p>
      <p className="mt-1 max-w-sm text-[13px] text-text-muted">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" className="mt-4" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
