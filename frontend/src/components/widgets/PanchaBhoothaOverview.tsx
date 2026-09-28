import React from 'react';
import { CloudRain, Droplets, Flame, Mountain, Wind } from 'lucide-react';
import { SourceBadge } from '../ui/CommandPrimitives';

export type SourceMode = 'REAL' | 'SIMULATION' | 'EXTERNAL_DATA' | 'REPLAY' | 'PLANNED';
export interface ElementStatus { domain_id: string; display_name: string; element: string; source_mode: SourceMode; hardware_state: string; risk_engine_state: string; latest_update: string | null; }
const configs: Record<string, { label: string; icon: React.ElementType; tone: string; description: string }> = {
  JALA: { label: 'जल (JALA)', icon: Droplets, tone: 'jala', description: 'Water intelligence' },
  AGNI: { label: 'अग्नि (AGNI)', icon: Flame, tone: 'agni', description: 'Fire intelligence' },
  BHUMI: { label: 'भूमि (BHUMI)', icon: Mountain, tone: 'bhumi', description: 'Terrain intelligence' },
  VAYU: { label: 'वायु (VAYU)', icon: Wind, tone: 'vayu', description: 'Air intelligence' },
  AKASHA: { label: 'आकाश (AKASHA)', icon: CloudRain, tone: 'akasha', description: 'Weather intelligence' },
};
export const ProvenanceBadge: React.FC<{ mode: SourceMode }> = ({ mode }) => <SourceBadge source={mode} />;

export const PanchaBhoothaOverview: React.FC<{ domains: ElementStatus[] }> = ({ domains }) => <section aria-labelledby="pancha-bhootha-title" className="command-panel p-3 md:p-4">
  <div className="mb-3 flex flex-wrap items-end justify-between gap-3"><div><div className="command-eyebrow">Environmental intelligence fabric</div><h2 id="pancha-bhootha-title" className="mt-1 text-sm font-bold tracking-wide text-text-primary">पंचभूत · Pancha Bhootha Fabric</h2><p className="mt-1 text-[10px] text-text-muted">Five evidence-aware domains. Every signal retains its source and operational state.</p></div><div aria-label="Provenance legend" className="flex flex-wrap gap-1">{(['REAL','SIMULATION','EXTERNAL_DATA','REPLAY','PLANNED'] as SourceMode[]).map(mode => <ProvenanceBadge key={mode} mode={mode} />)}</div></div>
  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-5">{domains.map(domain => { const config = configs[domain.display_name] || { label: domain.display_name, icon: Droplets, tone: 'vayu', description: domain.element }; const Icon = config.icon; return <article key={domain.domain_id} className="domain-status-card" style={{ '--domain-accent': `var(--${config.tone})` } as React.CSSProperties}>
    <div className="flex items-start justify-between gap-2"><div className="domain-status-icon"><Icon /></div><ProvenanceBadge mode={domain.source_mode} /></div>
    <div className="mt-3 text-xs font-bold text-text-primary">{config.label}</div><div className="mt-1 flex items-center justify-between gap-2"><span className="font-mono text-[9px] tracking-widest text-[color:var(--domain-accent)]">{domain.domain_id}</span><span className="text-[9px] text-text-muted">{config.description}</span></div>
    <div className="domain-signal"><span /><span /><span /><span /><span /></div>
    <dl className="mt-2 space-y-1 text-[9px]"><div className="flex justify-between gap-2"><dt className="text-text-muted">Hardware</dt><dd className="truncate text-text-secondary">{domain.hardware_state.replace(/_/g,' ')}</dd></div><div className="flex justify-between gap-2"><dt className="text-text-muted">Risk engine</dt><dd className="truncate text-text-secondary">{domain.risk_engine_state.replace(/_/g,' ')}</dd></div><div className="flex justify-between gap-2"><dt className="text-text-muted">Latest</dt><dd className="truncate text-text-secondary">{domain.latest_update ? new Date(domain.latest_update).toLocaleString() : 'No live physical telemetry'}</dd></div></dl>
  </article>; })}</div>
</section>;
