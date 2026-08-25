import { cn } from '../../lib/utils';

const TONES = {
  neutral: 'bg-surface-sunken text-text-muted border-line',
  brand: 'bg-brand-soft text-brand border-brand/20',
  success: 'bg-success-soft text-success border-success/20',
  warning: 'bg-warning-soft text-warning border-warning/25',
  danger: 'bg-danger-soft text-danger border-danger/20',
  info: 'bg-info-soft text-info border-info/20',
};

export function Badge({ tone = 'neutral', className, children, dot = false, ...props }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5',
        'text-[11px] font-medium whitespace-nowrap',
        TONES[tone] ?? TONES.neutral,
        className,
      )}
      {...props}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />}
      {children}
    </span>
  );
}

/* Party status. The backend emits these exact lowercase values; the previous UI
   mapped a key called "open" that the API never sends, so every row rendered
   "Unknown". */
const PARTY_STATUS = {
  active: { tone: 'success', label: 'Active' },
  payment_due: { tone: 'danger', label: 'Payment due' },
  closed: { tone: 'neutral', label: 'Settled' },
  inactive: { tone: 'neutral', label: 'Inactive' },
  default: { tone: 'warning', label: 'Flagged' },
};

export function PartyStatusBadge({ status }) {
  const meta = PARTY_STATUS[status] ?? { tone: 'neutral', label: status || 'Unknown' };
  return <Badge tone={meta.tone} dot>{meta.label}</Badge>;
}

const CONTRACT_STATUS = {
  open: { tone: 'info', label: 'Open' },
  partial: { tone: 'warning', label: 'Partly returned' },
  closed: { tone: 'success', label: 'Closed' },
  cancelled: { tone: 'neutral', label: 'Cancelled' },
};

export function ContractStatusBadge({ status }) {
  const meta = CONTRACT_STATUS[status] ?? { tone: 'neutral', label: status || 'Unknown' };
  return <Badge tone={meta.tone} dot>{meta.label}</Badge>;
}
