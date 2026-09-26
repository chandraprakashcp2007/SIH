import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, Clock3, Database, Radio, ShieldQuestion } from 'lucide-react';
import { LiveMap } from '../components/map/LiveMap';
import { fetchGeoDomain } from '../services/api';

export type DomainName = 'JALA' | 'AGNI' | 'BHUMI' | 'VAYU' | 'AKASHA';

const CONFIG: Record<DomainName, { title: string; subtitle: string; nodeId: string; metrics: string[]; unavailable: string }> = {
  JALA: { title: 'JALA River & Flood Intelligence', subtitle: 'Water level, rainfall evidence and river-risk operations', nodeId: 'JALA-01', metrics: ['water_level_cm', 'water_rise_rate_cm_min', 'rain_intensity'], unavailable: 'Authoritative river geometry, watershed and hydrodynamic travel model are not configured.' },
  AGNI: { title: 'AGNI Fire Intelligence', subtitle: 'Heat, flame and qualitative smoke/combustion evidence', nodeId: 'AGNI-02', metrics: ['temperature_c', 'smoke_index', 'gas_index', 'flame_detected'], unavailable: 'NASA FIRMS and validated fire-spread modelling are not configured.' },
  BHUMI: { title: 'BHUMI Terrain & Landslide Intelligence', subtitle: 'Soil moisture, tilt, vibration and rainfall context', nodeId: 'BHUMI-03', metrics: ['soil_moisture_upper_pct', 'tilt_delta_deg', 'vibration_rms', 'rain_context'], unavailable: 'A real DEM and authoritative landslide susceptibility dataset are not configured.' },
  VAYU: { title: 'VAYU Air & Smoke Intelligence', subtitle: 'Gas and smoke evidence with environmental context', nodeId: 'VAYU-04', metrics: ['pm2_5', 'pm10', 'co_ppm', 'voc_index'], unavailable: 'PM2.5 and PM10 are simulation-only until calibrated particulate hardware or a trusted provider is configured.' },
  AKASHA: { title: 'AKASHA Weather Intelligence', subtitle: 'Rain, pressure and atmospheric risk evidence', nodeId: 'AKASHA-05', metrics: ['rain_intensity', 'pressure_hpa', 'wind_speed_kmh', 'humidity_pct'], unavailable: 'Authoritative weather warnings, radar and satellite layers are not configured.' },
};

const riskColor: Record<string, string> = {
  SAFE: 'text-emerald-400', WATCH: 'text-yellow-400', WARNING: 'text-orange-400', CRITICAL: 'text-red-400', NO_DATA: 'text-slate-400',
};

