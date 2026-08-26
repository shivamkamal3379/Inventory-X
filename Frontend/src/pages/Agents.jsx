import { useState } from 'react';
import { Edit2, Plus, Search, Trash2, UserRound } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';
import { Button } from '../components/ui/Button';
import { Field, Input } from '../components/ui/Input';
import { Modal, ConfirmDialog } from '../components/ui/Modal';
import { EmptyState, ErrorState, SkeletonRows } from '../components/ui/Feedback';
import { Table, TableWrap, TBody, TD, TH, THead, TR, TRMessage } from '../components/ui/Table';
import { useToast } from '../components/ToastProvider';
import { useAsync, useDebounced } from '../hooks/useAsync';
import { db } from '../services/db';
import { errorMessage } from '../services/apiClient';

export default function Agents() {
  const [search, setSearch] = useState('');
  const debounced = useDebounced(search, 300);
  const [editing, setEditing] = useState(null);
  const [formOpen, setFormOpen] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [deletePending, setDeletePending] = useState(false);

  const toast = useToast();
  const agents = useAsync(() => db.agents.list({ q: debounced, limit: 200 }), [debounced]);

  const confirmDelete = async () => {
    setDeletePending(true);
    try {
      await db.agents.remove(deleting.agentId);
      toast.success(`${deleting.AgentName} removed.`);
      setDeleting(null);
      agents.reload();
    } catch (err) {
      toast.error(errorMessage(err, 'Could not remove this agent.'));
    } finally {
      setDeletePending(false);
    }
  };

  const rows = agents.data ?? [];

  return (
    <div>
      <PageHeader
        title="Agents"
        description="People who bring in and manage rentals."
        actions={
          <Button
            onClick={() => {
              setEditing(null);
              setFormOpen(true);
            }}
          >
            <Plus className="h-4 w-4" />
            Add agent
          </Button>
        }
      />

      <div className="mb-4 max-w-xs">
        <Input
          leadingIcon={Search}
          placeholder="Search agents…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search agents"
        />
      </div>

      <TableWrap>
        <Table>
          <THead>
            <TR>
              <TH>Name</TH>
              <TH>Mobile</TH>
              <TH>Email</TH>
              <TH align="right">Actions</TH>
            </TR>
          </THead>
          <TBody>
            {agents.loading ? (
              <SkeletonRows rows={5} cols={4} />
            ) : agents.error ? (
              <TRMessage colSpan={4}>
                <ErrorState message={agents.error} onRetry={agents.reload} />
              </TRMessage>
            ) : !rows.length ? (
              <TRMessage colSpan={4}>
                <EmptyState
                  icon={UserRound}
                  title={debounced ? 'No matching agents' : 'No agents yet'}
                  description={
                    debounced
                      ? 'Try a different search term.'
                      : 'Agents are optional — add them to track who placed each rental.'
                  }
                />
              </TRMessage>
            ) : (
              rows.map((a) => (
                <TR key={a.agentId}>
                  <TD className="font-medium text-text">{a.AgentName}</TD>
                  <TD className="text-text-muted">{a.mobile}</TD>
                  <TD className="text-text-muted">{a.email || '—'}</TD>
                  <TD align="right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => {
                          setEditing(a);
                          setFormOpen(true);
                        }}
                        aria-label={`Edit ${a.AgentName}`}
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="danger-ghost"
                        size="icon-sm"
                        onClick={() => setDeleting(a)}
                        aria-label={`Remove ${a.AgentName}`}
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

      <AgentFormModal
        open={formOpen}
        agent={editing}
        onClose={() => setFormOpen(false)}
        onSaved={() => {
          setFormOpen(false);
          agents.reload();
        }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        isLoading={deletePending}
        title={`Remove ${deleting?.AgentName}?`}
        description="Parties linked to this agent keep their records; they simply become unassigned."
        confirmLabel="Remove agent"
      />
    </div>
  );
}

function AgentFormModal({ open, agent, onClose, onSaved }) {
  const isEdit = Boolean(agent);
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({});

  const formKey = `${open}-${agent?.agentId ?? 'new'}`;
  const [lastKey, setLastKey] = useState(formKey);
  if (formKey !== lastKey) {
    setLastKey(formKey);
    setForm({
      AgentName: agent?.AgentName ?? '',
      mobile: agent?.mobile ?? '',
      email: agent?.email ?? '',
      aadhar: agent?.aadhar ?? '',
    });
  }

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        AgentName: form.AgentName,
        mobile: form.mobile,
        email: form.email || null,
        aadhar: form.aadhar || null,
      };
      if (isEdit) {
        await db.agents.update(agent.agentId, payload);
        toast.success('Agent updated.');
      } else {
        await db.agents.create(payload);
        toast.success('Agent added.');
      }
      onSaved();
    } catch (err) {
      toast.error(errorMessage(err, 'Could not save this agent.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Edit agent' : 'Add agent'}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button form="agent-form" type="submit" isLoading={saving}>
            {isEdit ? 'Save changes' : 'Add agent'}
          </Button>
        </>
      }
    >
      <form id="agent-form" onSubmit={handleSubmit} className="space-y-4">
        <Field label="Name" required>
          {(p) => <Input {...p} value={form.AgentName} onChange={set('AgentName')} required autoFocus />}
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Mobile" required>
            {(p) => <Input {...p} value={form.mobile} onChange={set('mobile')} required />}
          </Field>
          <Field label="Email">
            {(p) => <Input {...p} type="email" value={form.email} onChange={set('email')} />}
          </Field>
        </div>
        <Field label="Aadhaar" hint="Optional">
          {(p) => <Input {...p} value={form.aadhar} onChange={set('aadhar')} />}
        </Field>
      </form>
    </Modal>
  );
}
