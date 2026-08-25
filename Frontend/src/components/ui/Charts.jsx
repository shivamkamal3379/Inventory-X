import { useMemo, useState } from 'react';
import { cn, formatDate, formatMoney, formatNumber } from '../../lib/utils';

/* ==========================================================================
   Charts

   Inline SVG, no charting library. Every chart here is SINGLE-SERIES, so it
   carries no legend — the card title names the measure. Colour is the brand
   hue, validated for >= 3:1 contrast against both the light and dark chart
   surfaces, and marks carry a 2px surface gap so adjacent bars stay separable.
   Each chart also exposes its numbers as a table for screen readers, so meaning
   is never colour-alone.
   ========================================================================== */

/** Rounded-top bar anchored to the baseline (4px radius, clamped on short bars). */
function barPath(x, y, w, h, r = 4) {
  const radius = Math.max(0, Math.min(r, w / 2, h));
  if (h <= 0) return '';
  return [
    `M${x},${y + h}`,
    `V${y + radius}`,
    `Q${x},${y} ${x + radius},${y}`,
    `H${x + w - radius}`,
    `Q${x + w},${y} ${x + w},${y + radius}`,
    `V${y + h}`,
    'Z',
  ].join(' ');
}

/**
 * Daily revenue. Bars rather than a line because the series is discrete and
 * sparse — returns happen on some days and not others, and a line would imply
 * a continuous value between them that does not exist.
 */
export function RevenueTrend({ data = [], height = 168 }) {
  const [hover, setHover] = useState(null);

  const { bars, max, total } = useMemo(() => {
    const maxValue = Math.max(...data.map((d) => d.revenue), 0);
    return {
      bars: data,
      max: maxValue,
      total: data.reduce((sum, d) => sum + (d.revenue || 0), 0),
    };
  }, [data]);

  if (!data.length) {
    return <div className="h-[168px] rounded-lg bg-surface-sunken" aria-hidden="true" />;
  }

  const GAP = 2;
  const width = 640;
  const slot = width / data.length;
  const barW = Math.max(1, slot - GAP);
  const plotH = height - 22; // leave room for the x labels

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        style={{ height }}
        preserveAspectRatio="none"
        role="img"
        aria-label={`Daily revenue over the last ${data.length} days, totalling ${formatMoney(total)}`}
      >
        {/* Baseline only — a full grid would compete with such thin marks. */}
        <line
          x1="0" y1={plotH} x2={width} y2={plotH}
          className="stroke-line" strokeWidth="1" vectorEffect="non-scaling-stroke"
        />

        {bars.map((d, i) => {
          const h = max > 0 ? (d.revenue / max) * (plotH - 6) : 0;
          const x = i * slot + GAP / 2;
          const y = plotH - h;
          const isHovered = hover?.index === i;

          return (
            <g key={d.date}>
              {/* Hit target spans the full column height, so a near-zero bar is
                  still hoverable. */}
              <rect
                x={i * slot} y={0} width={slot} height={plotH}
                fill="transparent"
                onMouseEnter={() => setHover({ index: i, ...d })}
                onMouseLeave={() => setHover(null)}
              />
              {h > 0 && (
                <path
                  d={barPath(x, y, barW, h)}
                  className={cn('fill-brand transition-opacity', hover && !isHovered && 'opacity-40')}
                  pointerEvents="none"
                />
              )}
              {isHovered && (
                <line
                  x1={i * slot + slot / 2} y1={0} x2={i * slot + slot / 2} y2={plotH}
                  className="stroke-brand" strokeWidth="1" strokeDasharray="3 3"
                  vectorEffect="non-scaling-stroke" pointerEvents="none"
                />
              )}
            </g>
          );
        })}
      </svg>

      {/* Only the endpoints are labelled — a date under every bar would be an
          unreadable smear at 30 days. */}
      <div className="flex justify-between px-0.5 text-[11px] text-text-subtle">
        <span>{formatDate(data[0]?.date)}</span>
        <span>{formatDate(data[data.length - 1]?.date)}</span>
      </div>

      {hover && (
        <div
          className="pointer-events-none absolute -top-1 left-1/2 -translate-x-1/2 rounded-md border border-line bg-surface-raised px-2.5 py-1.5 shadow-md"
          role="status"
        >
          <p className="text-[11px] text-text-muted">{formatDate(hover.date)}</p>
          <p className="tabular text-[13px] font-semibold text-text">{formatMoney(hover.revenue)}</p>
        </div>
      )}

      <table className="sr-only">
        <caption>Daily revenue</caption>
        <thead>
          <tr><th>Date</th><th>Revenue</th></tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.date}><td>{d.date}</td><td>{d.revenue}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * A single ratio against a limit. A meter, not a two-slice pie.
 * The track uses the same hue at low opacity so the fill reads as a portion
 * of a whole rather than as a second category.
 */
export function Meter({ value = 0, label, caption }) {
  const pct = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-[13px] text-text-muted">{label}</span>
        <span className="tabular text-[13px] font-semibold text-text">{pct}%</span>
      </div>
      <div
        className="mt-2 h-2 w-full overflow-hidden rounded-full bg-brand/12"
        role="meter"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label}
      >
        <div
          className="h-full rounded-full bg-brand transition-[width] duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
      {caption && <p className="mt-1.5 text-[12px] text-text-subtle">{caption}</p>}
    </div>
  );
}

/** Ranked magnitude by category — horizontal bars, one hue, value labelled directly. */
export function RankedBars({ data = [], valueKey = 'unitsRented', labelKey = 'name', formatValue = formatNumber }) {
  const max = Math.max(...data.map((d) => Number(d[valueKey]) || 0), 1);

  if (!data.length) return null;

  return (
    <ul className="space-y-3">
      {data.map((d, i) => {
        const value = Number(d[valueKey]) || 0;
        return (
          <li key={d.itemId ?? i}>
            <div className="flex items-baseline justify-between gap-3">
              <span className="truncate text-[13px] text-text">{d[labelKey]}</span>
              <span className="tabular shrink-0 text-[13px] font-medium text-text-muted">
                {formatValue(value)}
              </span>
            </div>
            <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-surface-sunken">
              <div
                className="h-full rounded-full bg-brand"
                style={{ width: `${(value / max) * 100}%` }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}

/** Compact KPI tile: a value, an optional delta, and a caption. */
export function StatTile({ icon: Icon, label, value, caption, tone = 'neutral' }) {
  const toneCls = {
    neutral: 'text-text',
    success: 'text-success',
    warning: 'text-warning',
    danger: 'text-danger',
  }[tone];

  return (
    <div className="rounded-xl border border-line bg-surface p-4 shadow-xs">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[12px] font-medium text-text-muted">{label}</p>
        {Icon && <Icon className="h-4 w-4 text-text-subtle" aria-hidden="true" />}
      </div>
      <p className={cn('tabular mt-2 text-2xl font-semibold tracking-tight', toneCls)}>{value}</p>
      {caption && <p className="mt-1 text-[12px] text-text-subtle">{caption}</p>}
    </div>
  );
}
