import React, { useState, useEffect, useRef } from 'react';
import { useOutletContext } from 'react-router-dom';
import { LiveMap } from '../components/map/LiveMap';
import { IncidentFeed } from '../components/widgets/IncidentFeed';
import { LiveNodeStrips } from '../components/widgets/LiveNodeStrips';
import { NodeDetailDrawer } from '../components/widgets/NodeDetailDrawer';
import { PanchaBhoothaOverview, type ElementStatus } from '../components/widgets/PanchaBhoothaOverview';
import { fetchNodes, fetchAlerts, fetchElements } from '../services/api';
import { wsClient } from '../services/websocket';
import { Shield, Radio, Activity, Cpu, AlertTriangle, Layers } from 'lucide-react';

export const CommandCentre: React.FC = () => {
  const { summary } = useOutletContext<any>();
  const [nodes, setNodes] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [elements, setElements] = useState<ElementStatus[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [filterHazard, setFilterHazard] = useState<string>('ALL');
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');

  const refreshTimerRef = useRef<number | null>(null);
  const requestInFlightRef = useRef(false);

  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadData = async (silent = false) => {
    if (requestInFlightRef.current) return;

    requestInFlightRef.current = true;

    try {
      if (!silent) setLoading(true);

      setLoadError(null);

      const [nodeData, alertData, elementData] = await Promise.all([
        fetchNodes(),
        fetchAlerts(),
        fetchElements(),
      ]);

      setNodes(nodeData);
      setAlerts(alertData);
      setElements(elementData);
    } catch (err) {
      console.warn('Error loading command centre data:', err);

      setLoadError(
        'Live operational data is temporarily unavailable. Existing data remains visible.'
      );
    } finally {
      requestInFlightRef.current = false;

      if (!silent) {
        setLoading(false);
      }
    }
  };

  const queueRefresh = () => {
    if (refreshTimerRef.current !== null) return;

    refreshTimerRef.current = window.setTimeout(() => {
      refreshTimerRef.current = null;
      void loadData(true);
    }, 500);
  };

  useEffect(() => {
    void loadData(false);

    const unsubTelem = wsClient.subscribe('telemetry.updated', queueRefresh);
    const unsubRisk = wsClient.subscribe('risk.updated', queueRefresh);
    const unsubAlert = wsClient.subscribe('alert.created', queueRefresh);
    const unsubAlertAck = wsClient.subscribe('alert.acknowledged', queueRefresh);
    const unsubAlertRes = wsClient.subscribe('alert.resolved', queueRefresh);

    return () => {
      unsubTelem();
      unsubRisk();
      unsubAlert();
      unsubAlertAck();
      unsubAlertRes();

      if (refreshTimerRef.current !== null) {
        window.clearTimeout(refreshTimerRef.current);
        refreshTimerRef.current = null;
      }
    };
  }, []);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  return (
    <div className="prahari-command-centre h-full flex flex-col p-3 lg:p-4 space-y-3 overflow-y-auto">
      <div className="prahari-command-status shrink-0">
        {loadError && (
          <div className="mb-2 flex items-center justify-between gap-3 rounded-lg border border-hazard-warning/30 bg-hazard-warning/10 px-3 py-2 text-[11px] text-hazard-warning">
            <span>{loadError}</span>

            <button
              onClick={() => void loadData(false)}
              className="rounded-md border border-hazard-warning/30 bg-bg-surface px-2.5 py-1 font-semibold hover:bg-bg-elevated transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {loading && nodes.length === 0 && (
          <div className="mb-2 flex items-center gap-2 rounded-lg border border-accent-info/20 bg-accent-info/5 px-3 py-2 text-[11px] text-accent-info">
            <span className="h-2 w-2 rounded-full bg-accent-info animate-pulse" />
            Synchronizing live PRAHARI telemetry...
          </div>
        )}
      </div>

      {/* 1. TOP OPERATIONAL STATUS STRIP */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 shrink-0">
        <div className="bg-bg-secondary p-2.5 rounded border border-border-subtle flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded bg-hazard-normal/15 text-hazard-normal flex items-center justify-center shrink-0">
            <Radio className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-[10px] text-text-muted uppercase">Fleet Status</div>
            <div className="font-bold text-xs text-text-primary truncate">
              {summary?.nodes_online ?? 0} / {summary?.nodes_total ?? 0} Operational Nodes
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-2.5 rounded border border-border-subtle flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded bg-hazard-warning/15 text-hazard-warning flex items-center justify-center shrink-0">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-[10px] text-text-muted uppercase">Active Alerts</div>
            <div className="font-bold text-xs text-text-primary truncate">
              {summary?.active_alerts_count ?? 0} Unresolved
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-2.5 rounded border border-border-subtle flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded bg-accent-info/15 text-accent-info flex items-center justify-center shrink-0">
            <Cpu className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-[10px] text-text-muted uppercase">Gateway Link</div>
            <div className="font-bold text-xs text-text-primary truncate">
              {summary?.gateway_mode === 'REAL' ? 'USB Serial Hardware' : 'Windows Python / Simulator'}
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-2.5 rounded border border-border-subtle flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded bg-accent-ai/15 text-accent-ai flex items-center justify-center shrink-0">
            <Shield className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-[10px] text-text-muted uppercase">System Mode</div>
            <div className="font-bold text-xs text-text-primary truncate">
              {summary?.network_mode || 'LOCAL EDGE'}
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-2.5 rounded border border-border-subtle flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded bg-purple-500/15 text-purple-400 flex items-center justify-center shrink-0">
            <Activity className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-[10px] text-text-muted uppercase">Fleet Avg Risk</div>
            <div className="font-bold text-xs text-text-primary truncate">
              {summary?.average_risk == null ? 'Awaiting evidence' : `${summary.average_risk}%`}
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-2.5 rounded border border-border-subtle flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded bg-emerald-500/15 text-emerald-400 flex items-center justify-center shrink-0">
            <Layers className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-[10px] text-text-muted uppercase">Sim Engine</div>
            <div className="font-bold text-xs text-accent-info truncate">
              Continuous Stream
            </div>
          </div>
        </div>
      </div>

      {elements.length > 0 && <PanchaBhoothaOverview domains={elements} />}

      {/* 2. MAIN CENTER: MAP + RIGHT RAIL INCIDENT FEED */}
      <div className="grid grid-cols-1 lg:grid-cols-10 gap-3 flex-1 min-h-[560px] xl:min-h-[620px]">
        {/* Large Tactical Live Map (2 cols on large screen) */}
        <div className="lg:col-span-7 flex flex-col h-full min-h-[560px] xl:min-h-[620px]">
          {/* Map Tactical Filter Bar */}
          <div className="bg-gradient-to-r from-bg-secondary via-bg-surface to-bg-secondary px-3.5 py-2 rounded-t-xl border-t border-x border-border-subtle flex items-center justify-between text-xs shadow-[0_8px_30px_rgba(0,0,0,0.18)]">
            <span className="font-semibold text-text-primary text-[11px] uppercase tracking-wider">
              Geospatial Hazard Map
            </span>
            <div className="flex items-center space-x-2">
              <select
                value={filterHazard}
                onChange={(e) => setFilterHazard(e.target.value)}
                className="bg-bg-surface border border-border-subtle rounded px-2 py-0.5 text-[11px] text-text-secondary focus:outline-none"
              >
                <option value="ALL">All Hazards</option>
                <option value="FLOOD">Flood (JALA)</option>
                <option value="FIRE">Fire (AGNI)</option>
                <option value="LANDSLIDE">Landslide (BHUMI)</option>
                <option value="AIR_QUALITY">Air Quality (VAYU)</option>
                <option value="WEATHER">Atmosphere (AKASHA)</option>
              </select>

              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="bg-bg-surface border border-border-subtle rounded px-2 py-0.5 text-[11px] text-text-secondary focus:outline-none"
              >
                <option value="ALL">All Severities</option>
                <option value="NORMAL">Normal</option>
                <option value="WATCH">Watch</option>
                <option value="WARNING">Warning</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
          </div>

          <div className="flex-1 rounded-b-xl overflow-hidden border border-border-subtle shadow-[0_18px_55px_rgba(0,0,0,0.28)]">
            <LiveMap
              nodes={nodes}
              selectedNodeId={selectedNodeId || undefined}
              onSelectNode={(id) => setSelectedNodeId(id)}
              filterHazard={filterHazard}
              filterSeverity={filterSeverity}
            />
          </div>
        </div>

        {/* Right Rail: Active Incident Triage Feed */}
        <div className="lg:col-span-3 h-full min-h-[420px] lg:min-h-[560px] xl:min-h-[620px]">
          <IncidentFeed
            alerts={alerts}
            onRefresh={loadData}
            onSelectAlert={(a) => setSelectedNodeId(a.node_id)}
          />
        </div>
      </div>

      {/* 3. BOTTOM LIVE NODE STRIPS */}
      <div className="shrink-0">
        <LiveNodeStrips nodes={nodes} />
      </div>

      {/* Side Drawer for Node Details */}
      {selectedNode && (
        <NodeDetailDrawer
          node={selectedNode}
          onClose={() => setSelectedNodeId(null)}
        />
      )}
    </div>
  );
};
