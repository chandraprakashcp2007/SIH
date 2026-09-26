import React from 'react';
import { Database } from 'lucide-react';

export const DatasetManagerPage: React.FC = () => {
  const role = (() => { try { return JSON.parse(localStorage.getItem('prahari_user') || '{}').role; } catch { return undefined; } })();
  return <section className="p-4 sm:p-6 space-y-5" aria-labelledby="datasets-title">
    <header><h1 id="datasets-title" className="text-xl font-bold flex items-center gap-2"><Database className="text-accent-info"/>Dataset Manager</h1><p className="text-xs text-text-muted mt-1">Persistent manifests will appear here after validated manual imports or verified provider retrievals.</p></header>
    <div className="border border-border-subtle bg-bg-secondary p-5"><h2 className="font-bold text-sm">Installed datasets</h2><p className="mt-2 text-xs text-text-muted">NOT INSTALLED — no dataset is fabricated or inferred from simulation.</p>{role === 'ADMIN' ? <button disabled className="mt-4 px-3 py-2 border border-border-subtle text-xs opacity-60" title="Backend dataset import foundation is not configured">Manual import unavailable</button> : <p className="mt-4 text-xs text-hazard-watch">Read-only view — manual import requires administrator access.</p>}</div>
  </section>;
};
