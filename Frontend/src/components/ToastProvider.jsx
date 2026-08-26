import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';
import { cn } from '../lib/utils';

const ToastContext = createContext(null);

const TONES = {
  success: { icon: CheckCircle2, cls: 'text-success', ring: 'border-success/25' },
  error: { icon: AlertCircle, cls: 'text-danger', ring: 'border-danger/25' },
  info: { icon: Info, cls: 'text-info', ring: 'border-info/25' },
};

/**
 * App-wide notifications.
 *
 * Every page previously swallowed failures into console.error, so a failed save
 * looked identical to a successful one. Mutations now report through here.
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const timers = useRef(new Map());

  const dismiss = useCallback((id) => {
    setToasts((list) => list.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  }, []);

  const push = useCallback(
    (message, { tone = 'info', duration = 4500 } = {}) => {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      setToasts((list) => [...list, { id, message, tone }]);
      if (duration > 0) {
        timers.current.set(id, setTimeout(() => dismiss(id), duration));
      }
      return id;
    },
    [dismiss],
  );

  const api = useMemo(
    () => ({
      toast: push,
      success: (m, o) => push(m, { ...o, tone: 'success' }),
      // Errors stay visible longer — they usually carry an action to take.
      error: (m, o) => push(m, { duration: 7000, ...o, tone: 'error' }),
      info: (m, o) => push(m, { ...o, tone: 'info' }),
      dismiss,
    }),
    [push, dismiss],
  );

  return (
    <ToastContext.Provider value={api}>
      {children}
      {createPortal(
        <div
          className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-[min(24rem,calc(100vw-2rem))] flex-col gap-2"
          role="region"
          aria-label="Notifications"
        >
          <AnimatePresence initial={false}>
            {toasts.map((t) => {
              const meta = TONES[t.tone] ?? TONES.info;
              const Icon = meta.icon;
              return (
                <motion.div
                  key={t.id}
                  layout
                  initial={{ opacity: 0, y: 12, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, x: 24, scale: 0.97 }}
                  transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                  role={t.tone === 'error' ? 'alert' : 'status'}
                  className={cn(
                    'pointer-events-auto flex items-start gap-3 rounded-[var(--radius-app)]',
                    'border bg-surface-raised px-3.5 py-3 shadow-lg',
                    meta.ring,
                  )}
                >
                  <Icon className={cn('mt-0.5 h-4 w-4 shrink-0', meta.cls)} aria-hidden="true" />
                  <p className="flex-1 text-[13px] leading-relaxed text-text">{t.message}</p>
                  <button
                    onClick={() => dismiss(t.id)}
                    className="shrink-0 rounded p-0.5 text-text-subtle hover:text-text"
                    aria-label="Dismiss notification"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>,
        document.body,
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside a ToastProvider');
  return ctx;
}
