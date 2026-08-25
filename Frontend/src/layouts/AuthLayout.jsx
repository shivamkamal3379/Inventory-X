import { Outlet, Link } from 'react-router-dom';
import { Boxes } from 'lucide-react';

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-canvas lg:grid lg:grid-cols-2">
      {/* Form column */}
      <div className="flex min-h-screen flex-col justify-center px-6 py-12 lg:min-h-0 lg:px-16">
        <div className="mx-auto w-full max-w-sm">
          <Link to="/" className="mb-10 inline-flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand">
              <Boxes className="h-4.5 w-4.5 text-brand-text" />
            </span>
            <span className="text-[15px] font-semibold tracking-tight text-text">Inventory X</span>
          </Link>
          <Outlet />
        </div>
      </div>

      {/* Brand column — decorative, so it is hidden rather than stacked on mobile */}
      <div className="relative hidden overflow-hidden bg-surface-sunken border-l border-line lg:block">
        <div
          className="absolute inset-0 opacity-[0.35]"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, hsl(var(--line-strong)) 1px, transparent 0)',
            backgroundSize: '28px 28px',
          }}
          aria-hidden="true"
        />
        <div className="relative flex h-full flex-col justify-center px-16">
          <blockquote className="max-w-md">
            <p className="text-2xl font-semibold leading-snug tracking-tight text-text">
              Know exactly what is out, what is due back, and who owes what.
            </p>
            <p className="mt-5 text-sm leading-relaxed text-text-muted">
              Rental contracts with per-day billing, live stock, and a party ledger that
              always reconciles.
            </p>
          </blockquote>

          <dl className="mt-12 grid max-w-md grid-cols-3 gap-6 border-t border-line pt-8">
            {[
              ['Stock', 'Never oversold'],
              ['Billing', 'Priced by duration'],
              ['Ledger', 'Always balanced'],
            ].map(([term, detail]) => (
              <div key={term}>
                <dt className="text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
                  {term}
                </dt>
                <dd className="mt-1 text-[13px] text-text">{detail}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
}
