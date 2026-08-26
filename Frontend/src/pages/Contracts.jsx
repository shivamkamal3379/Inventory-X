import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { AlertTriangle, FileText, Plus, Search, Trash2 } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { Button } from '../components/ui/Button';
import { Field, Input, Select, Textarea } from '../components/ui/Input';
import { Badge, ContractStatusBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { EmptyState, ErrorState, SkeletonRows } from '../components/ui/Feedback';
import { Table, TableWrap, TBody, TD, TH, THead, TR, TRMessage } from '../components/ui/Table';
import { useToast } from '../components/ToastProvider';
import { useAsync, useDebounced } from '../hooks/useAsync';
import { db } from '../services/db';
import { errorMessage } from '../services/apiClient';
import { formatDate, formatMoney, formatNumber, isOverdue, rentUnitLabel, toDateInput } from '../lib/utils';

const STATUS_FILTERS = [
  { value: '', label: 'All rentals' },
  { value: 'open', label: 'Open' },
  { value: 'partial', label: 'Partly returned' },
  { value: 'closed', label: 'Closed' },
];

export default function Contracts() {
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const debounced = useDebounced(search, 300);

  // The dashboard links here with ?new=1 to open the form directly.
  const [formOpen, setFormOpen] = useState(params.get('new') === '1');

  const contracts = useAsync(
    () => db.contracts.list({ q: debounced, status, limit: 200 }),
    [debounced, status],
  );

  const closeForm = () => {
    setFormOpen(false);
    if (params.get('new')) {
      params.delete('new');
      setParams(params, { replace: true });
    }
  };

  const rows = contracts.data ?? [];

  return (
    <div>
      <PageHeader
        title="Rentals"
        description="Every contract, what is still out, and what is owed on it."
        actions={
          <Button onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" />
            New rental
          </Button>
        }
      />

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="w-full max-w-xs">
          <Input
            leadingIcon={Search}
            placeholder="Search invoice no or party…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search rentals"
          />
        </div>
        <div className="w-44">
          <Select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filter by status">
            {STATUS_FILTERS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <TableWrap>
        <Table>
          <THead>
            <TR>
              <TH>Invoice</TH>
              <TH>Party</TH>
              <TH>Out on</TH>
              <TH>Due back</TH>
              <TH>Status</TH>
              <TH align="right">Items out</TH>
              <TH align="right">Balance</TH>
            </TR>
          </THead>
          <TBody>
            {contracts.loading ? (
              <SkeletonRows rows={6} cols={7} />
            ) : contracts.error ? (
              <TRMessage colSpan={7}>
                <ErrorState message={contracts.error} onRetry={contracts.reload} />
              </TRMessage>
            ) : !rows.length ? (
              <TRMessage colSpan={7}>
                <EmptyState
                  icon={FileText}
                  title={debounced || status ? 'No matching rentals' : 'No rentals yet'}
                  description={
                    debounced || status
                      ? 'Try a different search or filter.'
                      : 'Create a rental to send items out on a contract.'
                  }
                  action={
                    !debounced && !status && (
                      <Button onClick={() => setFormOpen(true)}>
                        <Plus className="h-4 w-4" />
                        Create a rental
                      </Button>
                    )
                  }
                />
              </TRMessage>
            ) : (
              rows.map((c) => {
                const overdue = isOverdue(c.expectedReturnDate, c.status);
                return (
                  <TR key={c.contractId}>
                    <TD>
                      <Link
                        to={`/dashboard/contracts/${c.contractId}`}
                        className="-my-1 inline-block py-1 font-mono text-[13px] font-medium text-text hover:text-brand hover:underline"
                      >
                        {c.contractNo}
                      </Link>
                    </TD>
                    <TD>
                      <p className="font-medium text-text">{c.PartyName || c.partyId}</p>
                      {c.AgentName && (
                        <p className="mt-0.5 text-[11px] text-text-subtle">via {c.AgentName}</p>
                      )}
                    </TD>
                    <TD className="text-text-muted">{formatDate(c.startDate)}</TD>
                    <TD>
                      {c.expectedReturnDate ? (
                        <span className={overdue ? 'font-medium text-danger' : 'text-text-muted'}>
                          {formatDate(c.expectedReturnDate)}
                        </span>
                      ) : (
                        <span className="text-text-subtle">—</span>
                      )}
                    </TD>
                    <TD>
                      <div className="flex items-center gap-1.5">
                        <ContractStatusBadge status={c.status} />
                        {overdue && (
                          <Badge tone="danger">
                            <AlertTriangle className="h-3 w-3" />
                            Overdue
                          </Badge>
                        )}
                      </div>
                    </TD>
                    <TD align="right" numeric className="text-text-muted">
                      {formatNumber(c.outstandingQty)}
                    </TD>
                    <TD align="right" numeric>
                      <span className={c.balanceDue > 0 ? 'font-medium text-danger' : 'text-text-muted'}>
                        {formatMoney(c.balanceDue)}
                      </span>
                    </TD>
                  </TR>
                );
              })
            )}
          </TBody>
        </Table>
      </TableWrap>

      <NewRentalModal open={formOpen} onClose={closeForm} />
    </div>
  );
}

/* ========================================================================== */

const emptyLine = () => ({ key: crypto.randomUUID(), itemId: '', qty: 1 });

function NewRentalModal({ open, onClose }) {
  const toast = useToast();
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);

  const [partyId, setPartyId] = useState('');
  const [agentId, setAgentId] = useState('');
  const [startDate, setStartDate] = useState(toDateInput());
  const [expectedReturn, setExpectedReturn] = useState('');
  const [advance, setAdvance] = useState('');
  const [notes, setNotes] = useState('');
  const [lines, setLines] = useState([emptyLine()]);

  const parties = useAsync(() => db.parties.list({ limit: 200 }), [open], { immediate: open });
  const items = useAsync(() => db.items.list({ limit: 200 }), [open], { immediate: open });
  const agents = useAsync(() => db.agents.list({ limit: 200 }), [open], { immediate: open });

  useEffect(() => {
    if (!open) return;
    setPartyId('');
    setAgentId('');
    setStartDate(toDateInput());
    setExpectedReturn('');
    setAdvance('');
    setNotes('');
    setLines([emptyLine()]);
  }, [open]);

  const itemsById = useMemo(
    () => Object.fromEntries((items.data ?? []).map((i) => [String(i.itemId), i])),
    [items.data],
  );

  const chosenIds = lines.map((l) => l.itemId).filter(Boolean);

  const updateLine = (key, patch) =>
    setLines((ls) => ls.map((l) => (l.key === key ? { ...l, ...patch } : l)));

  /**
   * Indicative only. The real bill is computed by the server on return, from
   * the actual dates — this just shows the daily run rate so the counter has a
   * number to quote.
   */
  const dailyRunRate = lines.reduce((sum, l) => {
    const item = itemsById[l.itemId];
    if (!item?.rent) return sum;
    return sum + Number(item.rent) * (Number(l.qty) || 0);
  }, 0);

  const validLines = lines.filter((l) => l.itemId && Number(l.qty) > 0);

  const overCommitted = validLines.some((l) => {
    const item = itemsById[l.itemId];
    return item && Number(l.qty) > item.availableQty;
  });

  const canSubmit = partyId && validLines.length > 0 && !overCommitted;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      // One request carrying every line. The old client looped and fired a
      // separate POST per item, so a failure halfway left some items reserved
      // against a rental that did not exist.
      const contract = await db.contracts.create({
        partyId,
        agentId: agentId === '' ? null : Number(agentId),
        startDate: startDate ? new Date(`${startDate}T00:00:00`).toISOString() : null,
        expectedReturnDate: expectedReturn
          ? new Date(`${expectedReturn}T00:00:00`).toISOString()
          : null,
        advancePaid: advance === '' ? 0 : Number(advance),
        notes: notes || null,
        items: validLines.map((l) => ({ itemId: Number(l.itemId), qty: Number(l.qty) })),
      });
      toast.success(`Rental ${contract.contractNo} created.`);
      onClose();
      navigate(`/dashboard/contracts/${contract.contractId}`);
    } catch (err) {
      toast.error(errorMessage(err, 'Could not create this rental.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="New rental"
      description="Everything on this form goes out on one invoice."
      size="xl"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button form="rental-form" type="submit" isLoading={saving} disabled={!canSubmit}>
            Create rental
          </Button>
        </>
      }
    >
      <form id="rental-form" onSubmit={handleSubmit} className="space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Party" required>
            {(p) => (
              <Select {...p} value={partyId} onChange={(e) => setPartyId(e.target.value)} required>
                <option value="">Select a party…</option>
                {(parties.data ?? []).map((party) => (
                  <option key={party.id} value={party.id}>
                    {party.name} ({party.id})
                    {party.status === 'default' ? ' — flagged' : ''}
                  </option>
                ))}
              </Select>
            )}
          </Field>

          <Field label="Agent">
            {(p) => (
              <Select {...p} value={agentId} onChange={(e) => setAgentId(e.target.value)}>
                <option value="">No agent</option>
                {(agents.data ?? []).map((a) => (
                  <option key={a.agentId} value={a.agentId}>
                    {a.AgentName}
                  </option>
                ))}
              </Select>
            )}
          </Field>

          <Field label="Out on" required>
            {(p) => (
              <Input {...p} type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
            )}
          </Field>

          <Field label="Expected back" hint="Used to flag overdue rentals">
            {(p) => (
              <Input
                {...p}
                type="date"
                min={startDate}
                value={expectedReturn}
                onChange={(e) => setExpectedReturn(e.target.value)}
              />
            )}
          </Field>
        </div>

        {/* Line items */}
        <div>
          <div className="mb-2 flex items-center justify-between">
            <p className="text-[13px] font-medium text-text">Items</p>
            <Button type="button" variant="secondary" size="sm" onClick={() => setLines((ls) => [...ls, emptyLine()])}>
              <Plus className="h-3.5 w-3.5" />
              Add line
            </Button>
          </div>

          <div className="space-y-2">
            {lines.map((line) => {
              const item = itemsById[line.itemId];
              const over = item && Number(line.qty) > item.availableQty;
              return (
                <div key={line.key} className="flex items-start gap-2">
                  <div className="flex-1">
                    <Select
                      value={line.itemId}
                      onChange={(e) => updateLine(line.key, { itemId: e.target.value })}
                      aria-label="Item"
                    >
                      <option value="">Select an item…</option>
                      {(items.data ?? []).map((i) => (
                        <option
                          key={i.itemId}
                          value={i.itemId}
                          // Prevent picking the same item twice: the API rejects
                          // duplicate lines, so surface it before submission.
                          disabled={
                            i.availableQty <= 0 ||
                            (chosenIds.includes(String(i.itemId)) && String(i.itemId) !== line.itemId)
                          }
                        >
                          {i.name} — {i.availableQty} available
                          {i.rent != null ? ` · ${formatMoney(i.rent)}/${rentUnitLabel(i.rentFrequency)}` : ''}
                        </option>
                      ))}
                    </Select>
                    {over && (
                      <p className="mt-1 text-[12px] text-danger">
                        Only {item.availableQty} available.
                      </p>
                    )}
                  </div>

                  <div className="w-24">
                    <Input
                      type="number"
                      min="1"
                      max={item?.availableQty ?? undefined}
                      value={line.qty}
                      onChange={(e) => updateLine(line.key, { qty: e.target.value })}
                      invalid={over}
                      aria-label="Quantity"
                    />
                  </div>

                  <Button
                    type="button"
                    variant="danger-ghost"
                    size="icon"
                    onClick={() => setLines((ls) => (ls.length > 1 ? ls.filter((l) => l.key !== line.key) : ls))}
                    disabled={lines.length === 1}
                    aria-label="Remove line"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Advance taken" hint="Held as credit until the items come back">
            {(p) => (
              <Input {...p} type="number" min="0" step="0.01" value={advance} onChange={(e) => setAdvance(e.target.value)} placeholder="0.00" />
            )}
          </Field>
          <Field label="Notes">
            {(p) => <Textarea {...p} rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />}
          </Field>
        </div>

        <div className="rounded-lg border border-line bg-surface-sunken px-4 py-3">
          <div className="flex items-baseline justify-between">
            <span className="text-[13px] text-text-muted">Indicative rate</span>
            <span className="tabular text-[15px] font-semibold text-text">
              {formatMoney(dailyRunRate)}
              <span className="ml-1 text-[12px] font-normal text-text-subtle">per day</span>
            </span>
          </div>
          <p className="mt-1.5 text-[12px] text-text-subtle">
            Nothing is charged now. The final bill is calculated from the actual days
            held when the items are returned.
          </p>
        </div>
      </form>
    </Modal>
  );
}
