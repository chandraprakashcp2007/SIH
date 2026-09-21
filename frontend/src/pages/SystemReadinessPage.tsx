import React, { useCallback, useEffect, useState } from 'react';
import { CheckCircle2, RefreshCw, ShieldCheck, TriangleAlert } from 'lucide-react';
import { fetchReadiness } from '../services/api';

export const SystemReadinessPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await fetchReadiness()); } catch (err: any) { setError(err.message || 'Readiness checks unavailable'); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="p-8 text-sm text-text-muted animate-pulse">Checking backend, database, gateway, nodes, PWA, and Copilot…</div>;
  if (error) return <div className="p-8"><div role="alert" className="border border-hazard-critical/40 bg-hazard-critical/10 p-4 text-sm text-hazard-critical">{error}</div><button onClick={load} className="mt-3 text-xs text-accent-info">Retry checks</button></div>;

  return <section className="p-4 sm:p-6 max-w-7xl mx-auto" aria-labelledby="readiness-title">
    <header className="flex flex-wrap items-center justify-between gap-3 mb-5">
      <div><h1 id="readiness-title" className="text-xl font-bold flex items-center gap-2"><ShieldCheck className="text-accent-info"/>System Readiness</h1><p className="text-xs text-text-muted mt-1">Live checks; no hardcoded green indicators.</p></div>
      <button onClick={load} className="px-3 py-2 border border-border-subtle bg-bg-surface text-xs flex items-center gap-2 hover:border-accent-info"><RefreshCw className="w-4 h-4"/>Run checks</button>
    </header>
    <div className={`mb-4 border-l-4 p-4 bg-bg-secondary ${data.overall_status === 'READY' ? 'border-hazard-normal' : 'border-hazard-warning'}`}>
      <div className="text-xs text-text-muted">OVERALL STATE</div><div className="font-mono font-bold">{data.overall_status}</div><div className="text-[11px] text-text-muted">Checked {new Date(data.checked_at).toLocaleString()}</div>
    </div>
    <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-px bg-border-subtle border border-border-subtle">
      {Object.entries(data.checks).map(([name, check]: any) => <article key={name} className="bg-bg-secondary p-4 min-h-28">
        <div className="flex items-center justify-between"><h2 className="uppercase text-xs font-bold tracking-wider">{name.replaceAll('_',' ')}</h2>{check.status === 'READY' ? <CheckCircle2 aria-label="Ready" className="w-4 h-4 text-hazard-normal"/> : <TriangleAlert aria-label={check.status} className="w-4 h-4 text-hazard-warning"/>}</div>
        <div className="mt-2 font-mono text-xs">{check.status}</div><p className="mt-2 text-[11px] text-text-muted break-words">{typeof check.detail === 'object' ? JSON.stringify(check.detail) : check.detail}</p>
      </article>)}
    </div>
  </section>;
};
