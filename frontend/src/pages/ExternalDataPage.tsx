import React, { useCallback, useEffect, useState } from 'react';
import { CloudDownload, RefreshCw } from 'lucide-react';
import { fetchExternalObservations, fetchExternalProviderStatus } from '../services/api';

export const ExternalDataPage: React.FC = () => {
  const [providers, setProviders] = useState<any[]>([]);
  const [observations, setObservations] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [providerData, observationData] = await Promise.all([fetchExternalProviderStatus(), fetchExternalObservations()]);
      setProviders(providerData); setObservations(observationData);
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);
  return <section className="p-4 sm:p-6 space-y-5" aria-labelledby="external-title">
    <header><h1 id="external-title" className="text-xl font-bold flex items-center gap-2"><CloudDownload className="text-accent-info"/>External Data</h1><p className="text-xs text-text-muted mt-1">Provider states and observations are shown from verified persisted evidence only.</p></header>
    {error && <div role="alert" className="border border-hazard-critical/40 p-3 text-hazard-critical text-xs">{error} <button onClick={() => void load()} className="ml-3 text-accent-info">Retry</button></div>}
    {loading ? <p className="text-sm text-text-muted animate-pulse">Loading provider registry…</p> : <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-3">{providers.map((p) => <article key={p.provider} className="bg-bg-secondary border border-border-subtle p-4 min-w-0"><div className="flex justify-between gap-2"><h2 className="font-bold text-sm">{p.display_name}</h2><span className="text-[10px] font-bold text-hazard-watch">{p.state}</span></div><p className="text-xs text-text-muted mt-2">{p.capabilities.join(' • ')}</p><dl className="mt-3 text-[11px] text-text-secondary"><dt>Last successful retrieval</dt><dd>{p.last_success_at || 'No verified retrieval'}</dd><dt className="mt-2">Access note</dt><dd>{p.access_note || 'NOT CONFIGURED'}</dd>{p.last_error && <><dt className="mt-2">Error</dt><dd className="text-hazard-critical">{p.last_error}</dd></>}</dl></article>)}</div>}
    <div><h2 className="font-bold text-sm mb-2">Recent observations</h2>{observations.length === 0 ? <p className="border border-border-subtle bg-bg-secondary p-4 text-xs text-text-muted">NO OBSERVATION</p> : <div className="space-y-2">{observations.map((o) => <div key={o.id} className="border border-border-subtle p-3 text-xs"><span className="font-bold">{o.provider}</span> · {o.parameter} · <span className="text-accent-info">EXTERNAL DATA</span></div>)}</div>}</div>
  </section>;
};
