import React, { useEffect, useMemo, useRef, useState } from 'react';
import L from 'leaflet';
import { Crosshair, Layers3, Maximize2, ZoomIn, ZoomOut } from 'lucide-react';

export type NativeDomain = 'JALA' | 'AGNI' | 'BHUMI' | 'VAYU' | 'AKASHA';

export type DomainLayer = {
  id: string;
  status: string;
  provenance: string;
};

export type NativeHazardMapFeature = {
  geometry?: { coordinates?: [number, number] };
  properties?: Record<string, any>;
};

export type NativeHazardMapConfig = {
  domain: NativeDomain;
  testId: string;
  modeClass: string;
  mapLabel: string;
  accent: string;
  markerText: string;
  zoom: number;
  legend: Array<{ label: string; color: string }>;
  controls: string[];
};

interface Props {
  feature: NativeHazardMapFeature;
  layers: DomainLayer[];
  config: NativeHazardMapConfig;
}

const fallback: Record<NativeDomain, [number, number]> = {
  JALA: [26.1445, 91.7362],
  AGNI: [21.9497, 86.72],
  BHUMI: [30.3165, 78.0322],
  VAYU: [28.6139, 77.209],
  AKASHA: [13.0827, 80.2707],
};

function resolvePosition(domain: NativeDomain, feature: NativeHazardMapFeature): [number, number] {
  const coordinates = feature?.geometry?.coordinates;
  const lon = Number(coordinates?.[0]);
  const lat = Number(coordinates?.[1]);
  if (Number.isFinite(lat) && Number.isFinite(lon)) return [lat, lon];
  return fallback[domain];
}

function riskColor(band: string | undefined) {
  if (band === 'CRITICAL') return '#ef4444';
  if (band === 'WARNING') return '#f97316';
  if (band === 'WATCH') return '#eab308';
  if (band === 'SAFE' || band === 'NORMAL') return '#22c55e';
  return '#64748b';
}

