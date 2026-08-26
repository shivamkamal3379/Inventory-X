import { Link } from 'react-router-dom';
import { ArrowRight, Boxes, CalendarClock, FileText, ShieldCheck, Users, Wallet } from 'lucide-react';
import { Button } from '../components/ui/Button';

const FEATURES = [
  {
    icon: FileText,
    title: 'Contracts, not loose rows',
    body: 'One rental is one invoice with every item on it — printable, and returnable in a single step.',
  },
  {
    icon: CalendarClock,
    title: 'Billed by how long it was out',
    body: 'Daily, weekly or monthly rates. The charge is computed from the actual dates on return.',
  },
  {
    icon: Boxes,
    title: 'Stock that cannot go negative',
    body: 'Availability is locked while a rental is written, so two counters can never sell the same unit.',
  },
  {
    icon: Wallet,
    title: 'A ledger that reconciles',
    body: 'Advances, rent and payments all post to the party balance. Nothing is tracked in someone’s head.',
  },
  {
    icon: Users,
    title: 'Parties and agents',
    body: 'Know who is holding what, who owes money, and which agent placed the rental.',
  },
  {
    icon: ShieldCheck,
    title: 'Locked down by default',
    body: 'Every endpoint requires a signed token. Registration closes once your admin account exists.',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-canvas">
      <header className="sticky top-0 z-30 border-b border-line bg-canvas/85 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand">
              <Boxes className="h-4 w-4 text-brand-text" />
            </span>
            <span className="text-[14px] font-semibold tracking-tight text-text">Inventory X</span>
          </div>
          <Link to="/login">
            <Button size="sm">Sign in</Button>
          </Link>
        </div>
      </header>

      <main>
        <section className="mx-auto max-w-6xl px-5 pb-16 pt-20 text-center sm:pt-28">
          <p className="mb-4 inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-3 py-1 text-[12px] text-text-muted">
            Rental inventory management
          </p>
          <h1 className="mx-auto max-w-3xl text-4xl font-semibold leading-[1.1] tracking-tight text-text sm:text-5xl">
            Know exactly what is out, what is due back, and who owes what.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-[15px] leading-relaxed text-text-muted">
            Track equipment, rent it out on a proper contract, take it back with the
            bill already calculated, and keep every party balance straight.
          </p>
          <div className="mt-8 flex justify-center">
            <Link to="/login">
              <Button size="lg">
                Open the dashboard
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 pb-24">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ icon: Icon, title, body }) => (
              <div key={title} className="rounded-xl border border-line bg-surface p-5 shadow-xs">
                <span className="mb-3.5 flex h-9 w-9 items-center justify-center rounded-lg bg-brand-soft">
                  <Icon className="h-4.5 w-4.5 text-brand" aria-hidden="true" />
                </span>
                <h2 className="text-[14px] font-semibold text-text">{title}</h2>
                <p className="mt-1.5 text-[13px] leading-relaxed text-text-muted">{body}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-5 py-6 text-[12px] text-text-subtle sm:flex-row">
          <span>Inventory X — rental inventory management</span>
          <span>Built for small rental operations</span>
        </div>
      </footer>
    </div>
  );
}
