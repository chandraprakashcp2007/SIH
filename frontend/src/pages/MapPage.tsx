import React, { useState, useEffect } from 'react';
import { LiveMap } from '../components/map/LiveMap';
import { NodeDetailDrawer } from '../components/widgets/NodeDetailDrawer';
import { fetchNodes } from '../services/api';
import { wsClient } from '../services/websocket';
import { SectionHeader, SourceBadge } from '../components/ui/CommandPrimitives';

export const MapPage: React.FC = () => {
  const [nodes, setNodes] = useState<any[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [filterHazard, setFilterHazard] = useState<string>('ALL');
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');

  const loadNodes = async () => {
    try {
      const data = await fetchNodes();
      setNodes(data);
    } catch (e) {
      console.error('Error fetching map nodes:', e);
    }
  };

  useEffect(() => {
    loadNodes();
    const unsub = wsClient.subscribe('node.status_changed', loadNodes);
    return () => unsub();
  }, []);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  const nodeSources = [...new Set(nodes.map((node) => node.source_mode).filter(Boolean))];
  const mapSource = nodeSources.length === 1 ? nodeSources[0] : 'UNVERIFIED';

  return (
    <div className="h-full flex flex-col p-3 lg:p-4 space-y-3 command-reveal">
      {/* Map Control Bar */}
      <div className="command-panel p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shrink-0">
        <SectionHeader eyebrow="Geospatial operations" title="Live Multi-Hazard Map" description={`${nodes.length} georeferenced edge node${nodes.length === 1 ? '' : 's'} available`} level={2} />

        <div className="flex flex-wrap items-center gap-2"><SourceBadge source={mapSource} />
          <select
            value={filterHazard}
            onChange={(e) => setFilterHazard(e.target.value)}
            aria-label="Filter map by hazard"
            className="command-select"
          >
            <option value="ALL">All Hazards</option>
            <option value="FLOOD">जल (JALA) · Flood</option><option value="FIRE">अग्नि (AGNI) · Fire</option><option value="LANDSLIDE">भूमि (BHUMI) · Landslide</option><option value="AIR_QUALITY">वायु (VAYU) · Air</option><option value="WEATHER">आकाश (AKASHA) · Weather</option>
          </select>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            aria-label="Filter map by severity"
            className="command-select"
          >
            <option value="ALL">All Severities</option>
            <option value="NORMAL">Normal</option>
            <option value="WATCH">Watch</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {/* Map Body */}
      <div className="command-map-frame flex-1 rounded-2xl overflow-hidden border border-border-subtle min-h-[450px]">
        <LiveMap
          nodes={nodes}
          selectedNodeId={selectedNodeId || undefined}
          onSelectNode={(id) => setSelectedNodeId(id)}
          filterHazard={filterHazard}
          filterSeverity={filterSeverity}
        />
      </div>

      {/* Selected Node Drawer */}
      {selectedNode && (
        <NodeDetailDrawer
          node={selectedNode}
          onClose={() => setSelectedNodeId(null)}
        />
      )}
    </div>
  );
};
