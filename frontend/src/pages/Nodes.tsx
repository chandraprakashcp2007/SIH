import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchNodes } from '../services/api';
import { wsClient } from '../services/websocket';
import { Server, Search, Filter, Battery, Radio, Activity, ExternalLink, ShieldCheck } from 'lucide-react';

export const Nodes: React.FC = () => {
  const [nodes, setNodes] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const navigate = useNavigate();

  const loadNodes = async () => {
    try {
      const data = await fetchNodes();
      setNodes(data);
    } catch (err) {
      console.error('Error fetching nodes:', err);
    }
  };

  useEffect(() => {
    loadNodes();
    const unsub = wsClient.subscribe('node.status_changed', loadNodes);
    return () => unsub();
  }, []);

  const filtered = nodes.filter((n) => {
    if (typeFilter !== 'ALL' && n.node_type !== typeFilter) return false;
    if (statusFilter !== 'ALL' && n.status !== statusFilter) return false;
    if (
      searchTerm &&
      !n.id.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !n.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      !n.location_name.toLowerCase().includes(searchTerm.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <div>
          <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
            <Server className="w-5 h-5 text-accent-info" />
            <span>Operational Node Fleet Registry</span>
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Real-time health, RF signal telemetry, and sensor trust for edge units.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-text-muted" />
            <input
              type="text"
              placeholder="Search node or zone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-bg-surface border border-border-subtle rounded pl-8 pr-3 py-1.5 text-xs text-text-primary focus:outline-none focus:border-accent-info w-44"
            />
          </div>

          {/* Type filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-secondary focus:outline-none"
          >
            <option value="ALL">All Types</option>
            <option value="FLOOD">JALA (Flood)</option>
            <option value="FIRE">AGNI (Fire)</option>
            <option value="LANDSLIDE">BHUMI (Landslide)</option>
            <option value="AIR_QUALITY">VAYU (Air Quality)</option>
            <option value="WEATHER">AKASHA (Atmosphere)</option>
          </select>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-secondary focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="ONLINE">Online</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
            <option value="OFFLINE">Offline</option>
          </select>
        </div>
      </div>

      {/* Nodes Table */}
      <div className="bg-bg-secondary rounded-lg border border-border-subtle overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-bg-surface text-text-muted text-[11px] uppercase tracking-wider border-b border-border-subtle">
              <tr>
                <th className="py-3 px-4">Node ID / Name</th>
                <th className="py-3 px-4">Hazard Type</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Status & Risk</th>
                <th className="py-3 px-4">Signal / Transport</th>
                <th className="py-3 px-4">Battery</th>
                <th className="py-3 px-4">Packet Loss</th>
                <th className="py-3 px-4">Last Seen</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {filtered.map((node) => {
                const riskBand = node.latest_risk?.risk_band || 'NORMAL';
                const riskScore = node.latest_risk?.risk_score || 0;

                let statusBadge = 'bg-hazard-normal/20 text-hazard-normal border-hazard-normal/40';
                if (node.status === 'OFFLINE') statusBadge = 'bg-hazard-offline/20 text-hazard-offline border-hazard-offline/40';
                else if (riskBand === 'CRITICAL') statusBadge = 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical/40';
                else if (riskBand === 'WARNING') statusBadge = 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning/40';
                else if (riskBand === 'WATCH') statusBadge = 'bg-hazard-watch/20 text-hazard-watch border-hazard-watch/40';

                return (
                  <tr
                    key={node.id}
                    onClick={() => navigate(`/nodes/${node.id}`)}
                    className="hover:bg-bg-surface/50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4">
                      <div className="font-bold text-accent-info">{node.id}</div>
                      <div className="text-[11px] text-text-muted">{node.name}</div>
                    </td>

                    <td className="py-3 px-4">
                      <span className="font-mono text-[11px] bg-bg-surface px-2 py-0.5 rounded border border-border-subtle">
                        {node.node_type}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-text-secondary">
                      {node.location_name}
                    </td>

                    <td className="py-3 px-4">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${statusBadge}`}>
                        {node.status} ({riskScore}%)
                      </span>
                    </td>

                    <td className="py-3 px-4 font-mono">
                      <span className={node.signal_rssi < -85 ? 'text-hazard-warning' : 'text-text-primary'}>
                        {node.signal_rssi} dBm
                      </span>
                    </td>

                    <td className="py-3 px-4 font-mono">
                      <span className={node.battery_pct < 25 ? 'text-hazard-critical' : 'text-text-primary'}>
                        {node.battery_pct?.toFixed(0) ?? 95}%
                      </span>
                    </td>

                    <td className="py-3 px-4 font-mono text-text-secondary">
                      {node.packet_loss_pct?.toFixed(1) ?? 0.0}%
                    </td>

                    <td className="py-3 px-4 font-mono text-[11px] text-text-muted">
                      {new Date(node.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>

                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/nodes/${node.id}`);
                        }}
                        className="p-1.5 rounded hover:bg-bg-surface text-accent-info hover:text-cyan-300 transition-colors"
                        title="View Detailed Node Diagnostics"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
