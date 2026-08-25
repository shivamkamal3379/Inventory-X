import { forwardRef } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

const VARIANTS = {
  primary:
    'bg-brand text-brand-text hover:bg-brand-hover shadow-xs disabled:hover:bg-brand',
  secondary:
    'bg-surface text-text border border-line hover:bg-surface-sunken hover:border-line-strong shadow-xs',
  ghost: 'text-text-muted hover:bg-surface-sunken hover:text-text',
  danger: 'bg-danger text-danger-text hover:opacity-90 shadow-xs',
  'danger-ghost': 'text-danger hover:bg-danger-soft',
  link: 'text-brand underline-offset-4 hover:underline p-0 h-auto',
};

const SIZES = {
  sm: 'h-8 px-3 text-[13px] gap-1.5 rounded-md',
  md: 'h-9.5 px-4 text-sm gap-2 rounded-[var(--radius-app)]',
  lg: 'h-11 px-5 text-[15px] gap-2 rounded-[var(--radius-app)]',
  icon: 'h-9 w-9 rounded-md',
  'icon-sm': 'h-7.5 w-7.5 rounded-md',
};

/**
 * `isLoading` also disables the button — a submit handler that is already
 * in flight must not be re-entered by a second click.
 */
const Button = forwardRef(function Button(
  { className, variant = 'primary', size = 'md', isLoading = false, children, disabled, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      disabled={disabled || isLoading}
      className={cn(
        'inline-flex items-center justify-center font-medium whitespace-nowrap',
        'transition-colors duration-150 select-none',
        'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring',
        'disabled:opacity-55 disabled:pointer-events-none',
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
      {...props}
    >
      {isLoading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
      {children}
    </button>
  );
});

export { Button };
