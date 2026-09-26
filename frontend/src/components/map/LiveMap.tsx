import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Layers, ZoomIn, ZoomOut, Maximize2, Shield, Droplets, Flame, Mountain } from 'lucide-react';

interface NodeMapData {
  id: string;
  name: string;
  node_type: string;
  latitude: number;
  longitude: number;
  status: string;
  location_name: string;
  latest_risk?: {
    risk_score: number;
    risk_band: string;
    confidence: number;
    human_explanation?: string;
  };
  latest_metrics?: any;
}

const DEMO_NODE_COORDS: Record<string, [number, number]> = {
  "JALA-01": [26.1445, 91.7362],   // Assam
  "AGNI-02": [21.9497, 86.7200],   // Odisha
  "BHUMI-03": [30.3165, 78.0322],  // Uttarakhand
  "VAYU-04": [28.6139, 77.2090],   // Delhi
  "AKASHA-05": [13.0827, 80.2707], // Chennai
};

const resolveMapPosition = (node: NodeMapData): [number, number] => {
  const lat = Number(node.latitude);
  const lon = Number(node.longitude);

  const validIndiaCoordinate =
    Number.isFinite(lat) &&
    Number.isFinite(lon) &&
    lat >= 6 &&
    lat <= 38 &&
    lon >= 68 &&
    lon <= 98;

  if (validIndiaCoordinate) {
    return [lat, lon];
  }

  return DEMO_NODE_COORDS[node.id] || [22.5, 79.0];
};

interface LiveMapProps {
  nodes: NodeMapData[];
  selectedNodeId?: string;
  onSelectNode?: (nodeId: string) => void;
  filterHazard?: string;
  filterSeverity?: string;
}

