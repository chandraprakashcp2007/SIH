import React, { useState, useEffect } from 'react';
import { fetchNetworkStatus, fetchNetworkPackets } from '../services/api';
import { wsClient } from '../services/websocket';
import { Radio, Server, Cpu, Layers, ArrowRight, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';

export const NetworkPage: React.FC = () => {
  const [network, setNetwork] = useState<any>(null);
  const [packets, setPackets] = useState<any[]>([]);

  const loadNetwork = async () => {
    try {
      const [netData, pktData] = await Promise.all([
        fetchNetworkStatus(),
        fetchNetworkPackets(30),
      ]);
      setNetwork(netData);
      setPackets(pktData);
    } catch (err) {
      console.error('Error fetching network data:', err);
    }
  };

  useEffect(() => {
    loadNetwork();
    const unsub = wsClient.subscribe('telemetry.updated', loadNetwork);
    return () => unsub();
  }, []);

  if (!network) {
    return <div className="p-8 text-center text-text-muted text-xs">Loading network topology...</div>;
  }

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
          <Radio className="w-5 h-5 text-accent-info" />
          <span>LoRa Sub-GHz RF Network & Topology Inspection</span>
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          End-to-end packet audit: Physical nodes → SX1276 LoRa Concentrator → FastAPI Ingestion Engine.
        </p>
      </div>

      {/* Visual Network Topology Pipeline */}
      <div className="bg-bg-secondary p-5 rounded-lg border border-border-subtle">
        <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4">
          Physical Data Pipeline Topology
        </h3>

        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* 3 Edge Nodes */}
          <div className="space-y-2 w-full md:w-56">
            {network.nodes?.map((n: any) => (
              <div
                key={n.node_id}
                className="bg-bg-surface p-2.5 rounded border border-border-subtle flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-bold text-text-primary">{n.node_id}</div>
                  <div className="text-[10px] text-text-muted">RSSI: {n.rssi} dBm</div>
                </div>
                <span className="w-2.5 h-2.5 rounded-full bg-hazard-normal"></span>
              </div>
            ))}
          </div>

          <ArrowRight className="w-6 h-6 text-accent-info hidden md:block shrink-0" />

          {/* LoRa Gateway */}
          <div className="bg-bg-surface p-4 rounded-lg border border-accent-info/50 text-center w-full md:w-64">
            <div className="w-9 h-9 rounded bg-accent-info/20 text-accent-info mx-auto mb-2 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <div className="text-xs font-bold text-text-primary">PRAHARI LoRa Gateway</div>
            <div className="text-[11px] font-mono text-accent-info mt-0.5">{network.serial_port} @ {network.baud_rate}</div>
            <div className="text-[10px] text-text-muted mt-1 uppercase">Mode: {network.gateway_mode}</div>
          </div>

          <ArrowRight className="w-6 h-6 text-accent-info hidden md:block shrink-0" />

          {/* Local Backend & WebSocket */}
          <div className="bg-bg-surface p-4 rounded-lg border border-border-subtle text-center w-full md:w-64">
            <div className="w-9 h-9 rounded bg-accent-ai/20 text-accent-ai mx-auto mb-2 flex items-center justify-center">
              <Server className="w-5 h-5" />
            </div>
            <div className="text-xs font-bold text-text-primary">Local Command Engine</div>
            <div className="text-[11px] font-mono text-accent-ai mt-0.5">FastAPI + SQLite WAL</div>
            <div className="text-[10px] text-text-muted mt-1">Clients: {network.websocket_clients} active</div>
          </div>
        </div>
      </div>

      {/* RF Gateway Diagnostics KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Recent Packets Logged</div>
          <div className="text-xl font-mono font-bold text-text-primary mt-1">{network.total_packets_recent}</div>
        </div>
        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Sequence Gaps</div>
          <div className="text-xl font-mono font-bold text-hazard-warning mt-1">{network.sequence_gaps}</div>
        </div>
        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Duplicate Packets</div>
          <div className="text-xl font-mono font-bold text-text-secondary mt-1">{network.duplicate_packets}</div>
        </div>
        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Rejected Frames</div>
          <div className="text-xl font-mono font-bold text-hazard-normal mt-1">{network.rejected_packets}</div>
        </div>
      </div>

      {/* Live Packet Stream Table */}
      <div className="bg-bg-secondary rounded-lg border border-border-subtle overflow-hidden">
        <div className="p-3 bg-bg-surface border-b border-border-subtle flex items-center justify-between">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
            Live Gateway Ingestion Stream
          </h3>
          <span className="text-[11px] font-mono text-accent-info">CRC & Schema Validated</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-bg-surface text-text-muted text-[10px] uppercase tracking-wider border-b border-border-subtle">
              <tr>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Node</th>
                <th className="py-2.5 px-4">Seq</th>
                <th className="py-2.5 px-4">RSSI</th>
                <th className="py-2.5 px-4">Integrity</th>
                <th className="py-2.5 px-4">Gaps</th>
                <th className="py-2.5 px-4">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle font-mono text-[11px]">
              {packets.map((pkt) => (
                <tr key={pkt.id} className="hover:bg-bg-surface/50">
                  <td className="py-2 px-4 text-text-muted">
                    {new Date(pkt.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-2 px-4 font-bold text-accent-info">{pkt.node_id}</td>
                  <td className="py-2 px-4 text-text-primary">#{pkt.sequence}</td>
                  <td className="py-2 px-4 text-text-secondary">{pkt.rssi} dBm</td>
                  <td className="py-2 px-4">
                    {pkt.is_valid ? (
                      <span className="text-hazard-normal flex items-center space-x-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>VALID</span>
                      </span>
                    ) : (
                      <span className="text-hazard-critical flex items-center space-x-1">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>REJECTED</span>
                      </span>
                    )}
                  </td>
                  <td className="py-2 px-4 text-text-muted">{pkt.sequence_gap > 0 ? `+${pkt.sequence_gap}` : '0'}</td>
                  <td className="py-2 px-4 text-[10px] text-text-secondary">{pkt.gateway_source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
