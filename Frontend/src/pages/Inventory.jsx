import { useState } from 'react';
import { Edit2, Package, Plus, Search, Trash2 } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { Button } from '../components/ui/Button';
import { Field, Input, Select, Textarea } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Modal, ConfirmDialog } from '../components/ui/Modal';
import { EmptyState, ErrorState, SkeletonRows } from '../components/ui/Feedback';
import { Table, TableWrap, TBody, TD, TH, THead, TR, TRMessage } from '../components/ui/Table';
import { useToast } from '../components/ToastProvider';
import { useAsync, useDebounced } from '../hooks/useAsync';
import { db } from '../services/db';
import { errorMessage } from '../services/apiClient';
import { formatMoney, formatNumber, rentUnitLabel } from '../lib/utils';

export default function Inventory() {
  const [search, setSearch] = useState('');
  const debounced = useDebounced(search, 300);
  const [editing, setEditing] = useState(null);
  const [formOpen, setFormOpen] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [deletePending, setDeletePending] = useState(false);

  const toast = useToast();
  const items = useAsync(() => db.items.list({ q: debounced, limit: 200 }), [debounced]);

  const openCreate = () => {
    setEditing(null);
    setFormOpen(true);
  };

  const openEdit = (item) => {
    setEditing(item);
    setFormOpen(true);
  };

  const confirmDelete = async () => {
    setDeletePending(true);
    try {
      await db.items.remove(deleting.itemId);
      toast.success(`"${deleting.name}" deleted.`);
      setDeleting(null);
      items.reload();
    } catch (err) {
      toast.error(errorMessage(err, 'Could not delete this item.'));
    } finally {
      setDeletePending(false);
    }
  };

  const rows = items.data ?? [];

  return (
    <div>
      <PageHeader
        title="Inventory"
        description="What you own, what is on the shelf, and what it rents for."
        actions={
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" />
            Add item
          </Button>
        }
      />

      <div className="mb-4 max-w-xs">
        <Input
          leadingIcon={Search}
          placeholder="Search items…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search items"
        />
      </div>

      <TableWrap>
        <Table>
          <THead>
            <TR>
              <TH>Item</TH>
              <TH align="right">Available</TH>
              <TH align="right">Out</TH>
              <TH align="right">Total</TH>
              <TH align="right">Rate</TH>
              <TH align="right">Actions</TH>
            </TR>
          </THead>
          <TBody>
            {items.loading ? (
              <SkeletonRows rows={6} cols={6} />
            ) : items.error ? (
              <TRMessage colSpan={6}>
                <ErrorState message={items.error} onRetry={items.reload} />
              </TRMessage>
            ) : !rows.length ? (
              <TRMessage colSpan={6}>
                <EmptyState
                  icon={Package}
                  title={debounced ? 'No matching items' : 'No items yet'}
                  description={
                    debounced
                      ? 'Try a different search term.'
                      : 'Add the equipment you rent out to get started.'
                  }
                  action={
                    !debounced && (
                      <Button onClick={openCreate}>
                        <Plus className="h-4 w-4" />
                        Add your first item
                      </Button>
                    )
                  }
                />
              </TRMessage>
            ) : (
              rows.map((item) => (
                <TR key={item.itemId}>
                  <TD>
                    <p className="font-medium text-text">{item.name}</p>
                    {/* Null-safe: the old table called .toLowerCase() on a
                        possibly-null description and crashed the page. */}
                    {item.description && (
                      <p className="mt-0.5 max-w-md truncate text-[12px] text-text-muted">
                        {item.description}
                      </p>
                    )}
                  </TD>
                  <TD align="right" numeric>
                    {/* Real availability from the stock table. The old UI showed
                        item.qty in both the Available and Total columns, so
                        everything always looked fully in stock. */}
                    <Badge tone={item.availableQty > 0 ? 'success' : 'danger'}>
                      {formatNumber(item.availableQty)}
                    </Badge>
                  </TD>
                  <TD align="right" numeric className="text-text-muted">
                    {formatNumber(item.rentedOutQty)}
                  </TD>
                  <TD align="right" numeric className="text-text-muted">
                    {formatNumber(item.qty)}
                  </TD>
                  <TD align="right" numeric>
                    {item.rent != null ? (
                      <span>
                        {formatMoney(item.rent)}
                        <span className="ml-1 text-[11px] text-text-subtle">
                          /{rentUnitLabel(item.rentFrequency)}
                        </span>
                      </span>
                    ) : (
                      <span className="text-[12px] text-text-subtle">No rate set</span>
                    )}
                  </TD>
                  <TD align="right">
                    <div className="flex justify-end gap-1">
                      <Button variant="ghost" size="icon-sm" onClick={() => openEdit(item)} aria-label={`Edit ${item.name}`}>
                        <Edit2 className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="danger-ghost"
                        size="icon-sm"
                        onClick={() => setDeleting(item)}
                        aria-label={`Delete ${item.name}`}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </TD>
                </TR>
              ))
            )}
          </TBody>
        </Table>
      </TableWrap>

      <ItemFormModal
        open={formOpen}
        item={editing}
        onClose={() => setFormOpen(false)}
        onSaved={() => {
          setFormOpen(false);
          items.reload();
        }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        isLoading={deletePending}
        title={`Delete "${deleting?.name}"?`}
        description="This removes the item along with its stock and rate. It is refused if any units are currently rented out or the item appears on a past rental."
        confirmLabel="Delete item"
      />
    </div>
  );
}

function ItemFormModal({ open, item, onClose, onSaved }) {
  const isEdit = Boolean(item);
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({});

  // Reset whenever the modal opens, so a previous edit does not bleed through.
  const formKey = `${open}-${item?.itemId ?? 'new'}`;
  const [lastKey, setLastKey] = useState(formKey);
  if (formKey !== lastKey) {
    setLastKey(formKey);
    setForm({
      name: item?.name ?? '',
      description: item?.description ?? '',
      qty: item?.qty ?? 0,
      rent: item?.rent ?? '',
      rentFrequency: item?.rentFrequency ?? 'daily',
    });
  }

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (isEdit) {
        await db.items.update(item.itemId, {
          name: form.name,
          description: form.description || null,
          qty: Number(form.qty),
        });
        // Rate lives in its own table; keep it in step when it changed.
        const rent = form.rent === '' ? null : Number(form.rent);
        if (rent != null) {
          const payload = { rent, rentFrequency: form.rentFrequency, itemName: form.name };
          if (item.rent == null) {
            await db.prices.create({ itemId: item.itemId, ...payload });
          } else {
            await db.prices.update(item.itemId, payload);
          }
        }
        toast.success('Item updated.');
      } else {
        await db.items.create({
          name: form.name,
          description: form.description || null,
          qty: Number(form.qty),
          rent: form.rent === '' ? null : Number(form.rent),
          rentFrequency: form.rentFrequency,
        });
        toast.success('Item added.');
      }
      onSaved();
    } catch (err) {
      toast.error(errorMessage(err, 'Could not save this item.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Edit item' : 'Add item'}
      description={isEdit ? undefined : 'Stock is initialised from the quantity you enter.'}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button form="item-form" type="submit" isLoading={saving}>
            {isEdit ? 'Save changes' : 'Add item'}
          </Button>
        </>
      }
    >
      <form id="item-form" onSubmit={handleSubmit} className="space-y-4">
        <Field label="Item name" required>
          {(p) => <Input {...p} value={form.name} onChange={set('name')} required autoFocus />}
        </Field>

        <Field label="Description">
          {(p) => <Textarea {...p} value={form.description} onChange={set('description')} rows={2} />}
        </Field>

        <div className="grid gap-4 sm:grid-cols-3">
          <Field
            label="Total quantity"
            required
            hint={isEdit ? 'Cannot go below the number currently out' : undefined}
          >
            {(p) => (
              <Input {...p} type="number" min="0" value={form.qty} onChange={set('qty')} required />
            )}
          </Field>

          <Field label="Rental rate" hint="Leave blank for no charge">
            {(p) => (
              <Input {...p} type="number" min="0" step="0.01" value={form.rent} onChange={set('rent')} />
            )}
          </Field>

          <Field label="Per">
            {(p) => (
              <Select {...p} value={form.rentFrequency} onChange={set('rentFrequency')}>
                <option value="daily">Day</option>
                <option value="weekly">Week</option>
                <option value="monthly">Month</option>
              </Select>
            )}
          </Field>
        </div>
      </form>
    </Modal>
  );
}
