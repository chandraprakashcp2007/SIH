import React from 'react';

export type SourceMode = 'REAL' | 'SIMULATION' | 'EXTERNAL_DATA' | 'REPLAY' | 'PLANNED';

export interface ElementStatus {
  domain_id: string;
  display_name: string;
  element: string;
  source_mode: SourceMode;
  hardware_state: string;
  risk_engine_state: string;
  latest_update: string | null;
}

const labels: Record<SourceMode, string> = {
  REAL: 'REAL', SIMULATION: 'SIMULATION', EXTERNAL_DATA: 'EXTERNAL DATA', REPLAY: 'REPLAY', PLANNED: 'PLANNED',
};

const badgeStyles: Record<SourceMode, string> = {
  REAL: 'border-emerald-400/35 bg-emerald-400/10 text-emerald-300',
  SIMULATION: 'border-cyan-400/35 bg-cyan-400/10 text-cyan-300',
  EXTERNAL_DATA: 'border-violet-400/35 bg-violet-400/10 text-violet-300',
  REPLAY: 'border-amber-400/35 bg-amber-400/10 text-amber-300',
  PLANNED: 'border-slate-400/35 bg-slate-400/10 text-slate-300',
};

export const ProvenanceBadge: React.FC<{ mode: SourceMode }> = ({ mode }) => (
  <span className={`rounded border px-1.5 py-0.5 text-[9px] font-bold tracking-wide ${badgeStyles[mode]}`}>
    {labels[mode]}
  </span>
);

export const PanchaBhoothaOverview: React.FC<{ domains: ElementStatus[] }> = ({ domains }) => (
  <section aria-labelledby="pancha-bhootha-title" className="rounded-xl border border-border-subtle bg-bg-secondary/80 p-3">
    <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 id="pancha-bhootha-title" className="text-xs font-bold uppercase tracking-[0.16em] text-text-primary">Pancha Bhootha Fabric</h2>
        <p className="text-[10px] text-text-muted">Hardware and source state only; planned domains carry no fabricated readings.</p>
      </div>
      <div aria-label="Provenance legend" className="flex flex-wrap gap-1">
        {(['REAL', 'SIMULATION', 'EXTERNAL_DATA', 'REPLAY', 'PLANNED'] as SourceMode[]).map(mode => <ProvenanceBadge key={mode} mode={mode} />)}
      </div>
    </div>
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-5">
      {domains.map(domain => (
        <article key={domain.domain_id} className="rounded-lg border border-border-subtle bg-bg-surface p-2.5">
          <div className="flex items-start justify-between gap-2">
            <div><div className="text-xs font-bold text-text-primary">{domain.display_name}</div><div className="text-[9px] tracking-widest text-accent-info">{domain.element}</div></div>
            <ProvenanceBadge mode={domain.source_mode} />
          </div>
          <dl className="mt-2 space-y-1 text-[10px]">
            <div><dt className="inline text-text-muted">Hardware: </dt><dd className="inline text-text-secondary">{domain.hardware_state.replace(/_/g, ' ')}</dd></div>
            <div><dt className="inline text-text-muted">Risk engine: </dt><dd className="inline text-text-secondary">{domain.risk_engine_state.replace(/_/g, ' ')}</dd></div>
            <div><dt className="inline text-text-muted">Latest: </dt><dd className="inline text-text-secondary">{domain.latest_update ? new Date(domain.latest_update).toLocaleString() : 'No live physical telemetry'}</dd></div>
          </dl>
        </article>
      ))}
    </div>
  </section>
);
