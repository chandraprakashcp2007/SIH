import React, { useEffect, useState } from 'react';
import { Fingerprint, KeyRound, Shield, ShieldCheck } from 'lucide-react';
import { fetchSecurityCentre } from '../services/api';
import { EmptyState, SectionHeader, StatusBadge } from '../components/ui/CommandPrimitives';

export const SecurityCentrePage: React.FC = () => {
  const [data, setData] = useState<any>(); const [error, setError] = useState(''); const [loading, setLoading] = useState(true);
  useEffect(() => { fetchSecurityCentre().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false)); }, []);
  const cards = [
    { label: 'Signed telemetry', value: data?.status.signed_telemetry || 'UNVERIFIED', icon: KeyRound },
    { label: 'Replay protection', value: data?.status.replay_protection || 'UNVERIFIED', icon: Fingerprint },
    { label: 'Audit chain', value: data?.chain.valid === true ? 'VALID' : data?.chain.valid === false ? 'BLOCKED' : 'UNVERIFIED', icon: ShieldCheck },
  ];
  return <div className="command-page command-reveal space-y-4 p-3 lg:p-5">
    <SectionHeader eyebrow="Assurance / zero-trust telemetry" title="Security Event Centre" description="Signed telemetry readiness, nonce replay defense, device trust, and tamper-evident audit state." />
    {error && <div role="alert" className="command-error-state">{error}</div>}
    <section className="grid gap-3 sm:grid-cols-3">{cards.map(({ label, value, icon: Icon }) => <article key={label} className="command-panel p-4"><div className="flex items-center justify-between gap-2"><span className="security-icon"><Icon /></span><StatusBadge status={value} /></div><div className="mt-4 text-xs text-text-muted">{label}</div><strong className="mt-1 block text-lg text-text-primary">{value.replace(/_/g,' ')}</strong></article>)}</section>
    <section className="command-panel p-4"><h2 className="flex items-center gap-2 text-sm font-semibold"><Shield className="h-4 w-4 text-accent-info" />Security events</h2>{loading ? <EmptyState compact state="LOADING" title="Loading security events" /> : error ? <EmptyState compact state="UNAVAILABLE" title="Security events unavailable" detail="The audit queue could not be verified." /> : data.events.length === 0 ? <EmptyState compact state="CLEAR AUDIT QUEUE" title="No security events recorded" detail="The retained event chain contains no security incidents." /> : <div className="mt-3 space-y-2">{data.events.map((event: any) => <article key={event.id} className="rounded-lg border border-border-subtle bg-bg-surface p-3 text-xs"><div className="flex justify-between gap-2"><strong>{event.event_type}</strong><StatusBadge status={event.severity} /></div><div className="mt-2 truncate font-mono text-[10px] text-text-muted">{event.event_hash}</div></article>)}</div>}</section>
    <p className="rounded-lg border border-border-subtle bg-bg-secondary/50 p-3 text-xs text-text-muted">Device secrets are read from server environment configuration and are never returned to this client.</p>
  </div>;
};
