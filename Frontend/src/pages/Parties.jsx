import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Edit2, Plus, Search, Users } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { Button } from '../components/ui/Button';
import { Field, Input, Select } from '../components/ui/Input';
import { PartyStatusBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { EmptyState, ErrorState, SkeletonRows } from '../components/ui/Feedback';
import { Table, TableWrap, TBody, TD, TH, THead, TR, TRMessage } from '../components/ui/Table';
import { useToast } from '../components/ToastProvider';
import { useAsync, useDebounced } from '../hooks/useAsync';
import { db } from '../services/db';
import { errorMessage } from '../services/apiClient';
import { formatMoney, formatNumber } from '../lib/utils';

const STATUS_FILTERS = [
  { value: '', label: 'All statuses' },
  { value: 'active', label: 'Active' },
  { value: 'payment_due', label: 'Payment due' },
  { value: 'closed', label: 'Settled' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'default', label: 'Flagged' },
];

export default function Parties() {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const debounced = useDebounced(search, 300);
  const [editing, setEditing] = useState(null);
  const [formOpen, setFormOpen] = useState(false);

  const parties = useAsync(
    () => db.parties.list({ q: debounced, status, limit: 200 }),
    [debounced, status],
  );

  const rows = parties.data ?? [];

  return (
    <div>
      <PageHeader
        title="Parties"
        description="Customers, their balances, and what they are holding."
        actions={
          <Button
            onClick={() => {
              setEditing(null);
              setFormOpen(true);
            }}
          >
            <Plus className="h-4 w-4" />
            Add party
          </Button>
        }
      />

      <div className="mb-4 flex flex-wrap gap-3">
        <div className="w-full max-w-xs">
          <Input
            leadingIcon={Search}
            placeholder="Search name, mobile or ID…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search parties"
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
              <TH>Party</TH>
              <TH>Mobile</TH>
              <TH>Status</TH>
              <TH align="right">Items out</TH>
              <TH align="right">Balance</TH>
              <TH align="right">Actions</TH>
            </TR>
          </THead>
          <TBody>
            {parties.loading ? (
              <SkeletonRows rows={6} cols={6} />
            ) : parties.error ? (
              <TRMessage colSpan={6}>
                <ErrorState message={parties.error} onRetry={parties.reload} />
              </TRMessage>
            ) : !rows.length ? (
              <TRMessage colSpan={6}>
                <EmptyState
                  icon={Users}
                  title={debounced || status ? 'No matching parties' : 'No parties yet'}
                  description={
                    debounced || status
                      ? 'Try a different search or filter.'
                      : 'Register a customer before renting anything out.'
                  }
                />
              </TRMessage>
            ) : (
              rows.map((p) => {
                const balance = Number(p.balance) || 0;
                return (
                  <TR key={p.id}>
                    <TD>
                      <Link
                        to={`/dashboard/parties/${encodeURIComponent(p.id)}`}
                        className="-my-1 inline-block py-1 font-medium text-text hover:text-brand hover:underline"
                      >
                        {p.name}
                      </Link>
                      <p className="mt-0.5 font-mono text-[11px] text-text-subtle">{p.id}</p>
                    </TD>
                    <TD className="text-text-muted">{p.mobile}</TD>
                    <TD>
                      <PartyStatusBadge status={p.status} />
                    </TD>
                    <TD align="right" numeric className="text-text-muted">
                      {formatNumber(p.activeItems)}
                    </TD>
                    <TD align="right" numeric>
                      {/* Null-safe, and signed: a negative balance is credit the
                          shop is holding, not money owed. */}
                      <span
                        className={
                          balance > 0 ? 'font-medium text-danger'
                          : balance < 0 ? 'font-medium text-success'
                          : 'text-text-muted'
                        }
                      >
                        {formatMoney(Math.abs(balance))}
                        {balance < 0 && <span className="ml-1 text-[11px]">cr</span>}
                      </span>
                    </TD>
                    <TD align="right">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => {
                          setEditing(p);
                          setFormOpen(true);
                        }}
                        aria-label={`Edit ${p.name}`}
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </Button>
                    </TD>
                  </TR>
                );
              })
            )}
          </TBody>
        </Table>
      </TableWrap>

      <PartyFormModal
        open={formOpen}
        party={editing}
        onClose={() => setFormOpen(false)}
        onSaved={() => {
          setFormOpen(false);
          parties.reload();
        }}
      />
    </div>
  );
}

