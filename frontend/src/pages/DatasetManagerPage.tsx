import React, { useEffect, useState } from 'react';
import { Database } from 'lucide-react';
import { fetchModelRegistry } from '../services/api';

export const DatasetManagerPage: React.FC = () => {
  const role = (() => { try { return JSON.parse(localStorage.getItem('prahari_user') || '{}').role; } catch { return undefined; } })();
  const [registry,setRegistry]=useState<any>({datasets:[],models:[]});
  useEffect(()=>{fetchModelRegistry().then(setRegistry).catch(()=>setRegistry({datasets:[],models:[]}))},[]);
  return <section className="command-page command-reveal p-3 lg:p-5 space-y-5" aria-labelledby="datasets-title">
    <header><h1 id="datasets-title" className="text-xl font-bold flex items-center gap-2"><Database className="text-accent-info"/>Dataset Manager</h1><p className="text-xs text-text-muted mt-1">Persisted manifests, validation evidence, model status and drift abstention.</p></header>
    <div className="grid md:grid-cols-2 gap-4"><div className="border border-border-subtle bg-bg-secondary p-5"><h2 className="font-bold text-sm">Dataset validation</h2><p className="mt-2 text-xs text-text-muted">{registry.datasets.length ? `${registry.datasets.length} persisted manifest(s)` : 'NOT INSTALLED — no dataset is fabricated or inferred from simulation.'}</p></div><div className="border border-border-subtle bg-bg-secondary p-5"><h2 className="font-bold text-sm">Model registry</h2><p className="mt-2 text-xs text-text-muted">{registry.models.length ? `${registry.models.length} registered model(s)` : 'NO VALIDATED MODELS'}</p><p className="mt-2 text-xs text-hazard-watch">Unvalidated or out-of-distribution models ABSTAIN.</p></div></div>
    {role === 'ADMIN' ? <p className="text-xs text-text-muted">Imports require explicit checksum, version and licence metadata.</p> : <p className="text-xs text-hazard-watch">Read-only view — registry mutations require administrator access.</p>}
  </section>;
};
