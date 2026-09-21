import React, { useState, useEffect } from 'react';
import { LiveMap } from '../components/map/LiveMap';
import { NodeDetailDrawer } from '../components/widgets/NodeDetailDrawer';
import { fetchNodes } from '../services/api';
import { wsClient } from '../services/websocket';
import { Map as MapIcon, Layers, Radio } from 'lucide-react';

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

  return (
    <div className="h-full flex flex-col p-3 space-y-2">
      {/* Map Control Bar */}
      <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shrink-0">
        <div className="flex items-center space-x-2">
          <MapIcon className="w-4 h-4 text-accent-info" />
          <span className="font-bold text-text-primary text-xs uppercase tracking-wider">
            Full Tactical GIS Map Overview
          </span>
          <span className="text-[10px] font-mono text-text-muted">
            • 3 Georeferenced Edge Nodes
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={filterHazard}
            onChange={(e) => setFilterHazard(e.target.value)}
            className="bg-bg-surface border border-border-subtle rounded px-2.5 py-1 text-xs text-text-secondary focus:outline-none"
          >
            <option value="ALL">All Hazards</option>
            <option value="FLOOD">JALA (Flood)</option>
            <option value="FIRE">AGNI (Fire)</option>
            <option value="LANDSLIDE">BHUMI (Landslide)</option>
          </select>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-bg-surface border border-border-subtle rounded px-2.5 py-1 text-xs text-text-secondary focus:outline-none"
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
      <div className="flex-1 rounded-lg overflow-hidden border border-border-subtle min-h-[450px]">
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