function PartyFormModal({ open, party, onClose, onSaved }) {
  const isEdit = Boolean(party);
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({});

  const agents = useAsync(() => db.agents.list({ limit: 200 }), [open], { immediate: open });

  const formKey = `${open}-${party?.id ?? 'new'}`;
  const [lastKey, setLastKey] = useState(formKey);
  if (formKey !== lastKey) {
    setLastKey(formKey);
    setForm({
      id: party?.id ?? '',
      name: party?.name ?? '',
      mobile: party?.mobile ?? '',
      email: party?.email ?? '',
      address: party?.address ?? '',
      agentId: party?.agentId ?? '',
      flagged: party?.status === 'default',
    });
  }

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const base = {
        name: form.name,
        mobile: form.mobile,
        email: form.email || null,
        address: form.address || null,
        agentId: form.agentId === '' ? null : Number(form.agentId),
      };

      if (isEdit) {
        // Only send `status` when the flag actually changed, so a normal edit
        // never overwrites a status the backend derived from the ledger.
        const wasFlagged = party.status === 'default';
        const payload = { ...base };
        if (form.flagged !== wasFlagged) {
          payload.status = form.flagged ? 'default' : 'active';
        }
        await db.parties.update(party.id, payload);
        toast.success('Party updated.');
      } else {
        await db.parties.create({ id: form.id.trim(), ...base });
        toast.success('Party added.');
      }
      onSaved();
    } catch (err) {
      toast.error(errorMessage(err, 'Could not save this party.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Edit party' : 'Add party'}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button form="party-form" type="submit" isLoading={saving}>
            {isEdit ? 'Save changes' : 'Add party'}
          </Button>
        </>
      }
    >
      <form id="party-form" onSubmit={handleSubmit} className="space-y-4">
        {!isEdit && (
          <Field
            label="Party ID"
            required
            hint="Your own reference, e.g. CUST001. Letters, digits, - and _ only."
          >
            {(p) => (
              <Input
                {...p}
                value={form.id}
                onChange={set('id')}
                placeholder="CUST001"
                required
                autoFocus
                className="font-mono"
              />
            )}
          </Field>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Name" required>
            {(p) => <Input {...p} value={form.name} onChange={set('name')} required />}
          </Field>
          <Field label="Mobile" required>
            {(p) => <Input {...p} value={form.mobile} onChange={set('mobile')} required />}
          </Field>
        </div>

        <Field label="Email">
          {(p) => <Input {...p} type="email" value={form.email} onChange={set('email')} />}
        </Field>

        <Field label="Address">
          {(p) => <Input {...p} value={form.address} onChange={set('address')} />}
        </Field>

        <Field label="Assigned agent">
          {(p) => (
            <Select {...p} value={form.agentId} onChange={set('agentId')}>
              <option value="">No agent</option>
              {(agents.data ?? []).map((a) => (
                <option key={a.agentId} value={a.agentId}>
                  {a.AgentName}
                </option>
              ))}
            </Select>
          )}
        </Field>

        {isEdit && (
          <label className="flex cursor-pointer items-start gap-2.5 rounded-lg border border-line bg-surface-sunken p-3">
            <input
              type="checkbox"
              className="mt-0.5 h-4 w-4 accent-[hsl(var(--warning))]"
              checked={form.flagged}
              onChange={(e) => setForm((f) => ({ ...f, flagged: e.target.checked }))}
            />
            <span>
              <span className="block text-[13px] font-medium text-text">Flag this party</span>
              <span className="mt-0.5 block text-[12px] text-text-muted">
                Marks the account as a problem customer. This overrides the automatic
                status and stays put until you clear it.
              </span>
            </span>
          </label>
        )}
      </form>
    </Modal>
  );
}
