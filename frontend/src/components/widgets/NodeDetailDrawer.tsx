import React from 'react';
import { useNavigate } from 'react-router-dom';
import { X, ExternalLink, ShieldCheck, Activity, Battery, Radio, AlertTriangle } from 'lucide-react';

interface NodeDetailDrawerProps {
  node: any | null;
  onClose: () => void;
}

export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({ node, onClose }) => {
  const navigate = useNavigate();

  if (!node) return null;

  const risk = node.latest_risk || {};
  const metrics = node.latest_metrics || {};
  const riskBand = risk.risk_band || 'NORMAL';
  const riskScore = risk.risk_score || 0;

  let badgeColor = 'bg-hazard-normal/20 text-hazard-normal border-hazard-normal/40';
  if (riskBand === 'CRITICAL') badgeColor = 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical/40';
  else if (riskBand === 'WARNING') badgeColor = 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning/40';
  else if (riskBand === 'WATCH') badgeColor = 'bg-hazard-watch/20 text-hazard-watch border-hazard-watch/40';

  return (
    <div className="fixed inset-y-0 right-0 w-96 max-w-full bg-bg-secondary border-l border-border-subtle shadow-2xl z-50 flex flex-col select-text">
      {/* Drawer Header */}
      <div className="p-4 bg-bg-surface border-b border-border-subtle flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-bold text-text-primary">{node.id}</h2>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${badgeColor}`}>
              {riskBand} ({riskScore}%)
            </span>
          </div>
          <p className="text-xs text-text-muted mt-0.5">{node.name}</p>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded text-text-muted hover:text-text-primary hover:bg-bg-elevated transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {/* Hardware Status Strip */}
        <div className="grid grid-cols-3 gap-2 bg-bg-surface p-2.5 rounded border border-border-subtle text-center">
          <div>
            <div className="text-[10px] text-text-muted flex items-center justify-center space-x-1">
              <Battery className="w-3 h-3 text-hazard-normal" />
              <span>Battery</span>
            </div>
            <div className="font-mono font-bold text-text-primary mt-0.5">{node.battery_pct?.toFixed(0) ?? 95}%</div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted flex items-center justify-center space-x-1">
              <Radio className="w-3 h-3 text-accent-info" />
              <span>LoRa RSSI</span>
            </div>
            <div className="font-mono font-bold text-text-primary mt-0.5">{node.signal_rssi ?? -78} dBm</div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted flex items-center justify-center space-x-1">
              <Activity className="w-3 h-3 text-accent-ai" />
              <span>Packet Loss</span>
            </div>
            <div className="font-mono font-bold text-text-primary mt-0.5">{node.packet_loss_pct?.toFixed(1) ?? 0.0}%</div>
          </div>
        </div>

        {/* Explainable AI Narrative */}
        <div className="bg-bg-surface p-3 rounded border border-border-subtle">
          <div className="flex items-center space-x-1.5 text-accent-ai font-semibold mb-2">
            <ShieldCheck className="w-4 h-4" />
            <span className="text-[11px] uppercase tracking-wider">Explainable AI Analysis</span>
          </div>
          <div className="text-text-secondary leading-relaxed whitespace-pre-line font-mono text-[11px] bg-bg-secondary p-2.5 rounded border border-border-subtle">
            {risk.human_explanation || 'All parameters conform to nominal baselines.'}
          </div>
        </div>

        {/* Dynamic Sensor Trust Ratings */}
        {risk.sensor_trust && Object.keys(risk.sensor_trust).length > 0 && (
          <div className="bg-bg-surface p-3 rounded border border-border-subtle">
            <h4 className="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-2">
              Sensor Trust Scores
            </h4>
            <div className="space-y-2">
              {Object.entries(risk.sensor_trust).map(([sensor, score]: [string, any]) => (
                <div key={sensor} className="flex items-center justify-between text-[11px]">
                  <span className="text-text-muted font-mono">{sensor}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 h-1.5 bg-bg-secondary rounded-full overflow-hidden">
                      <div
                        className={`h-full ${score < 50 ? 'bg-hazard-critical' : score < 80 ? 'bg-hazard-warning' : 'bg-hazard-normal'}`}
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <span className="font-mono font-bold text-text-primary">{score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Telemetry Metric Readouts */}
        <div className="bg-bg-surface p-3 rounded border border-border-subtle">
          <h4 className="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-2">
            Live Telemetry Metrics
          </h4>
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            {Object.entries(metrics).map(([key, val]: [string, any]) => (
              <div key={key} className="bg-bg-secondary p-1.5 rounded border border-border-subtle">
                <div className="text-[10px] text-text-muted truncate">{key}</div>
                <div className="font-mono font-semibold text-text-primary truncate">
                  {typeof val === 'number' ? val.toFixed(2) : String(val)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Drawer Action Footer */}
      <div className="p-3 bg-bg-surface border-t border-border-subtle flex items-center justify-between">
        <span className="text-[10px] text-text-muted">Location: {node.location_name}</span>
        <button
          onClick={() => navigate(`/nodes/${node.id}`)}
          className="flex items-center space-x-1.5 bg-accent-info hover:bg-cyan-400 text-bg-primary font-bold px-3 py-1.5 rounded text-xs transition-colors"
        >
          <span>Open Full Node View</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
