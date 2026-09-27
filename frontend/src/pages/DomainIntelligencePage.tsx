import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Database,
  Radio,
  RefreshCw,
  ShieldQuestion,
} from 'lucide-react';
import { fetchGeoDomain } from '../services/api';
import { JalaFloodMap } from '../components/map/domains/JalaFloodMap';
import { AgniFireMap } from '../components/map/domains/AgniFireMap';
import { BhumiLandslideMap } from '../components/map/domains/BhumiLandslideMap';
import { VayuAirMap } from '../components/map/domains/VayuAirMap';
import { AkashaWeatherMap } from '../components/map/domains/AkashaWeatherMap';

export type DomainName = 'JALA' | 'AGNI' | 'BHUMI' | 'VAYU' | 'AKASHA';

const CONFIG: Record<DomainName, {
  hindi: string;
  title: string;
  subtitle: string;
  nodeId: string;
  metrics: string[];
  unavailable: string;
  providerLabel: string;
}> = {
  JALA: {
    hindi: 'जल',
    title: 'Flood & River Surge Intelligence',
    subtitle: 'Hydrological evidence, rainfall context, river-risk operations and downstream awareness',
    nodeId: 'JALA-01',
    metrics: ['water_level_cm', 'water_rise_rate_cm_min', 'rain_intensity'],
    unavailable: 'Authoritative river geometry, watershed and validated travel-time hydrodynamics remain unavailable unless configured in the dataset registry.',
    providerLabel: 'Hydrology / GloFAS context',
  },
  AGNI: {
    hindi: 'अग्नि',
    title: 'Fire, Smoke & Thermal Intelligence',
    subtitle: 'Local heat, flame, smoke and gas evidence with wind-aware cross-hazard context',
    nodeId: 'AGNI-02',
    metrics: ['temperature_c', 'smoke_index', 'gas_index', 'flame_detected'],
    unavailable: 'NASA FIRMS remains NOT_CONFIGURED until a valid backend MAP key and successful retrieval are present.',
    providerLabel: 'NASA FIRMS / external hotspots',
  },
  BHUMI: {
    hindi: 'भूमि',
    title: 'Geotechnical Slope & Landslide Intelligence',
    subtitle: 'Soil moisture, tilt, vibration and rainfall-linked slope-risk operations',
    nodeId: 'BHUMI-03',
    metrics: ['soil_moisture_upper_pct', 'tilt_delta_deg', 'vibration_rms', 'rain_context'],
    unavailable: 'A verified DEM and authoritative landslide susceptibility dataset remain NOT_CONFIGURED.',
    providerLabel: 'DEM / susceptibility dataset',
  },
  VAYU: {
    hindi: 'वायु',
    title: 'Air Quality, Smoke & Gas Intelligence',
    subtitle: 'Atmospheric gas/smoke evidence, wind context and AGNI relationship visibility',
    nodeId: 'VAYU-04',
    metrics: ['pm2_5', 'pm10', 'co_ppm', 'voc_index'],
    unavailable: 'PM2.5/PM10 are not physical PRAHARI measurements unless calibrated particulate hardware or a trusted external provider is explicitly configured.',
    providerLabel: 'Air-quality model / PM source',
  },
  AKASHA: {
    hindi: 'आकाश',
    title: 'Atmospheric & Severe Weather Intelligence',
    subtitle: 'Rain, pressure, humidity and wind evidence with JALA/BHUMI cross-hazard context',
    nodeId: 'AKASHA-05',
    metrics: ['rain_intensity', 'pressure_hpa', 'wind_speed_kmh', 'humidity_pct'],
    unavailable: 'Authoritative weather warning, radar and satellite feeds remain NOT_CONFIGURED unless a provider is successfully connected.',
    providerLabel: 'Weather / radar / satellite sources',
  },
};

const MAPS = {
  JALA: JalaFloodMap,
  AGNI: AgniFireMap,
  BHUMI: BhumiLandslideMap,
  VAYU: VayuAirMap,
  AKASHA: AkashaWeatherMap,
} satisfies Record<DomainName, React.ComponentType<any>>;