export const NativeHazardMapBase: React.FC<Props> = ({ feature, layers, config }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const dynamicRef = useRef<L.LayerGroup | null>(null);
  const [tilesDegraded, setTilesDegraded] = useState(false);
  const [layerPanelOpen, setLayerPanelOpen] = useState(false);
  const position = useMemo(() => resolvePosition(config.domain, feature), [config.domain, feature]);
  const props = feature?.properties || {};

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: position,
      zoom: config.zoom,
      zoomControl: false,
      preferCanvas: true,
      fadeAnimation: false,
      maxBounds: [[5, 67], [38.5, 98.5]],
      maxBoundsViscosity: 0.7,
    });

    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      minZoom: 4,
      maxZoom: 18,
      keepBuffer: 4,
      updateWhenIdle: true,
      className: `prahari-map-tiles native-domain-tiles native-domain-tiles-${config.domain.toLowerCase()}`,
    });
    tiles.on('tileerror', () => setTilesDegraded(true));
    tiles.on('load', () => setTilesDegraded(false));
    tiles.addTo(map);

    dynamicRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    const observer = new ResizeObserver(() => requestAnimationFrame(() => map.invalidateSize(false)));
    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      map.remove();
      mapRef.current = null;
      dynamicRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const dynamic = dynamicRef.current;
    if (!map || !dynamic) return;

    dynamic.clearLayers();
    const band = props.risk_band || 'NO_DATA';
    const color = riskColor(band);

    const icon = L.divIcon({
      className: 'native-domain-node-icon',
      html: `<div class="native-domain-node-dot" style="--domain-accent:${config.accent};--risk-color:${color}"><span>${config.markerText}</span></div>`,
      iconSize: [46, 46],
      iconAnchor: [23, 23],
    });

    const marker = L.marker(position, { icon }).addTo(dynamic);
    marker.bindPopup(`
      <div style="min-width:210px;font-size:12px">
        <strong style="color:${config.accent}">${props.node_id || config.domain}</strong>
        <div style="margin-top:4px;color:#cbd5e1">${props.name || config.mapLabel}</div>
        <div style="margin-top:6px;color:#94a3b8">Risk: ${band}${props.risk_score == null ? '' : ` · ${props.risk_score}`}</div>
        <div style="margin-top:3px;color:#64748b">Source: ${props.provenance || 'UNKNOWN'}</div>
      </div>
    `);

    if (props.risk_score != null && band !== 'NO_DATA') {
      const visualRadius = 900 + Math.min(2400, Number(props.risk_score) * 18);
      L.circle(position, {
        radius: visualRadius,
        color,
        weight: 1.5,
        dashArray: '7 8',
        fillColor: color,
        fillOpacity: 0.08,
      })
        .bindTooltip('Risk-index emphasis only — not a measured impact extent')
        .addTo(dynamic);
    }

    map.setView(position, config.zoom, { animate: false });
  }, [config, position, props.name, props.node_id, props.provenance, props.risk_band, props.risk_score]);

  const availableLayers = layers.filter((layer) => layer.status === 'AVAILABLE').length;

  const toggleFullscreen = async () => {
    const host = containerRef.current?.parentElement;
    if (!host) return;
    if (!document.fullscreenElement) await host.requestFullscreen?.();
    else await document.exitFullscreen?.();
    window.setTimeout(() => mapRef.current?.invalidateSize(false), 120);
  };

  return (
    <div data-testid={config.testId} className={`native-hazard-map native-hazard-map-${config.modeClass} relative h-full min-h-[520px] overflow-hidden rounded-xl bg-[#050b14]`}>
      <div ref={containerRef} className="absolute inset-0" />
      <div className={`native-domain-visual native-domain-visual-${config.modeClass}`} aria-hidden="true" />

      {tilesDegraded && (
        <div className="absolute left-3 top-3 z-[600] rounded-md border border-amber-400/30 bg-slate-950/90 px-3 py-2 text-[10px] font-semibold text-amber-200 backdrop-blur-xl">
          MAP TILES DEGRADED · LOCAL EVIDENCE REMAINS AVAILABLE
        </div>
      )}

      <div className="absolute left-3 top-3 z-[550] max-w-[70%] rounded-lg border border-white/10 bg-slate-950/80 px-3 py-2 backdrop-blur-xl">
        <div className="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-500">Native hazard map</div>
        <div className="mt-0.5 text-xs font-bold text-white">{config.mapLabel}</div>
        <div className="mt-1 flex flex-wrap gap-1 text-[9px]">
          <span className="rounded border border-white/10 bg-white/5 px-1.5 py-0.5 text-slate-300">{props.provenance || 'UNKNOWN'}</span>
          <span className="rounded border border-white/10 bg-white/5 px-1.5 py-0.5 text-slate-400">{availableLayers}/{layers.length} layers available</span>
        </div>
      </div>

      <div className="absolute right-3 top-3 z-[650] flex flex-col gap-1.5">
        <button type="button" title="Zoom in" onClick={() => mapRef.current?.zoomIn()} className="native-map-control"><ZoomIn className="h-4 w-4" /></button>
        <button type="button" title="Zoom out" onClick={() => mapRef.current?.zoomOut()} className="native-map-control"><ZoomOut className="h-4 w-4" /></button>
        <button type="button" title="Fit to node" onClick={() => mapRef.current?.flyTo(position, config.zoom, { duration: 0.5 })} className="native-map-control"><Crosshair className="h-4 w-4" /></button>
        <button type="button" title="Layer status" aria-label={`${config.domain} layer status`} onClick={() => setLayerPanelOpen((value) => !value)} className="native-map-control"><Layers3 className="h-4 w-4" /></button>
        <button type="button" title="Fullscreen map" onClick={toggleFullscreen} className="native-map-control"><Maximize2 className="h-4 w-4" /></button>
      </div>

      {layerPanelOpen && (
        <div className="absolute right-14 top-3 z-[640] w-64 rounded-xl border border-white/10 bg-slate-950/95 p-3 text-[10px] shadow-2xl backdrop-blur-xl">
          <div className="mb-2 font-bold uppercase tracking-[0.14em] text-slate-300">Operational layers</div>
          <div className="max-h-64 space-y-1 overflow-auto">
            {layers.map((layer) => (
              <div key={layer.id} className="flex items-center justify-between gap-2 rounded border border-white/5 bg-white/[0.03] px-2 py-1.5">
                <span className="truncate text-slate-300">{layer.id.split('_').join(' ')}</span>
                <span className={layer.status === 'AVAILABLE' ? 'text-emerald-300' : layer.status === 'PLANNED' ? 'text-violet-300' : 'text-slate-500'}>{layer.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="absolute bottom-3 left-3 z-[550] max-w-[calc(100%-1.5rem)] rounded-lg border border-white/10 bg-slate-950/85 px-3 py-2 backdrop-blur-xl">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[9px] text-slate-300">
          {config.legend.map((item) => (
            <span key={item.label} className="flex items-center gap-1.5"><i className="h-2 w-2 rounded-full" style={{ background: item.color }} />{item.label}</span>
          ))}
        </div>
        <div className="mt-1.5 flex flex-wrap gap-1 text-[8px] uppercase tracking-wide text-slate-500">
          {config.controls.map((item) => <span key={item} className="rounded border border-white/5 px-1.5 py-0.5">{item}</span>)}
        </div>
      </div>

      <div className="absolute bottom-3 right-3 z-[550] rounded border border-white/10 bg-slate-950/85 px-2 py-1 text-[8px] font-bold tracking-wide text-slate-500 backdrop-blur-xl">
        VISUAL CONTEXT ≠ HAZARD EXTENT
      </div>
    </div>
  );
};
