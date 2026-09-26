import React, { useCallback, useEffect, useState } from 'react';
import { GitBranch, RefreshCw, ShieldAlert } from 'lucide-react';
import { fetchCrossHazardIntelligence, reevaluateCrossHazards } from '../services/api';

type Intelligence = { relationships: any[]; compoundRisks: any[]; consensus: any[] };

const Provenance = ({ value }: { value: string }) => <span className="rounded border border-border-subtle px-2 py-0.5 font-mono text-[10px] text-text-muted">{value}</span>;

export const CrossHazardPage: React.FC = () => {
  const [data, setData] = useState<Intelligence>({ relationships: [], compoundRisks: [], consensus: [] });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const load = useCallback(() => fetchCrossHazardIntelligence().then(setData).catch(e => setError(e.message)), []);
  useEffect(() => { load(); }, [load]);
  const reevaluate = async () => {
    setBusy(true); setError('');
    try {
      const result = await reevaluateCrossHazards();
      setData({ relationships: result.relationships, compoundRisks: result.compound_risks, consensus: result.consensus });
    } catch (e: any) { setError(e.message); } finally { setBusy(false); }
  };
  return <div className="space-y-5 p-4 lg:p-6">
    <header className="flex flex-wrap items-start justify-between gap-3"><div><h1 className="flex items-center gap-2 text-xl font-semibold"><GitBranch className="h-5 w-5" />Cross-Hazard Intelligence</h1><p className="mt-1 max-w-3xl text-xs text-text-muted">Configured reevaluation relationships and transparent compound rules. Relationships are operational triggers, not claims of physical causation.</p></div><button onClick={reevaluate} disabled={busy} className="flex items-center gap-2 rounded bg-accent-info px-3 py-2 text-xs font-semibold text-bg-primary disabled:opacity-50"><RefreshCw className={`h-4 w-4 ${busy ? 'animate-spin' : ''}`} />Reevaluate</button></header>
    {error && <div role="alert" className="rounded border border-red-400/30 bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}
    <section><h2 className="mb-2 text-sm font-semibold">Configured relationships</h2><div className="grid gap-3 lg:grid-cols-2">{data.relationships.map(item => <article key={item.id} className="rounded-lg border border-border-subtle bg-bg-secondary p-4"><div className="flex items-center justify-between gap-2"><strong>{item.source_node_id} → {item.target_node_id}</strong><Provenance value={item.provenance} /></div><div className="mt-2 text-xs">{item.relationship_type} · {item.state} · {item.source_risk_band} → {item.target_risk_band}</div><p className="mt-2 text-xs text-text-muted">{item.explanation}</p><div className="mt-2 text-[10px] text-text-muted">Confidence {item.confidence}% · evidence {item.evidence_refs.length}</div></article>)}</div>{data.relationships.length === 0 && <div className="rounded border border-border-subtle p-5 text-sm text-text-muted">No evaluation has been run.</div>}</section>
    <section><h2 className="mb-2 text-sm font-semibold">Compound risk rules</h2><div className="grid gap-3 lg:grid-cols-3">{data.compoundRisks.map(item => <article key={item.id} className="rounded-lg border border-border-subtle bg-bg-secondary p-4"><div className="flex justify-between gap-2"><strong className="text-sm">{item.rule_id}</strong><Provenance value={item.provenance} /></div><div className="mt-2 text-xs font-semibold text-amber-200">{item.risk_class}</div><p className="mt-2 text-xs text-text-muted">{item.explanation}</p><div className="mt-2 text-[10px] text-text-muted">{item.method} · uncertainty {item.uncertainty}% · v{item.rule_version}</div></article>)}</div></section>
    <section><h2 className="mb-2 text-sm font-semibold">Node-to-node consensus</h2><div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-5">{data.consensus.slice(0, 5).map(item => <article key={item.id} className="rounded-lg border border-border-subtle bg-bg-secondary p-3"><div className="flex items-center gap-2"><ShieldAlert className="h-4 w-4 text-amber-300" /><strong className="text-xs">{item.node_id}</strong></div><div className="mt-2 text-[11px] text-amber-200">{item.state}</div><p className="mt-1 text-[10px] text-text-muted">{item.neighbour_count}/{item.required_neighbours} independently configured neighbours</p></article>)}</div></section>
  </div>;
};