export const LiveMap: React.FC<LiveMapProps> = ({
  nodes,
  selectedNodeId,
  onSelectNode,
  filterHazard,
  filterSeverity,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Record<string, L.Marker>>({});
  const lastAutoFitKeyRef = useRef<string>('');
  const [offlineTilesActive, setOfflineTilesActive] = useState<boolean>(false);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Center on Northern/Eastern India monitoring corridor
    const map = L.map(mapContainerRef.current, {
      center: [22.5, 79.0],
      zoom: 5,
      zoomControl: false,

      // Smooth PRAHARI map behaviour
      zoomAnimation: true,
      fadeAnimation: false,
      markerZoomAnimation: true,
      preferCanvas: true,

      // Controlled pan / zoom
      inertia: true,
      inertiaDeceleration: 3200,
      inertiaMaxSpeed: 1100,

      // Prevent mouse wheel from skipping several zoom levels
      wheelDebounceTime: 80,
      wheelPxPerZoomLevel: 110,
    });

    /*
      No API key is required.
      URL is constructed this way to prevent terminals/editors
      from accidentally converting it into Markdown.
    */
    // Keyless map chain:
    // CARTO Dark -> OpenStreetMap -> local tactical grid.
    const primaryLayer = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        minZoom: 3,
        maxZoom: 19,
        keepBuffer: 6,
        updateWhenIdle: true,
        detectRetina: false,
        className: 'prahari-map-dark-native',
      }
    );

    const fallbackLayer = L.tileLayer(
      'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution: '&copy; OpenStreetMap contributors',
        minZoom: 3,
        maxZoom: 18,
        keepBuffer: 6,
        updateWhenIdle: true,
        detectRetina: false,
        className: 'prahari-map-tiles',
      }
    );

    let primaryFailures = 0;
    let fallbackEnabled = false;

    primaryLayer.on('tileerror', () => {
      primaryFailures += 1;

      if (primaryFailures >= 2 && !fallbackEnabled) {
        fallbackEnabled = true;

        if (map.hasLayer(primaryLayer)) {
          map.removeLayer(primaryLayer);
        }

        fallbackLayer.addTo(map);
      }
    });

    primaryLayer.on('load', () => {
      setOfflineTilesActive(false);
      window.requestAnimationFrame(() => map.invalidateSize(false));
    });

    fallbackLayer.on('load', () => {
      setOfflineTilesActive(false);
      window.requestAnimationFrame(() => map.invalidateSize(false));
    });

    fallbackLayer.on('tileerror', () => {
      setOfflineTilesActive(true);
    });

    primaryLayer.addTo(map);

    /*
      Once zoom/pan finishes, correct the Leaflet viewport.
      This prevents the right/left side from remaining
      partially unpainted after dashboard layout changes.
    */
    const settleMapViewport = () => {
      window.requestAnimationFrame(() => {
        map.invalidateSize(false);
      });
    };

    map.on('zoomend', settleMapViewport);
    map.on('moveend', settleMapViewport);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);



  // PRAHARI_RESIZE_OBSERVER
  useEffect(() => {
    const container = mapContainerRef.current;
    const map = mapInstanceRef.current;

    if (!container || !map) return;

    const updateMapSize = () => {
      window.requestAnimationFrame(() => {
        map.invalidateSize(false);
      });
    };

    const observer = new ResizeObserver(updateMapSize);

    observer.observe(container);

    window.addEventListener('resize', updateMapSize);

    const initialTimer = window.setTimeout(
      updateMapSize,
      120
    );

    return () => {
      observer.disconnect();

      window.removeEventListener(
        'resize',
        updateMapSize
      );

      window.clearTimeout(initialTimer);
    };
  }, []);

  // Update Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    const filtered = nodes.filter((n) => {
      if (filterHazard && filterHazard !== 'ALL' && n.node_type !== filterHazard) return false;
      if (filterSeverity && filterSeverity !== 'ALL' && n.latest_risk?.risk_band !== filterSeverity) return false;
      return true;
    });

    // Remove obsolete markers
    Object.keys(markersRef.current).forEach((id) => {
      if (!filtered.find((n) => n.id === id)) {
        markersRef.current[id].remove();
        delete markersRef.current[id];
      }
    });

    filtered.forEach((node) => {
      const position = resolveMapPosition(node);

      const riskBand = node.latest_risk?.risk_band || 'NORMAL';
      const riskScore = node.latest_risk?.risk_score ?? 0;

      let markerColor = '#22C55E'; // Normal
      if (node.status === 'OFFLINE') markerColor = '#64748B';
      else if (riskBand === 'CRITICAL') markerColor = '#EF4444';
      else if (riskBand === 'WARNING') markerColor = '#F97316';
      else if (riskBand === 'WATCH') markerColor = '#EAB308';

      const iconHtml = `
        <div style="
          width: 34px;
          height: 34px;
          border-radius: 50%;
          background: ${markerColor};
          border: 3px solid #07111F;
          box-shadow: 0 0 14px ${markerColor}99;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #07111F;
          font-weight: bold;
          font-size: 11px;
          cursor: pointer;
        ">
          ${node.id.split('-')[0][0]}
        </div>
      `;

      const customIcon = L.divIcon({
        className: 'custom-node-marker',
        html: iconHtml,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
      });

      if (markersRef.current[node.id]) {
        markersRef.current[node.id].setLatLng(position);
        markersRef.current[node.id].setIcon(customIcon);
      } else {
        const marker = L.marker(position, { icon: customIcon }).addTo(map);

        marker.on('click', () => {
          if (onSelectNode) onSelectNode(node.id);
        });

        // Popup Content
        marker.bindPopup(`
          <div style="font-family: inherit; font-size: 12px; padding: 4px; min-width: 200px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <strong style="color: #27C7E8; font-size: 13px;">${node.id}</strong>
              <span style="background: ${markerColor}33; color: ${markerColor}; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 10px;">
                ${riskBand} (${riskScore}%)
              </span>
            </div>
            <div style="color: #9FB0C3; margin-bottom: 4px;">${node.name}</div>
            <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">📍 ${node.location_name}</div>
            <div style="font-size: 11px; color: #F1F5F9; border-top: 1px solid #22364A; padding-top: 6px;">
              ${node.latest_risk?.human_explanation?.split('\n')[0] || 'Nominal telemetry stream.'}
            </div>
          </div>
        `);

        markersRef.current[node.id] = marker;
      }
    });


    // PRAHARI_AUTO_FIT
    if (filtered.length > 0) {
      const fitKey = [
        filterHazard || 'ALL',
        filterSeverity || 'ALL',
        ...filtered.map((node) => node.id).sort(),
      ].join('|');

      if (lastAutoFitKeyRef.current !== fitKey) {
        lastAutoFitKeyRef.current = fitKey;

        window.requestAnimationFrame(() => {
          map.invalidateSize(false);

          const visibleMarkers =
            Object.values(markersRef.current);

          if (visibleMarkers.length === 0) return;

          const group =
            L.featureGroup(visibleMarkers);

          const bounds =
            group.getBounds();

          if (bounds.isValid()) {
            map.fitBounds(
              bounds.pad(0.28),
              {
                padding: [48, 48],
                maxZoom: 8,
                animate: true,
                duration: 0.65,
              }
            );
          }
        });
      }
    }

  }, [nodes, filterHazard, filterSeverity, onSelectNode]);

  const fitAllNodes = () => {
    const map = mapInstanceRef.current;

    if (!map) return;

    const markers =
      Object.values(markersRef.current);

    if (markers.length === 0) return;

    map.invalidateSize(false);

    const group =
      L.featureGroup(markers);

    const bounds =
      group.getBounds();

    if (!bounds.isValid()) return;

    map.fitBounds(
      bounds.pad(0.28),
      {
        padding: [48, 48],
        maxZoom: 8,
        animate: true,
        duration: 0.65,
      }
    );
  };



  // PRAHARI_SELECTED_NODE_FOCUS
  useEffect(() => {
    if (!selectedNodeId) return;

    const map = mapInstanceRef.current;
    const marker = markersRef.current[selectedNodeId];

    if (!map || !marker) return;

    const position = marker.getLatLng();

    map.flyTo(
      position,
      Math.max(map.getZoom(), 8),
      {
        animate: true,
        duration: 0.65,
      }
    );

    marker.openPopup();
  }, [selectedNodeId]);

  return (
    <div className="relative w-full h-full min-h-[560px] xl:min-h-[620px] bg-bg-secondary rounded-lg border border-border-subtle overflow-hidden">
      {/* Offline Tactical Grid Backdrop Fallback (visible if tiles fail) */}
      <div
        className={`absolute inset-0 pointer-events-none transition-opacity duration-300 ${
          offlineTilesActive ? 'opacity-100' : 'opacity-0'
        }`}
        style={{
          backgroundImage: `
            radial-gradient(circle at 50% 50%, rgba(39, 199, 232, 0.05) 0%, transparent 80%),
            linear-gradient(#102033 1px, transparent 1px),
            linear-gradient(90deg, #102033 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 30px 30px, 30px 30px',
        }}
      >
        <div className="absolute top-4 left-4 bg-bg-elevated/90 border border-border-subtle px-3 py-1.5 rounded text-xs text-text-secondary">
          📡 <strong>Local Tactical Grid Active</strong> (Offline Tile Fallback)
        </div>
      </div>

      {/* Leaflet DOM Node */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Floating Tactical Controls */}
      <div className="absolute top-3 right-3 flex flex-col space-y-1.5 z-10">
        <button
          onClick={() => mapInstanceRef.current?.zoomIn()}
          className="w-8 h-8 rounded bg-bg-surface hover:bg-bg-elevated text-text-primary border border-border-subtle flex items-center justify-center shadow-lg transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => mapInstanceRef.current?.zoomOut()}
          className="w-8 h-8 rounded bg-bg-surface hover:bg-bg-elevated text-text-primary border border-border-subtle flex items-center justify-center shadow-lg transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={fitAllNodes}
          className="w-8 h-8 rounded bg-bg-surface hover:bg-bg-elevated text-accent-info border border-border-subtle flex items-center justify-center shadow-lg transition-colors"
          title="Fit All Operational Nodes"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Bottom Floating Legend */}
      <div className="absolute bottom-3 left-3 bg-bg-surface/90 backdrop-blur-sm border border-border-subtle rounded-md px-3 py-1.5 text-[11px] flex items-center space-x-3 z-10 text-text-secondary">
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-hazard-normal"></span>
          <span>Normal</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-hazard-watch"></span>
          <span>Watch</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-hazard-warning"></span>
          <span>Warning</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-hazard-critical animate-pulse"></span>
          <span>Critical</span>
        </div>
      </div>
    </div>
  );
};
