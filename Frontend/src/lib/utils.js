import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const INR = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
});

/** Currency, null-safe. `party.balance.toFixed()` used to crash on a null balance. */
export function formatMoney(value) {
  const n = Number(value);
  return INR.format(Number.isFinite(n) ? n : 0);
}

export function formatNumber(value) {
  const n = Number(value);
  return new Intl.NumberFormat('en-IN').format(Number.isFinite(n) ? n : 0);
}

const DATE_FMT = new Intl.DateTimeFormat('en-IN', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
});

const DATETIME_FMT = new Intl.DateTimeFormat('en-IN', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

export function formatDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '—' : DATE_FMT.format(d);
}

export function formatDateTime(value) {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '—' : DATETIME_FMT.format(d);
}

export function relativeTime(value) {
  if (!value) return '';
  const then = new Date(value).getTime();
  if (Number.isNaN(then)) return '';

  const seconds = Math.round((Date.now() - then) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 30) return `${days}d ago`;
  return formatDate(value);
}

/** For <input type="date">, which needs exactly yyyy-mm-dd. */
export function toDateInput(value) {
  const d = value ? new Date(value) : new Date();
  if (Number.isNaN(d.getTime())) return '';
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

/** Whether an expected-return date has passed. */
export function isOverdue(expected, status) {
  if (!expected || !['open', 'partial'].includes(status)) return false;
  return new Date(expected).getTime() < Date.now();
}

/**
 * Short label for a rental period, e.g. "day" for daily.
 *
 * Not a string trim: stripping "ly" from "daily" yields "dai", which is what
 * used to be printed on invoices.
 */
const RENT_UNIT = {
  daily: 'day',
  weekly: 'week',
  monthly: 'month',
};

export function rentUnitLabel(frequency) {
  return RENT_UNIT[frequency] ?? RENT_UNIT.daily;
}
