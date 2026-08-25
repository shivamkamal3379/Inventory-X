import { forwardRef, useId } from 'react';
import { cn } from '../../lib/utils';

const BASE =
  'w-full bg-surface text-text placeholder:text-text-subtle ' +
  'border border-line rounded-[var(--radius-app)] ' +
  'transition-colors duration-150 ' +
  'focus:outline-none focus:border-brand focus:ring-2 focus:ring-brand/20 ' +
  'disabled:opacity-55 disabled:cursor-not-allowed';

const Input = forwardRef(function Input(
  { className, type = 'text', invalid = false, leadingIcon: Icon, ...props },
  ref,
) {
  return (
    <div className="relative">
      {Icon && (
        <Icon
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-subtle"
          aria-hidden="true"
        />
      )}
      <input
        ref={ref}
        type={type}
        aria-invalid={invalid || undefined}
        className={cn(
          BASE,
          'h-9.5 px-3 text-sm',
          Icon && 'pl-9',
          invalid && 'border-danger focus:border-danger focus:ring-danger/20',
          className,
        )}
        {...props}
      />
    </div>
  );
});

const Textarea = forwardRef(function Textarea({ className, rows = 3, ...props }, ref) {
  return (
    <textarea ref={ref} rows={rows} className={cn(BASE, 'px-3 py-2 text-sm resize-y', className)} {...props} />
  );
});

const Select = forwardRef(function Select({ className, children, invalid = false, ...props }, ref) {
  return (
    <select
      ref={ref}
      aria-invalid={invalid || undefined}
      className={cn(
        BASE,
        'h-9.5 px-3 text-sm appearance-none cursor-pointer',
        // Chevron drawn as a background image so the control stays a native
        // <select> and keeps mobile's built-in picker.
        "bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2216%22 height=%2216%22 fill=%22none%22 stroke=%22%23888%22 stroke-width=%222%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3E%3Cpath d=%22m4 6 4 4 4-4%22/%3E%3C/svg%3E')] bg-[length:16px] bg-[right_0.65rem_center] bg-no-repeat pr-9",
        invalid && 'border-danger',
        className,
      )}
      {...props}
    >
      {children}
    </select>
  );
});

/** Label + control + error, so forms stay consistent and accessible. */
function Field({ label, hint, error, required, children, className }) {
  const id = useId();
  const child =
    typeof children === 'function'
      ? children({ id, 'aria-describedby': error ? `${id}-error` : undefined })
      : children;

  return (
    <div className={cn('space-y-1.5', className)}>
      {label && (
        <label htmlFor={id} className="block text-[13px] font-medium text-text">
          {label}
          {required && <span className="ml-0.5 text-danger">*</span>}
        </label>
      )}
      {typeof children === 'function' ? child : <div>{child}</div>}
      {error ? (
        <p id={`${id}-error`} className="text-[12px] text-danger">
          {error}
        </p>
      ) : hint ? (
        <p className="text-[12px] text-text-subtle">{hint}</p>
      ) : null}
    </div>
  );
}

export { Input, Textarea, Select, Field };
