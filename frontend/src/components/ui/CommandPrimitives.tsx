import React from 'react';
import { AlertTriangle, ArrowUpRight, Database, Radio, ShieldCheck } from 'lucide-react';
import clsx from 'clsx';

type ElementProps = React.HTMLAttributes<HTMLElement> & { children: React.ReactNode };

export function GlassPanel({ children, className, ...props }: ElementProps) {
  return <section className={clsx('command-panel', className)} {...props}>{children}</section>;
}

export function SectionHeader({ eyebrow, title, description, action, level = 2, className }: {
  eyebrow?: string; title: string; description?: string; action?: React.ReactNode;
  level?: 1 | 2 | 3; className?: string;
}) {
  const Heading = `h${level}` as 'h1' | 'h2' | 'h3';
  return <div className={clsx('command-section-header', className)}><div className="min-w-0">
    {eyebrow && <div className="command-eyebrow">{eyebrow}</div>}
    <Heading className="command-section-title">{title}</Heading>
    {description && <p className="command-section-description">{description}</p>}
  </div>{action && <div className="command-section-action">{action}</div>}</div>;
}

const statusTone: Record<string, string> = {
  OPERATIONAL: 'is-success', AVAILABLE: 'is-success', NORMAL: 'is-success', REAL: 'is-real',
  DEGRADED: 'is-warning', WATCH: 'is-warning', WARNING: 'is-warning', CRITICAL: 'is-critical',
  BLOCKED: 'is-critical', ERROR: 'is-critical', NOT_CONFIGURED: 'is-muted', UNVERIFIED: 'is-muted',
  METADATA_ONLY: 'is-muted', PLANNED: 'is-planned', OFFLINE: 'is-muted', NO_DATA: 'is-muted',
};
const displayState = (value: string) => value.replace(/_/g, ' ');

export function StatusBadge({ status, className }: { status: string; className?: string }) {
  const label = displayState(status || 'UNVERIFIED');
  return <span className={clsx('command-badge', statusTone[status] || 'is-muted', className)} aria-label={`Status: ${label}`}><span className="command-status-dot" />{label}</span>;
}

const sourceTone: Record<string, string> = { REAL: 'is-real', SIMULATION: 'is-simulation', REPLAY: 'is-replay', MODEL: 'is-model', EXTERNAL_DATA: 'is-external', PLANNED: 'is-planned' };
export function SourceBadge({ source, className }: { source?: string | null; className?: string }) {
  const key = source || 'UNVERIFIED'; const label = displayState(key);
  return <span className={clsx('command-badge command-source', sourceTone[key] || 'is-muted', className)} aria-label={`Source: ${label}`}><Database aria-hidden="true" />{label}</span>;
}

export function MetricCard({ label, value, detail, icon, tone = 'mint', trend }: {
  label: string; value: React.ReactNode; detail?: React.ReactNode; icon?: React.ReactNode;
  tone?: 'mint' | 'cyan' | 'amber' | 'red' | 'violet'; trend?: React.ReactNode;
}) {
  return <article className={clsx('command-metric', `tone-${tone}`)}><div className="command-metric-top"><span>{label}</span>{icon || <Radio aria-hidden="true" />}</div><div className="command-metric-value">{value}</div>{(detail || trend) && <div className="command-metric-detail"><span>{detail}</span>{trend && <span className="command-metric-trend">{trend}</span>}</div>}</article>;
}

export function EmptyState({ title, detail, actionLabel, onAction, state = 'NO DATA', compact = false }: {
  title: string; detail?: string; actionLabel?: string; onAction?: () => void; state?: string; compact?: boolean;
}) {
  return <div className={clsx('command-empty', compact && 'is-compact')} role="status"><div className="command-empty-icon">{state.includes('ERROR') ? <AlertTriangle /> : <ShieldCheck />}</div><div className="command-eyebrow">{state}</div><h3>{title}</h3>{detail && <p>{detail}</p>}{actionLabel && onAction && <button type="button" className="command-button is-secondary" onClick={onAction}>{actionLabel}<ArrowUpRight /></button>}</div>;
}
