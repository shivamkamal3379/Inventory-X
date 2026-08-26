import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

const SIZES = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
};

/**
 * Rendered through a portal so it is never clipped by an ancestor's overflow,
 * and locks body scroll while open.
 */
export function Modal({ open, onClose, title, description, size = 'md', children, footer }) {
  const panelRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;

    const onKey = (e) => {
      if (e.key === 'Escape') onClose?.();
    };
    document.addEventListener('keydown', onKey);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    // Move focus into the dialog so keyboard users are not left behind on the
    // page underneath.
    const focusTimer = window.setTimeout(() => panelRef.current?.focus(), 0);

    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = previousOverflow;
      window.clearTimeout(focusTimer);
    };
  }, [open, onClose]);

  return createPortal(
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto p-4 sm:items-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 bg-black/45 backdrop-blur-[2px]"
            onClick={onClose}
            aria-hidden="true"
          />
          <motion.div
            ref={panelRef}
            tabIndex={-1}
            role="dialog"
            aria-modal="true"
            aria-label={title}
            initial={{ opacity: 0, scale: 0.97, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 8 }}
            transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
            className={cn(
              'relative z-10 my-auto w-full bg-surface border border-line rounded-xl shadow-lg outline-none',
              SIZES[size],
            )}
          >
            {(title || description) && (
              <div className="flex items-start justify-between gap-4 px-5 py-4 border-b border-line">
                <div className="min-w-0">
                  {title && <h2 className="text-[15px] font-semibold text-text">{title}</h2>}
                  {description && <p className="mt-0.5 text-[13px] text-text-muted">{description}</p>}
                </div>
                <Button variant="ghost" size="icon-sm" onClick={onClose} aria-label="Close dialog">
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )}
            <div className="px-5 py-4">{children}</div>
            {footer && (
              <div className="flex justify-end gap-2 px-5 py-3.5 border-t border-line bg-surface-sunken rounded-b-xl">
                {footer}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>,
    document.body,
  );
}

/**
 * Replaces window.confirm() for destructive actions — the native dialog cannot
 * be styled, cannot say what will actually happen, and is blocked in some
 * embedded browsers.
 */
export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title = 'Are you sure?',
  description,
  confirmLabel = 'Confirm',
  tone = 'danger',
  isLoading = false,
}) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant={tone} onClick={onConfirm} isLoading={isLoading}>
            {confirmLabel}
          </Button>
        </>
      }
    >
      <p className="text-sm text-text-muted">{description}</p>
    </Modal>
  );
}
