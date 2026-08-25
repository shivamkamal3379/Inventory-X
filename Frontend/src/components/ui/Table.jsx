import { cn } from '../../lib/utils';

/** Wrapper that scrolls horizontally on its own, so the page body never does. */
export function TableWrap({ className, children }) {
  return (
    <div className={cn('bg-surface border border-line rounded-xl shadow-xs overflow-hidden', className)}>
      <div className="overflow-x-auto">{children}</div>
    </div>
  );
}

export function Table({ className, ...props }) {
  return <table className={cn('w-full text-sm border-collapse', className)} {...props} />;
}

export function THead({ className, ...props }) {
  return <thead className={cn('bg-surface-sunken', className)} {...props} />;
}

export function TH({ className, align = 'left', ...props }) {
  return (
    <th
      scope="col"
      className={cn(
        'px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-text-muted',
        'border-b border-line whitespace-nowrap',
        align === 'right' && 'text-right',
        align === 'center' && 'text-center',
        align === 'left' && 'text-left',
        className,
      )}
      {...props}
    />
  );
}

export function TBody({ className, ...props }) {
  return <tbody className={cn('divide-y divide-line', className)} {...props} />;
}

export function TR({ className, interactive = false, ...props }) {
  return (
    <tr
      className={cn(
        'transition-colors',
        interactive && 'hover:bg-surface-sunken cursor-pointer',
        className,
      )}
      {...props}
    />
  );
}

export function TD({ className, align = 'left', numeric = false, ...props }) {
  return (
    <td
      className={cn(
        'px-4 py-3 text-text align-middle',
        align === 'right' && 'text-right',
        align === 'center' && 'text-center',
        numeric && 'tabular',
        className,
      )}
      {...props}
    />
  );
}

/** Full-width message row for empty / loading / error states inside a table. */
export function TRMessage({ colSpan, children }) {
  return (
    <tr>
      <td colSpan={colSpan} className="px-4 py-14 text-center">
        {children}
      </td>
    </tr>
  );
}
