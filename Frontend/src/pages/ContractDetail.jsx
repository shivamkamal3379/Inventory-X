import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  ArrowLeft, Banknote, Boxes, PackageCheck, Printer,
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { Field, Input, Textarea } from '../components/ui/Input';
import { Badge, ContractStatusBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { ErrorState, Skeleton, Spinner } from '../components/ui/Feedback';
import { Table, TableWrap, TBody, TD, TH, THead, TR } from '../components/ui/Table';
import { useToast } from '../components/ToastProvider';
import { useAsync } from '../hooks/useAsync';
import { db } from '../services/db';
import { errorMessage } from '../services/apiClient';
import { formatDate, formatMoney, formatNumber, isOverdue, rentUnitLabel, toDateInput } from '../lib/utils';

export default function ContractDetail() {
  const { id } = useParams();
  const contract = useAsync(() => db.contracts.get(id), [id]);
  const [returnOpen, setReturnOpen] = useState(false);
  const [payOpen, setPayOpen] = useState(false);

  const c = contract.data;

  if (contract.loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (contract.error) {
    return (
      <Card>
        <CardContent>
          <ErrorState message={contract.error} onRetry={contract.reload} />
        </CardContent>
      </Card>
    );
  }

  const outstanding = c.lines.reduce((sum, l) => sum + l.outstandingQty, 0);
  const overdue = isOverdue(c.expectedReturnDate, c.status);

  return (
    <div>
      {/* Toolbar — excluded from print */}
      <div className="no-print mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          {/* The label goes on the anchor: a screen reader announces the link,
              and a label on the inner button is not read as the link name. */}
          <Link to="/dashboard/contracts" aria-label="Back to rentals">
            {/* The anchor carries the name; the inner button is decorative and is
                hidden from assistive tech so the link is announced once, not twice. */}
            <Button variant="ghost" size="icon-sm" tabIndex={-1} aria-hidden="true">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-mono text-lg font-semibold tracking-tight text-text">
                {c.contractNo}
              </h1>
              <ContractStatusBadge status={c.status} />
              {overdue && <Badge tone="danger">Overdue</Badge>}
            </div>
            <p className="mt-0.5 text-[13px] text-text-muted">
              {c.PartyName} · out {formatDate(c.startDate)}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => window.print()}>
            <Printer className="h-4 w-4" />
            Print
          </Button>
          {c.balanceDue > 0 && (
            <Button variant="secondary" onClick={() => setPayOpen(true)}>
              <Banknote className="h-4 w-4" />
              Record payment
            </Button>
          )}
          {outstanding > 0 && (
            <Button onClick={() => setReturnOpen(true)}>
              <PackageCheck className="h-4 w-4" />
              Return items
            </Button>
          )}
        </div>
      </div>

      {/* Invoice sheet */}
      <div className="print-sheet mx-auto max-w-3xl rounded-xl border border-line bg-surface p-6 shadow-xs sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand">
                <Boxes className="h-4 w-4 text-brand-text" />
              </span>
              <span className="text-[15px] font-semibold tracking-tight text-text">Inventory X</span>
            </div>
            <p className="mt-2 text-[12px] text-text-muted">Rental contract</p>
          </div>
          <div className="text-right">
            <p className="font-mono text-[15px] font-semibold text-text">{c.contractNo}</p>
            <p className="mt-0.5 text-[12px] text-text-muted">Issued {formatDate(c.createdAt)}</p>
          </div>
        </div>

        <div className="grid gap-6 border-b border-line py-6 sm:grid-cols-2">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
              Rented to
            </p>
            <p className="mt-1.5 text-[14px] font-medium text-text">{c.PartyName}</p>
            <p className="font-mono text-[12px] text-text-muted">{c.partyId}</p>
            {c.AgentName && (
              <p className="mt-1 text-[12px] text-text-muted">Agent: {c.AgentName}</p>
            )}
          </div>
          <div className="sm:text-right">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
              Period
            </p>
            <p className="mt-1.5 text-[13px] text-text">Out: {formatDate(c.startDate)}</p>
            <p className="text-[13px] text-text">
              Due back: {c.expectedReturnDate ? formatDate(c.expectedReturnDate) : 'Open-ended'}
            </p>
            {c.closedAt && (
              <p className="text-[13px] text-text-muted">Closed: {formatDate(c.closedAt)}</p>
            )}
          </div>
        </div>

        {/* Lines */}
        <div className="py-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line">
                <th className="pb-2 text-left text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
                  Item
                </th>
                <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
                  Rate
                </th>
                <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
                  Out
                </th>
                <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
                  Back
                </th>
                <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-wider text-text-subtle">
                  Charged
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {c.lines.map((l) => (
                <tr key={l.id}>
                  <td className="py-2.5 text-text">{l.Item}</td>
                  <td className="tabular py-2.5 text-right text-text-muted">
                    {formatMoney(l.ratePerUnit)}
                    <span className="ml-0.5 text-[11px]">/{rentUnitLabel(l.rentFrequency)}</span>
                  </td>
                  <td className="tabular py-2.5 text-right text-text">{formatNumber(l.qty)}</td>
                  <td className="tabular py-2.5 text-right text-text-muted">
                    {formatNumber(l.returnedQty)}
                    {l.outstandingQty > 0 && (
                      <span className="ml-1 text-[11px] text-warning">
                        ({l.outstandingQty} out)
                      </span>
                    )}
                  </td>
                  <td className="tabular py-2.5 text-right font-medium text-text">
                    {formatMoney(l.accruedRent)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Totals */}
        <div className="flex justify-end border-t border-line pt-5">
          <dl className="w-full max-w-xs space-y-2">
            <div className="flex justify-between text-[13px]">
              <dt className="text-text-muted">Rent charged</dt>
              <dd className="tabular text-text">{formatMoney(c.accruedRent)}</dd>
            </div>
            <div className="flex justify-between text-[13px]">
              <dt className="text-text-muted">Advance</dt>
              <dd className="tabular text-text">− {formatMoney(c.advancePaid)}</dd>
            </div>
            <div className="flex justify-between text-[13px]">
              <dt className="text-text-muted">Payments</dt>
              <dd className="tabular text-text">− {formatMoney(c.totalPaid)}</dd>
            </div>
            <div className="flex justify-between border-t border-line pt-2.5 text-[15px] font-semibold">
              <dt className="text-text">{c.balanceDue < 0 ? 'Credit held' : 'Balance due'}</dt>
              <dd className={`tabular ${c.balanceDue > 0 ? 'text-danger' : 'text-success'}`}>
                {formatMoney(Math.abs(c.balanceDue))}
              </dd>
            </div>
          </dl>
        </div>

        {c.notes && (
          <div className="mt-6 border-t border-line pt-5">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-text-subtle">Notes</p>
            <p className="mt-1.5 whitespace-pre-line text-[13px] text-text-muted">{c.notes}</p>
          </div>
        )}

        <p className="mt-8 border-t border-line pt-4 text-[11px] text-text-subtle">
          Part periods are billed as full periods. Rent accrues from the date items go
          out until the date they are returned.
        </p>
      </div>

      <ReturnModal
        open={returnOpen}
        contract={c}
        onClose={() => setReturnOpen(false)}
        onDone={() => {
          setReturnOpen(false);
          contract.reload();
        }}
      />
      <PaymentModal
        open={payOpen}
        contract={c}
        onClose={() => setPayOpen(false)}
        onDone={() => {
          setPayOpen(false);
          contract.reload();
        }}
      />
    </div>
  );
}

/* ========================================================================== */

function ReturnModal({ open, contract, onClose, onDone }) {
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [returnDate, setReturnDate] = useState(toDateInput());
  const [amountPaid, setAmountPaid] = useState('');
  const [qtys, setQtys] = useState({});
  const [quote, setQuote] = useState(null);
  const [quoting, setQuoting] = useState(false);

  const outstandingLines = (contract?.lines ?? []).filter((l) => l.outstandingQty > 0);

  useEffect(() => {
    if (!open) return;
    setReturnDate(toDateInput());
    setAmountPaid('');
    setQtys(Object.fromEntries(outstandingLines.map((l) => [l.id, l.outstandingQty])));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, contract?.contractId]);

  // Ask the server to price the return whenever the date changes. This is the
  // same calculation the commit will run, so the number shown is the number
  // charged.
  useEffect(() => {
    if (!open || !returnDate) return undefined;
    let cancelled = false;
    setQuoting(true);
    db.contracts
      .quote(contract.contractId, new Date(`${returnDate}T00:00:00`).toISOString())
      .then((q) => {
        if (!cancelled) setQuote(q);
      })
      .catch(() => {
        if (!cancelled) setQuote(null);
      })
      .finally(() => {
        if (!cancelled) setQuoting(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open, returnDate, contract?.contractId]);

  const selected = outstandingLines
    .map((l) => ({ lineId: l.id, qty: Number(qtys[l.id]) || 0 }))
    .filter((l) => l.qty > 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const result = await db.contracts.returnItems(contract.contractId, {
        items: selected,
        returnDate: new Date(`${returnDate}T00:00:00`).toISOString(),
        amountPaid: amountPaid === '' ? 0 : Number(amountPaid),
      });
      toast.success(`Returned. Rent charged: ${formatMoney(result.totalCharged)}.`);
      onDone();
    } catch (err) {
      toast.error(errorMessage(err, 'Could not process this return.'));
    } finally {
      setSaving(false);
    }
  };

  // The quote prices a full return; it only matches the bill exactly when every
  // outstanding unit is being handed back.
  const isFullReturn =
    selected.length === outstandingLines.length &&
    outstandingLines.every((l) => Number(qtys[l.id]) === l.outstandingQty);

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Return items"
      description="Rent is charged for the period between the out date and the return date."
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button form="return-form" type="submit" isLoading={saving} disabled={!selected.length}>
            Confirm return
          </Button>
        </>
      }
    >
      <form id="return-form" onSubmit={handleSubmit} className="space-y-5">
        <Field label="Return date" required>
          {(p) => (
            <Input
              {...p}
              type="date"
              min={toDateInput(contract?.startDate)}
              value={returnDate}
              onChange={(e) => setReturnDate(e.target.value)}
              required
            />
          )}
        </Field>

        <div>
          <p className="mb-2 text-[13px] font-medium text-text">Items coming back</p>
          <TableWrap>
            <Table>
              <THead>
                <TR>
                  <TH>Item</TH>
                  <TH align="right">Still out</TH>
                  <TH align="right">Returning</TH>
                </TR>
              </THead>
              <TBody>
                {outstandingLines.map((l) => (
                  <TR key={l.id}>
                    <TD>{l.Item}</TD>
                    <TD align="right" numeric className="text-text-muted">
                      {l.outstandingQty}
                    </TD>
                    <TD align="right">
                      <Input
                        type="number"
                        min="0"
                        max={l.outstandingQty}
                        value={qtys[l.id] ?? 0}
                        onChange={(e) =>
                          setQtys((q) => ({
                            ...q,
                            [l.id]: Math.min(Number(e.target.value) || 0, l.outstandingQty),
                          }))
                        }
                        className="ml-auto w-20 text-right"
                        aria-label={`Quantity returning for ${l.Item}`}
                      />
                    </TD>
                  </TR>
                ))}
              </TBody>
            </Table>
          </TableWrap>
        </div>

        <div className="rounded-lg border border-line bg-surface-sunken px-4 py-3">
          <div className="flex items-center justify-between">
            <span className="text-[13px] text-text-muted">
              {isFullReturn ? 'Rent for this return' : 'Rent if everything is returned'}
            </span>
            <span className="tabular text-[15px] font-semibold text-text">
              {quoting ? <Spinner /> : formatMoney(quote?.subtotal ?? 0)}
            </span>
          </div>
          {quote?.lines?.length > 0 && (
            <p className="mt-1.5 text-[12px] text-text-subtle">
              {quote.lines[0].daysHeld} day{quote.lines[0].daysHeld === 1 ? '' : 's'} held ·
              billed as {quote.lines[0].periodsCharged} period
              {quote.lines[0].periodsCharged === 1 ? '' : 's'}
            </p>
          )}
          {!isFullReturn && selected.length > 0 && (
            <p className="mt-1.5 text-[12px] text-warning">
              You are returning part of the contract — the actual charge will be lower
              and is confirmed on the invoice.
            </p>
          )}
        </div>

        <Field label="Payment collected now" hint="Leave blank to bill it to the party's account">
          {(p) => (
            <Input
              {...p}
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
              value={amountPaid}
              onChange={(e) => setAmountPaid(e.target.value)}
            />
          )}
        </Field>
      </form>
    </Modal>
  );
}

function PaymentModal({ open, contract, onClose, onDone }) {
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('cash');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (!open) return;
    setAmount(contract?.balanceDue > 0 ? String(contract.balanceDue) : '');
    setMethod('cash');
    setNotes('');
  }, [open, contract?.balanceDue]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await db.contracts.addPayment(contract.contractId, {
        amount: Number(amount),
        method,
        notes: notes || null,
      });
      toast.success('Payment recorded.');
      onDone();
    } catch (err) {
      toast.error(errorMessage(err, 'Could not record this payment.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Record payment"
      description={`Outstanding on this contract: ${formatMoney(contract?.balanceDue ?? 0)}`}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button form="payment-form" type="submit" isLoading={saving} disabled={!Number(amount)}>
            Record payment
          </Button>
        </>
      }
    >
      <form id="payment-form" onSubmit={handleSubmit} className="space-y-4">
        <Field label="Amount" required>
          {(p) => (
            <Input
              {...p}
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              autoFocus
            />
          )}
        </Field>
        <Field label="Method">
          {(p) => (
            <Input {...p} value={method} onChange={(e) => setMethod(e.target.value)} placeholder="cash / upi / bank" />
          )}
        </Field>
        <Field label="Notes">
          {(p) => <Textarea {...p} rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />}
        </Field>
      </form>
    </Modal>
  );
}
