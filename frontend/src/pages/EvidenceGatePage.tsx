import React, { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { fetchEvidenceGateEvaluations } from '../services/api';

export const EvidenceGatePage: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState('');
  useEffect(() => { fetchEvidenceGateEvaluations().then(setItems).catch(e => setError(e.message)); }, []);
  return <div className="p-4 lg:p-6 space-y-4"><header><h1 className="flex items-center gap-2 text-xl font-semibold"><ShieldCheck className="h-5 w-5" />Evidence Gate</h1><p className="text-xs text-text-muted">Hazard-specific required and optional publication checks. A numeric pass count never overrides a failed mandatory check.</p></header>
    {error && <div role="alert" className="text-red-300">{error}</div>}
    {!error && items.length === 0 && <div className="rounded border border-border-subtle p-6 text-sm text-text-muted">NO EVALUATIONS — predictions remain COLLECTING until evidence is evaluated.</div>}
    {items.map(item => <article key={item.id} className="rounded-lg border border-border-subtle bg-bg-secondary p-4"><div className="flex flex-wrap items-center justify-between gap-2"><div className="font-semibold">{item.hazard} · {item.severity}</div><span className={`rounded px-2 py-1 text-xs ${item.publication_allowed ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-200'}`}>{item.lifecycle}</span></div><div className="mt-3 grid gap-2 sm:grid-cols-3 lg:grid-cols-5">{item.checks.map((check: any) => <div key={check.number} className="rounded border border-border-subtle bg-bg-surface p-2 text-[10px]"><div>{String(check.number).padStart(2, '0')} {check.name}</div><div className="mt-1 text-text-muted">{check.status} · {check.required ? 'REQUIRED' : 'OPTIONAL'}</div></div>)}</div>{item.why_withheld.length > 0 && <div className="mt-3 rounded bg-amber-500/5 p-3 text-xs text-amber-100"><strong>Why withheld:</strong> {item.why_withheld.join('; ')}</div>}<div className="mt-2 text-[10px] text-text-muted">Confidence {item.confidence}% · policy {item.policy_version} · evidence {item.evidence_ids.length}</div></article>)}
  </div>;
};
