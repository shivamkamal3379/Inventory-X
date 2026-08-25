import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, FileText, Mail, MapPin, Phone } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { ContractStatusBadge, PartyStatusBadge } from '../components/ui/Badge';
import { EmptyState, ErrorState, Skeleton } from '../components/ui/Feedback';
import { Table, TBody, TD, TH, THead, TR } from '../components/ui/Table';
import { StatTile } from '../components/ui/Charts';
import { useAsync } from '../hooks/useAsync';
import { db } from '../services/db';
import { formatDate, formatMoney, formatNumber } from '../lib/utils';

export default function PartyDetail() {
  const { id } = useParams();
  const ledger = useAsync(() => db.parties.ledger(id), [id]);

  if (ledger.loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (ledger.error) {
    return (
      <Card>
        <CardContent>
          <ErrorState message={ledger.error} onRetry={ledger.reload} />
        </CardContent>
      </Card>
    );
  }

  const { party, contracts, returns, payments, totals } = ledger.data;
  const balance = Number(totals.balance) || 0;

  return (
    <div>
      <div className="mb-6 flex items-start gap-3">
        <Link to="/dashboard/parties" aria-label="Back to parties">
          <Button variant="ghost" size="icon-sm" tabIndex={-1} aria-hidden="true">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-xl font-semibold tracking-tight text-text">{party.name}</h1>
            <PartyStatusBadge status={party.status} />
          </div>
          <p className="mt-1 font-mono text-[12px] text-text-subtle">{party.id}</p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label={balance < 0 ? 'Credit held' : 'Balance due'}
          value={formatMoney(Math.abs(balance))}
          tone={balance > 0 ? 'danger' : balance < 0 ? 'success' : 'neutral'}
          caption={balance > 0 ? 'Owed to you' : balance < 0 ? 'Owed to the party' : 'Settled'}
        />
        <StatTile label="Items held" value={formatNumber(totals.activeItems)} caption="Currently out" />
        <StatTile label="Open rentals" value={formatNumber(totals.openContracts)} caption={`${contracts.length} total`} />
        <StatTile label="Rent charged" value={formatMoney(totals.rentCharged)} caption="Lifetime" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Contact</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2.5">
            <p className="flex items-center gap-2 text-[13px] text-text">
              <Phone className="h-3.5 w-3.5 text-text-subtle" />
              {party.mobile}
            </p>
            {party.email && (
              <p className="flex items-center gap-2 text-[13px] text-text">
                <Mail className="h-3.5 w-3.5 text-text-subtle" />
                {party.email}
              </p>
            )}
            {party.address && (
              <p className="flex items-start gap-2 text-[13px] text-text">
                <MapPin className="mt-0.5 h-3.5 w-3.5 shrink-0 text-text-subtle" />
                {party.address}
              </p>
            )}
            {party.agentName && (
              <p className="border-t border-line pt-2.5 text-[12px] text-text-muted">
                Agent: {party.agentName}
              </p>
            )}
            <p className="text-[12px] text-text-subtle">
              Registered {formatDate(party.dateCreated)}
            </p>
          </CardContent>
        </Card>

        <Card className="min-w-0 lg:col-span-2">
          <CardHeader>
            <CardTitle>Rentals</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {!contracts.length ? (
              <div className="p-5">
                <EmptyState icon={FileText} title="No rentals yet" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                <THead>
                  <TR>
                    <TH>Invoice</TH>
                    <TH>Out on</TH>
                    <TH>Status</TH>
                    <TH align="right">Balance</TH>
                  </TR>
                </THead>
                <TBody>
                  {contracts.map((c) => (
                    <TR key={c.contractId}>
                      <TD>
                        <Link
                          to={`/dashboard/contracts/${c.contractId}`}
                          className="-my-1 inline-block py-1 font-mono text-[13px] font-medium text-text hover:text-brand hover:underline"
                        >
                          {c.contractNo}
                        </Link>
                      </TD>
                      <TD className="text-text-muted">{formatDate(c.startDate)}</TD>
                      <TD>
                        <ContractStatusBadge status={c.status} />
                      </TD>
                      <TD align="right" numeric>
                        <span className={c.balanceDue > 0 ? 'font-medium text-danger' : 'text-text-muted'}>
                          {formatMoney(c.balanceDue)}
                        </span>
                      </TD>
                    </TR>
                  ))}
                </TBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>Returns</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {!returns.length ? (
              <div className="p-5">
                <EmptyState title="No returns yet" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                <THead>
                  <TR>
                    <TH>Item</TH>
                    <TH align="right">Qty</TH>
                    <TH align="right">Days</TH>
                    <TH align="right">Charged</TH>
                    <TH>Date</TH>
                  </TR>
                </THead>
                <TBody>
                  {returns.map((r) => (
                    <TR key={r.id}>
                      <TD>{r.Item}</TD>
                      <TD align="right" numeric>{r.qty}</TD>
                      <TD align="right" numeric className="text-text-muted">{r.daysHeld}</TD>
                      <TD align="right" numeric>{formatMoney(r.rentCharged)}</TD>
                      <TD className="text-text-muted">{formatDate(r.returnDate)}</TD>
                    </TR>
                  ))}
                </TBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>Payments</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {!payments.length ? (
              <div className="p-5">
                <EmptyState title="No payments recorded" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                <THead>
                  <TR>
                    <TH>Date</TH>
                    <TH>Method</TH>
                    <TH align="right">Amount</TH>
                  </TR>
                </THead>
                <TBody>
                  {payments.map((p) => (
                    <TR key={p.id}>
                      <TD className="text-text-muted">{formatDate(p.paidAt)}</TD>
                      <TD className="text-text-muted">{p.method || '—'}</TD>
                      <TD align="right" numeric>{formatMoney(p.amount)}</TD>
                    </TR>
                  ))}
                </TBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
