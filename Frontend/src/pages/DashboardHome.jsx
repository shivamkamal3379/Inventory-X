import { Link } from 'react-router-dom';
import {
  AlertTriangle, ArrowRight, FileText, IndianRupee, Package, Users,
} from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { EmptyState, ErrorState, Skeleton } from '../components/ui/Feedback';
import { Meter, RankedBars, RevenueTrend, StatTile } from '../components/ui/Charts';
import { useAsync } from '../hooks/useAsync';
import { db } from '../services/db';
import { formatMoney, formatNumber, relativeTime } from '../lib/utils';

const ACTIVITY_TONE = {
  RENTAL: { tone: 'info', label: 'Rented' },
  RETURN: { tone: 'success', label: 'Returned' },
  PAYMENT: { tone: 'brand', label: 'Payment' },
};

export default function DashboardHome() {
  const stats = useAsync(() => db.dashboard.stats(), []);
  const activity = useAsync(() => db.dashboard.activity(8), []);
  const trend = useAsync(() => db.dashboard.trend(30), []);
  const topItems = useAsync(() => db.dashboard.topItems(5), []);

  const s = stats.data;

  return (
    <div>
      <PageHeader
        title="Overview"
        description="Live position across stock, rentals and balances."
        actions={
          <Link to="/dashboard/contracts?new=1">
            <Button>
              <FileText className="h-4 w-4" />
              New rental
            </Button>
          </Link>
        }
      />

      {/* KPI row */}
      {stats.loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-line bg-surface p-4">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="mt-3 h-7 w-20" />
            </div>
          ))}
        </div>
      ) : stats.error ? (
        <Card>
          <CardContent>
            <ErrorState message={stats.error} onRetry={stats.reload} />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile
            icon={IndianRupee}
            label="Revenue this month"
            value={formatMoney(s?.revenueThisMonth)}
            caption="Recognised when items come back"
          />
          {/* The net figure can be negative when advances held exceed rent
              charged so far. Showing that as a negative "outstanding balance"
              reads as an error, so the tile flips to describe the credit. */}
          <StatTile
            icon={Users}
            label={s?.outstandingBalance < 0 ? 'Advances held' : 'Outstanding balance'}
            value={formatMoney(Math.abs(s?.outstandingBalance ?? 0))}
            tone={s?.outstandingBalance > 0 ? 'warning' : 'neutral'}
            caption={
              s?.outstandingBalance < 0
                ? 'Customer money not yet earned'
                : `${formatNumber(s?.partiesWithDues)} part${s?.partiesWithDues === 1 ? 'y' : 'ies'} owing`
            }
          />
          <StatTile
            icon={FileText}
            label="Open rentals"
            value={formatNumber(s?.openContracts)}
            caption={`${formatNumber(s?.totalContracts)} all time`}
          />
          <StatTile
            icon={AlertTriangle}
            label="Overdue"
            value={formatNumber(s?.overdueContracts)}
            tone={s?.overdueContracts > 0 ? 'danger' : 'neutral'}
            caption="Past their expected return date"
          />
        </div>
      )}

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        {/* Revenue trend */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Revenue, last 30 days</CardTitle>
          </CardHeader>
          <CardContent>
            {trend.loading ? (
              <Skeleton className="h-[168px] w-full" />
            ) : trend.error ? (
              <ErrorState message={trend.error} onRetry={trend.reload} />
            ) : (
              <RevenueTrend data={trend.data || []} />
            )}
          </CardContent>
        </Card>

        {/* Stock position */}
        <Card>
          <CardHeader>
            <CardTitle>Stock position</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {stats.loading ? (
              <>
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </>
            ) : (
              <>
                <Meter
                  value={s?.utilisationPct ?? 0}
                  label="Utilisation"
                  caption={`${formatNumber(s?.totalRentedOutQty)} of ${formatNumber(
                    (s?.totalRentedOutQty || 0) + (s?.totalAvailableQty || 0),
                  )} units are out`}
                />
                <dl className="grid grid-cols-2 gap-3 border-t border-line pt-4">
                  <div>
                    <dt className="text-[12px] text-text-muted">Available</dt>
                    <dd className="tabular mt-0.5 text-lg font-semibold text-text">
                      {formatNumber(s?.totalAvailableQty)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-[12px] text-text-muted">Rented out</dt>
                    <dd className="tabular mt-0.5 text-lg font-semibold text-text">
                      {formatNumber(s?.totalRentedOutQty)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-[12px] text-text-muted">Distinct items</dt>
                    <dd className="tabular mt-0.5 text-lg font-semibold text-text">
                      {formatNumber(s?.totalItems)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-[12px] text-text-muted">Parties</dt>
                    <dd className="tabular mt-0.5 text-lg font-semibold text-text">
                      {formatNumber(s?.totalParties)}
                    </dd>
                  </div>
                </dl>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        {/* Activity */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Recent activity</CardTitle>
            <Link
              to="/dashboard/contracts"
              /* min-h-8 plus padding: an 18px-tall link is an unreliable tap
                 target on touch, well under the 24px minimum. */
              className="-mr-2 inline-flex min-h-8 items-center gap-1 rounded-md px-2 text-[12px] font-medium text-brand hover:bg-brand-soft hover:underline"
            >
              All rentals <ArrowRight className="h-3 w-3" />
            </Link>
          </CardHeader>
          <CardContent>
            {activity.loading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : activity.error ? (
              <ErrorState message={activity.error} onRetry={activity.reload} />
            ) : !activity.data?.length ? (
              <EmptyState
                icon={FileText}
                title="Nothing has happened yet"
                description="Rentals, returns and payments will appear here as they are recorded."
              />
            ) : (
              <ul className="divide-y divide-line">
                {activity.data.map((a) => {
                  const meta = ACTIVITY_TONE[a.type] ?? { tone: 'neutral', label: a.type };
                  return (
                    <li key={`${a.type}-${a.id}`} className="flex items-center gap-3 py-2.5 first:pt-0 last:pb-0">
                      <Badge tone={meta.tone}>{meta.label}</Badge>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-[13px] font-medium text-text">
                          {a.PartyName || a.partyId}
                        </p>
                        <p className="truncate text-[12px] text-text-muted">
                          {a.Item || a.contractNo || '—'}
                          {a.itemQty > 0 && ` · ${a.itemQty} unit${a.itemQty === 1 ? '' : 's'}`}
                        </p>
                      </div>
                      <div className="shrink-0 text-right">
                        <p className="tabular text-[13px] font-medium text-text">
                          {a.amount ? formatMoney(a.amount) : '—'}
                        </p>
                        <p className="text-[11px] text-text-subtle">{relativeTime(a.TxnDate)}</p>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Top items */}
        <Card>
          <CardHeader>
            <CardTitle>Most rented</CardTitle>
          </CardHeader>
          <CardContent>
            {topItems.loading ? (
              <div className="space-y-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-8 w-full" />
                ))}
              </div>
            ) : !topItems.data?.length ? (
              <EmptyState
                icon={Package}
                title="No rentals yet"
                description="Once items go out, the busiest ones show up here."
              />
            ) : (
              <RankedBars data={topItems.data} valueKey="unitsRented" labelKey="name" />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
