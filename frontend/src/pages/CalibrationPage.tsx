import React, { useCallback, useEffect, useState } from 'react';
import { Gauge, RefreshCw, Save } from 'lucide-react';
import { fetchCalibration, saveCalibration } from '../services/api';

export const CalibrationPage: React.FC = () => {
  const role = (() => { try { return JSON.parse(localStorage.getItem('prahari_user') || '{}').role; } catch { return undefined; } })();
  const canEdit = role === 'ADMIN';
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const load = useCallback(() => fetchCalibration().then(setData).catch((e) => setError(e.message)), []);
  useEffect(() => { load(); }, [load]);
  const update = (node: string, key: string, value: string) => setData((current: any) => ({...current, nodes: {...current.nodes, [node]: {...current.nodes[node], [key]: Number(value)}}}));
  const save = async (node: string) => { setSaving(node); setError(null); try { await saveCalibration(node, data.nodes[node]); } catch (e: any) { setError(e.message); } finally { setSaving(null); } };
  if (!data && !error) return <div className="p-8 text-sm text-text-muted animate-pulse">Loading sensor calibration registry…</div>;
  if (!data) return <div className="p-8"><div role="alert" className="text-hazard-critical">{error}</div><button onClick={load} className="mt-3 text-accent-info text-xs">Retry</button></div>;
  return <section className="p-4 sm:p-6 max-w-6xl mx-auto" aria-labelledby="calibration-title">
    <header className="mb-5"><h1 id="calibration-title" className="text-xl font-bold flex items-center gap-2"><Gauge className="text-accent-info"/>Sensor Calibration</h1><p className="text-xs text-text-muted mt-1">Persisted offsets and baselines. Changes require administrator access.</p>{!canEdit && <p role="status" className="mt-2 text-xs text-hazard-watch">Read-only view — administrator access is required to save calibration.</p>}</header>
    {error && <div role="alert" className="mb-4 border border-hazard-critical/40 bg-hazard-critical/10 p-3 text-xs text-hazard-critical">{error}</div>}
    <div className="grid lg:grid-cols-3 gap-4">{Object.entries(data.nodes).map(([node, values]: any) => <article key={node} className="border border-border-subtle bg-bg-secondary">
      <div className="px-4 py-3 border-b border-border-subtle font-mono font-bold text-accent-info">{node}</div>
      <div className="p-4 space-y-3">{Object.entries(values).map(([key, value]: any) => <label key={key} className="block text-[11px] text-text-secondary"><span className="block mb-1">{key.replaceAll('_',' ')}</span><input aria-label={`${node} ${key}`} type="number" step="any" value={value} disabled={!canEdit} onChange={(e) => update(node,key,e.target.value)} className="w-full bg-bg-surface border border-border-subtle px-3 py-2 font-mono text-xs focus:outline-none focus:border-accent-info disabled:opacity-60"/></label>)}</div>
      {canEdit && <button onClick={() => save(node)} disabled={saving === node} className="m-4 mt-0 px-3 py-2 bg-accent-info text-bg-primary text-xs font-bold flex items-center gap-2 disabled:opacity-50">{saving === node ? <RefreshCw className="w-4 h-4 animate-spin"/> : <Save className="w-4 h-4"/>}Save calibration</button>}
    </article>)}</div>
  </section>;
};