export const DomainIntelligencePage: React.FC<{ domain: DomainName }> = ({ domain }) => {
  const config = CONFIG[domain];
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    fetchGeoDomain(domain).then((value) => active && setData(value)).catch((reason) => active && setError(reason.message || 'Map data unavailable'));
    return () => { active = false; };
  }, [domain]);

  const feature = data?.features?.[0];
  const props = feature?.properties || {};
  const node = useMemo(() => feature ? [{
    id: props.node_id, name: props.name, node_type: domain,
    latitude: feature.geometry.coordinates[1], longitude: feature.geometry.coordinates[0],
    status: props.risk_band === 'NO_DATA' ? 'OFFLINE' : 'ONLINE', location_name: props.location_name,
    latest_risk: { risk_score: props.risk_score ?? 0, risk_band: props.risk_band === 'SAFE' ? 'NORMAL' : props.risk_band, confidence: props.confidence ?? 0 },
    latest_metrics: props.metrics,
  }] : [], [domain, feature, props]);

  if (error) return <div role="alert" className="p-6"><div className="rounded-lg border border-red-500/30 bg-red-500/10 p-5 text-red-200"><AlertTriangle className="mb-2 h-5 w-5" />{error}</div></div>;
  if (!data) return <div role="status" className="p-8 text-sm text-text-muted">Loading {domain} geospatial evidence…</div>;

  return <div className="p-4 lg:p-6 space-y-4" data-testid={`domain-map-${domain.toLowerCase()}`}>
    <header className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
      <div><div className="text-[10px] tracking-[0.22em] text-text-muted">LIVE OPERATIONS / {domain}</div><h1 className="mt-1 text-2xl font-semibold">{config.title}</h1><p className="text-sm text-text-secondary">{config.subtitle}</p></div>
      <div className="flex gap-2 text-xs"><span className="rounded border border-border-subtle px-2 py-1">Source: {props.provenance}</span><span className="rounded border border-border-subtle px-2 py-1"><Clock3 className="mr-1 inline h-3 w-3" />Freshness: {props.freshness_seconds == null ? 'NO DATA' : `${props.freshness_seconds}s`}</span></div>
    </header>

    <section className="grid gap-3 lg:grid-cols-4">
      <div className="rounded-lg border border-border-subtle bg-bg-secondary p-4"><div className="text-xs text-text-muted">BACKEND RISK STATE</div><div className={`mt-2 text-xl font-bold ${riskColor[props.risk_band] || riskColor.NO_DATA}`}>{props.risk_band}</div><div className="text-xs text-text-muted">{props.risk_score == null ? 'Insufficient evidence' : `Score ${props.risk_score} · confidence ${props.confidence}%`}</div></div>
      <div className="rounded-lg border border-border-subtle bg-bg-secondary p-4 lg:col-span-2"><div className="mb-2 text-xs text-text-muted">OBSERVED VALUES</div><div className="grid grid-cols-2 gap-2">{config.metrics.map(metric => <div key={metric} className="rounded bg-bg-surface p-2"><div className="text-[10px] text-text-muted">{metric}</div><div className="font-mono text-sm">{props.metrics?.[metric] ?? 'UNAVAILABLE'}</div></div>)}</div></div>
      <div className="rounded-lg border border-border-subtle bg-bg-secondary p-4"><div className="text-xs text-text-muted">EVIDENCE STATUS</div><div className="mt-2 flex items-center gap-2 text-sm"><Radio className="h-4 w-4" />{props.provenance}</div><div className="mt-1 text-xs text-text-muted">Observed {props.observed_at ? new Date(props.observed_at).toLocaleString() : 'NO LIVE DATA'}</div></div>
    </section>

    <section className="grid min-h-[520px] gap-4 xl:grid-cols-[1fr_280px]">
      <div className="overflow-hidden rounded-lg border border-border-subtle bg-bg-secondary"><LiveMap nodes={node} selectedNodeId={config.nodeId} /></div>
      <aside className="space-y-3 overflow-auto rounded-lg border border-border-subtle bg-bg-secondary p-3"><h2 className="flex items-center gap-2 text-sm font-semibold"><Database className="h-4 w-4" />Operational layers</h2>{data.layers.map((layer: any) => <div key={layer.id} className="rounded border border-border-subtle bg-bg-surface p-2"><div className="flex items-center justify-between gap-2"><span className="text-xs">{layer.id.replaceAll('_', ' ')}</span>{layer.status === 'AVAILABLE' ? <CheckCircle2 className="h-4 w-4 text-emerald-400" /> : <ShieldQuestion className="h-4 w-4 text-slate-400" />}</div><div className="mt-1 text-[10px] text-text-muted">{layer.status} · {layer.provenance}</div></div>)}</aside>
    </section>

    <div className="rounded-lg border border-amber-500/25 bg-amber-500/5 p-3 text-xs text-amber-100"><strong>Data limitation:</strong> {config.unavailable}</div>
    <div className="flex flex-wrap gap-3 text-[10px] text-text-muted"><span>GREEN — SAFE</span><span>YELLOW — WATCH</span><span>ORANGE — WARNING</span><span>RED — CRITICAL</span><span>GREY — NO / INSUFFICIENT DATA</span></div>
  </div>;
};

export const JalaIntelligencePage = () => <DomainIntelligencePage domain="JALA" />;
export const AgniIntelligencePage = () => <DomainIntelligencePage domain="AGNI" />;
export const BhumiIntelligencePage = () => <DomainIntelligencePage domain="BHUMI" />;
export const VayuIntelligencePage = () => <DomainIntelligencePage domain="VAYU" />;
export const AkashaIntelligencePage = () => <DomainIntelligencePage domain="AKASHA" />;
