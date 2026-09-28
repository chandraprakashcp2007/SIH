import React, { useEffect, useState } from 'react';
import { ArrowRight, CheckCircle2, Fingerprint, ScanSearch, ShieldCheck, Waypoints } from 'lucide-react';
import { fetchEvidenceGateEvaluations } from '../services/api';
import { EmptyState, SectionHeader, SourceBadge, StatusBadge } from '../components/ui/CommandPrimitives';

const stages = [
  { label: 'RAW EVIDENCE', icon: ScanSearch }, { label: 'VALIDATION', icon: CheckCircle2 },
  { label: 'TRUST', icon: Fingerprint }, { label: 'CORROBORATION', icon: Waypoints }, { label: 'RISK DECISION', icon: ShieldCheck },
];
export const EvidenceGatePage: React.FC = () => {
  const [items, setItems] = useState<any[]>([]); const [error, setError] = useState('');
  useEffect(() => { fetchEvidenceGateEvaluations().then(setItems).catch(e => setError(e.message)); }, []);
  return <div className="command-page command-reveal space-y-4 p-3 lg:p-5">
    <SectionHeader eyebrow="Provenance assurance" title="Evidence Gate" description="PRAHARI never promotes a single unvalidated sensor spike into an operational risk decision." />
    <section className="command-panel evidence-pipeline p-3 md:p-5" aria-label="Evidence decision pipeline">{stages.map(({ label, icon: Icon }, index) => <React.Fragment key={label}><div className="evidence-stage"><span><Icon /></span><b>{label}</b><small>{index < 4 ? 'Verified transition' : 'Policy controlled'}</small></div>{index < stages.length - 1 && <ArrowRight className="evidence-arrow" aria-hidden="true" />}</React.Fragment>)}</section>
    {error && <div role="alert" className="command-error-state">{error}</div>}
    {!error && items.length === 0 && <EmptyState state="COLLECTING" title="NO EVALUATIONS" detail="Predictions remain COLLECTING until evidence is evaluated." />}
    <div className="grid gap-3">{items.map(item => <article key={item.id} className="command-panel p-4"><div className="flex flex-wrap items-center justify-between gap-2"><div><div className="command-eyebrow">{item.hazard}</div><h2 className="mt-1 font-semibold">{item.severity} evidence assessment</h2></div><div className="flex gap-2"><SourceBadge source={item.provenance || 'UNVERIFIED'} /><StatusBadge status={item.publication_allowed ? 'OPERATIONAL' : 'BLOCKED'} /></div></div><div className="mt-4 grid gap-2 sm:grid-cols-3 lg:grid-cols-5">{item.checks.map((check: any) => <div key={check.number} className="evidence-check"><span>{String(check.number).padStart(2,'0')}</span><b>{check.name}</b><small>{check.status} · {check.required ? 'REQUIRED' : 'OPTIONAL'}</small></div>)}</div>{item.why_withheld.length > 0 && <div className="mt-3 rounded-lg border border-amber-400/20 bg-amber-400/5 p-3 text-xs text-amber-100"><strong>Why withheld:</strong> {item.why_withheld.join('; ')}</div>}<div className="mt-3 text-[10px] text-text-muted">Confidence {item.confidence}% · policy {item.policy_version} · evidence {item.evidence_ids.length}</div></article>)}</div>
  </div>;
};