const riskColor: Record<string, string> = {
  SAFE: 'text-emerald-400',
  WATCH: 'text-yellow-400',
  WARNING: 'text-orange-400',
  CRITICAL: 'text-red-400',
  NO_DATA: 'text-slate-400',
};

function displayMetric(metric: string, value: unknown) {
  if (value === null || value === undefined || value === '') return 'UNAVAILABLE';
  if (typeof value === 'boolean') return value ? 'TRUE' : 'FALSE';
  return String(value);
}

export const DomainIntelligencePage: React.FC<{ domain: DomainName }> = ({ domain }) => {
  const config = CONFIG[domain];
  const MapComponent = MAPS[domain];
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setData(await fetchGeoDomain(domain));
    } catch (reason: any) {
      setError(reason?.message || `${domain} map data unavailable`);
    } finally {
      setLoading(false);
    }
  }, [domain]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    fetchGeoDomain(domain)
      .then((value) => active && setData(value))
      .catch((reason) => active && setError(reason?.message || `${domain} map data unavailable`))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [domain]);

  const feature = data?.features?.[0];
  const props = feature?.properties || {};
  const layers = useMemo(() => Array.isArray(data?.layers) ? data.layers : [], [data?.layers]);
  const available = layers.filter((layer: any) => layer.status === 'AVAILABLE').length;
  const unavailable = layers.filter((layer: any) => layer.status === 'NOT_CONFIGURED' || layer.status === 'NO_LIVE_DATA').length;

  if (loading && !data) {
    return (
      <div role="status" className="p-5 lg:p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-80 rounded bg-slate-800" />
          <div className="grid gap-3 lg:grid-cols-4">{[0, 1, 2, 3].map((item) => <div key={item} className="h-24 rounded-xl bg-slate-900" />)}</div>
          <div className="h-[540px] rounded-xl bg-slate-900" />
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div role="alert" className="p-6">
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-5 text-red-100">
          <AlertTriangle className="mb-2 h-5 w-5" />
          <div className="font-semibold">Unable to load {config.hindi} ({domain}) intelligence.</div>
          <div className="mt-1 text-xs text-red-200/80">{error}</div>
          <button type="button" onClick={load} className="mt-4 inline-flex items-center gap-2 rounded border border-red-300/30 px-3 py-1.5 text-xs hover:bg-red-400/10"><RefreshCw className="h-3.5 w-3.5" />Retry authenticated request</button>
        </div>
      </div>
    );
  }

  return (
    <div className="domain-intelligence-page space-y-4 p-4 lg:p-6" data-testid={`domain-map-${domain.toLowerCase()}`}>
      <header className="flex flex-col gap-3 rounded-2xl border border-white/5 bg-gradient-to-r from-slate-950 via-slate-900/80 to-slate-950 p-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="text-[10px] font-bold tracking-[0.22em] text-slate-500">LIVE OPERATIONS / {config.hindi} ({domain}) / {config.nodeId}</div>
          <h1 className="mt-1 text-2xl font-bold text-white">{config.hindi} ({domain}) — {config.title}</h1>
          <p className="mt-1 text-sm text-slate-400">{config.subtitle}</p>
        </div>
        <div className="flex flex-wrap gap-2 text-[10px]">
          <span className="rounded border border-white/10 bg-white/[0.03] px-2 py-1">Source: <strong>{props.provenance || 'UNKNOWN'}</strong></span>
          <span className="rounded border border-white/10 bg-white/[0.03] px-2 py-1"><Clock3 className="mr-1 inline h-3 w-3" />Freshness: {props.freshness_seconds == null ? 'NO DATA' : `${props.freshness_seconds}s`}</span>
          <span className="rounded border border-white/10 bg-white/[0.03] px-2 py-1">Generated: {data?.generated_at ? new Date(data.generated_at).toLocaleTimeString() : '—'}</span>
        </div>
      </header>

      {error && data && (
        <div role="status" className="flex items-center justify-between gap-3 rounded-lg border border-amber-400/25 bg-amber-400/5 px-3 py-2 text-xs text-amber-100">
          <span>Refresh degraded: {error}. Showing last successfully loaded domain state.</span>
          <button type="button" onClick={load} className="inline-flex items-center gap-1 rounded border border-amber-300/20 px-2 py-1"><RefreshCw className="h-3 w-3" />Retry</button>
        </div>
      )}

      <section className="grid gap-3 lg:grid-cols-4">
        <div className="rounded-xl border border-border-subtle bg-bg-secondary p-4">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">Backend risk state</div>
          <div className={`mt-2 text-2xl font-black ${riskColor[props.risk_band] || riskColor.NO_DATA}`}>{props.risk_band || 'NO_DATA'}</div>
          <div className="mt-1 text-[10px] text-text-muted">{props.risk_score == null ? 'Insufficient validated evidence' : `Score ${props.risk_score} · confidence ${props.confidence ?? '—'}%`}</div>
        </div>

        <div className="rounded-xl border border-border-subtle bg-bg-secondary p-4 lg:col-span-2">
          <div className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-text-muted">Domain evidence</div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {config.metrics.map((metric) => (
              <div key={metric} className="rounded-lg border border-white/5 bg-bg-surface p-2.5">
                <div className="truncate text-[9px] uppercase tracking-wide text-text-muted">{metric.split('_').join(' ')}</div>
                <div className="mt-1 truncate font-mono text-sm text-text-primary">{displayMetric(metric, props.metrics?.[metric])}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-border-subtle bg-bg-secondary p-4">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">Evidence availability</div>
          <div className="mt-2 flex items-center gap-2 text-sm"><Radio className="h-4 w-4 text-accent-info" />{props.provenance || 'UNKNOWN'}</div>
          <div className="mt-2 text-[10px] text-text-muted">Layers: <strong className="text-emerald-300">{available} available</strong> · {unavailable} unavailable/no-live-data</div>
          <div className="mt-1 text-[10px] text-text-muted">Observed: {props.observed_at ? new Date(props.observed_at).toLocaleString() : 'NO LIVE OBSERVATION'}</div>
        </div>
      </section>

      <section className="grid min-h-[540px] gap-4 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-h-[540px] overflow-hidden rounded-xl border border-border-subtle bg-bg-secondary shadow-[0_25px_80px_rgba(0,0,0,0.28)]">
          <MapComponent feature={feature} layers={layers} />
        </div>

        <aside className="space-y-3 rounded-xl border border-border-subtle bg-bg-secondary p-3">
          <div className="rounded-lg border border-white/5 bg-bg-surface p-3">
            <h2 className="flex items-center gap-2 text-sm font-semibold"><Database className="h-4 w-4 text-accent-info" />Operational layers</h2>
            <p className="mt-1 text-[10px] leading-4 text-text-muted">{config.providerLabel}. A map layer is operational only when the backend reports it AVAILABLE.</p>
          </div>

          <div className="max-h-[430px] space-y-2 overflow-auto pr-1">
            {layers.map((layer: any) => (
              <div key={layer.id} className="rounded-lg border border-border-subtle bg-bg-surface p-2.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium">{layer.id.split('_').join(' ')}</span>
                  {layer.status === 'AVAILABLE' ? <CheckCircle2 className="h-4 w-4 text-emerald-400" /> : <ShieldQuestion className="h-4 w-4 text-slate-500" />}
                </div>
                <div className="mt-1 flex items-center justify-between text-[9px] uppercase tracking-wide text-text-muted">
                  <span>{layer.status}</span><span>{layer.provenance}</span>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </section>

      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-xs leading-5 text-amber-100"><strong>Data limitation:</strong> {config.unavailable}</div>
      <div className="flex flex-wrap gap-3 text-[9px] font-semibold tracking-wide text-text-muted"><span>GREEN — SAFE</span><span>YELLOW — WATCH</span><span>ORANGE — WARNING</span><span>RED — CRITICAL</span><span>GREY — INSUFFICIENT / NOT CONFIGURED</span></div>
    </div>
  );
};

export const JalaIntelligencePage = () => <DomainIntelligencePage domain="JALA" />;
export const AgniIntelligencePage = () => <DomainIntelligencePage domain="AGNI" />;
export const BhumiIntelligencePage = () => <DomainIntelligencePage domain="BHUMI" />;
export const VayuIntelligencePage = () => <DomainIntelligencePage domain="VAYU" />;
export const AkashaIntelligencePage = () => <DomainIntelligencePage domain="AKASHA" />;
