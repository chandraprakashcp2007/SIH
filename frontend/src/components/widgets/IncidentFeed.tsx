import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, Clock, ShieldAlert, Check, ArrowRight } from 'lucide-react';
import { acknowledgeAlert, resolveAlert } from '../../services/api';

interface AlertItem {
  id: string;
  severity: string;
  hazard: string;
  node_id: string;
  location_name: string;
  created_at: string;
  confidence: number;
  risk_score: number;
  headline: string;
  summary: string;
  action_recommended: string;
  state: string;
}

interface IncidentFeedProps {
  alerts: AlertItem[];
  onRefresh: () => void;
  onSelectAlert?: (alert: AlertItem) => void;
}

export const IncidentFeed: React.FC<IncidentFeedProps> = ({ alerts, onRefresh, onSelectAlert }) => {
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [resolutionText, setResolutionText] = useState<string>('');

  const handleAcknowledge = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await acknowledgeAlert(id);
      onRefresh();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const handleConfirmResolve = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!resolutionText.trim()) return;
    try {
      await resolveAlert(id, resolutionText);
      setResolvingId(null);
      setResolutionText('');
      onRefresh();
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    }
  };

  const activeAlerts = alerts.filter((a) => a.state !== 'RESOLVED');

  return (
    <div className="h-full flex flex-col bg-bg-secondary/95 rounded-xl border border-border-subtle overflow-hidden shadow-[0_18px_50px_rgba(0,0,0,0.22)]">
      {/* Header */}
      <div className="p-3 bg-gradient-to-r from-bg-surface to-bg-secondary border-b border-border-subtle flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-hazard-warning" />
          <h3 className="text-xs font-bold tracking-wider uppercase text-text-primary">
            Active Incident Feed
          </h3>
        </div>
        <span className="text-[11px] font-mono bg-bg-elevated px-2 py-0.5 rounded text-text-secondary border border-border-subtle">
          {activeAlerts.length} QUEUED
        </span>
      </div>

      {/* Feed List */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-2">
        {activeAlerts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-text-muted">
            <CheckCircle className="w-10 h-10 text-hazard-normal/60 mb-2" />
            <p className="text-xs font-medium text-text-secondary">All Monitored Zones Nominal</p>
            <p className="text-[11px] mt-1 text-text-muted">No active emergency alerts detected.</p>
          </div>
        ) : (
          activeAlerts.map((alert) => {
            const isCritical = alert.severity === 'CRITICAL';
            const isWarning = alert.severity === 'WARNING';
            const badgeColor = isCritical
              ? 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical'
              : isWarning
              ? 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning'
              : 'bg-hazard-watch/20 text-hazard-watch border-hazard-watch';

            return (
              <div
                key={alert.id}
                onClick={() => onSelectAlert && onSelectAlert(alert)}
                className={`p-3 rounded-md bg-bg-surface border transition-all cursor-pointer hover:border-accent-info/50 ${
                  isCritical ? 'border-hazard-critical/40 pulse-critical' : 'border-border-subtle'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${badgeColor}`}>
                    {alert.severity} • {alert.hazard}
                  </span>
                  <span className="text-[10px] font-mono text-text-muted">
                    {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                <div className="font-semibold text-xs text-text-primary line-clamp-1 mb-1">
                  {alert.headline}
                </div>

                <div className="text-[11px] text-text-secondary line-clamp-2 mb-2 leading-relaxed">
                  {alert.summary}
                </div>

                {/* State & Action Controls */}
                <div className="flex items-center justify-between pt-2 border-t border-border-subtle text-[11px]">
                  <div className="flex items-center space-x-2 text-text-muted">
                    <span>Conf: <strong className="text-text-primary">{alert.confidence.toFixed(0)}%</strong></span>
                    <span>•</span>
                    <span className="uppercase text-[10px] font-semibold text-accent-info">{alert.state}</span>
                  </div>

                  <div className="flex items-center space-x-1.5" onClick={(e) => e.stopPropagation()}>
                    {alert.state === 'NEW' && (
                      <button
                        onClick={(e) => handleAcknowledge(alert.id, e)}
                        className="px-2 py-1 bg-accent-info/20 hover:bg-accent-info/30 text-accent-info text-[10px] font-semibold rounded border border-accent-info/40 transition-colors"
                      >
                        ACKNOWLEDGE
                      </button>
                    )}

                    {alert.state === 'ACKNOWLEDGED' && resolvingId !== alert.id && (
                      <button
                        onClick={() => setResolvingId(alert.id)}
                        className="px-2 py-1 bg-hazard-normal/20 hover:bg-hazard-normal/30 text-hazard-normal text-[10px] font-semibold rounded border border-hazard-normal/40 transition-colors"
                      >
                        RESOLVE
                      </button>
                    )}
                  </div>
                </div>

                {/* Quick Resolve Input if open */}
                {resolvingId === alert.id && (
                  <div className="mt-2 pt-2 border-t border-border-subtle" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      placeholder="Resolution notes (e.g., Sluice gate opened)..."
                      value={resolutionText}
                      onChange={(e) => setResolutionText(e.target.value)}
                      className="w-full bg-bg-secondary border border-border-subtle rounded px-2 py-1 text-xs text-text-primary focus:outline-none focus:border-hazard-normal mb-1.5"
                    />
                    <div className="flex justify-end space-x-1.5">
                      <button
                        onClick={() => setResolvingId(null)}
                        className="px-2 py-0.5 text-[10px] text-text-muted hover:text-text-primary"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={(e) => handleConfirmResolve(alert.id, e)}
                        disabled={!resolutionText.trim()}
                        className="px-2.5 py-0.5 text-[10px] bg-hazard-normal text-bg-primary font-bold rounded disabled:opacity-50"
                      >
                        Confirm Resolve
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
