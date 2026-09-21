import React, { useState, useEffect } from 'react';
import { fetchAlerts, acknowledgeAlert, resolveAlert } from '../services/api';
import { wsClient } from '../services/websocket';
import { AlertTriangle, ShieldCheck, Check, Clock, Filter, Eye, X, CheckCircle } from 'lucide-react';

export const AlertCentre: React.FC = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);
  const [stateFilter, setStateFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [resolveModalOpen, setResolveModalOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');

  const loadAlerts = async () => {
    try {
      const data = await fetchAlerts();
      setAlerts(data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    }
  };

  useEffect(() => {
    loadAlerts();
    const unsub1 = wsClient.subscribe('alert.created', loadAlerts);
    const unsub2 = wsClient.subscribe('alert.acknowledged', loadAlerts);
    const unsub3 = wsClient.subscribe('alert.resolved', loadAlerts);
    const unsub4 = wsClient.subscribe('alert.updated', loadAlerts);

    return () => {
      unsub1();
      unsub2();
      unsub3();
      unsub4();
    };
  }, []);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await acknowledgeAlert(alertId);
      loadAlerts();
      if (selectedAlert?.id === alertId) {
        setSelectedAlert((prev: any) => ({ ...prev, state: 'ACKNOWLEDGED' }));
      }
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const handleResolveSubmit = async () => {
    if (!selectedAlert || !resolutionNotes.trim()) return;
    try {
      await resolveAlert(selectedAlert.id, resolutionNotes);
      setResolveModalOpen(false);
      setResolutionNotes('');
      loadAlerts();
      setSelectedAlert(null);
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    }
  };

  const filteredAlerts = alerts.filter((a) => {
    if (stateFilter !== 'ALL' && a.state !== stateFilter) return false;
    if (severityFilter !== 'ALL' && a.severity !== severityFilter) return false;
    return true;
  });

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <div>
          <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-hazard-warning" />
            <span>Incident Alert Command & Triage Centre</span>
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Operational triage adhering to NDMA Common Alerting Protocol (CAP) lifecycle standards.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-2 text-xs">
          <select
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-secondary focus:outline-none"
          >
            <option value="ALL">All States</option>
            <option value="NEW">New (Unacknowledged)</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="MONITORING">Monitoring</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-secondary focus:outline-none"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="WARNING">Warning</option>
            <option value="WATCH">Watch</option>
          </select>
        </div>
      </div>

      {/* Incident Table */}
      <div className="bg-bg-secondary rounded-lg border border-border-subtle overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-bg-surface text-text-muted text-[11px] uppercase tracking-wider border-b border-border-subtle">
              <tr>
                <th className="py-3 px-4">Severity / Hazard</th>
                <th className="py-3 px-4">Alert ID</th>
                <th className="py-3 px-4">Origin Node</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Detection Time</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Lifecycle State</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-text-muted">
                    No incident records matching the selected filters.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alert) => {
                  const isCritical = alert.severity === 'CRITICAL';
                  const isWarning = alert.severity === 'WARNING';
                  const sevBadge = isCritical
                    ? 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical/40'
                    : isWarning
                    ? 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning/40'
                    : 'bg-hazard-watch/20 text-hazard-watch border-hazard-watch/40';

                  return (
                    <tr
                      key={alert.id}
                      onClick={() => setSelectedAlert(alert)}
                      className="hover:bg-bg-surface/50 cursor-pointer transition-colors"
                    >
                      <td className="py-3 px-4">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${sevBadge}`}>
                          {alert.severity} • {alert.hazard}
                        </span>
                      </td>

                      <td className="py-3 px-4 font-mono font-bold text-accent-info">
                        {alert.id}
                      </td>

                      <td className="py-3 px-4 font-bold text-text-primary">
                        {alert.node_id}
                      </td>

                      <td className="py-3 px-4 text-text-secondary truncate max-w-[180px]">
                        {alert.location_name}
                      </td>

                      <td className="py-3 px-4 font-mono text-[11px] text-text-muted">
                        {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </td>

                      <td className="py-3 px-4 font-mono font-semibold">
                        {alert.confidence.toFixed(0)}%
                      </td>

                      <td className="py-3 px-4">
                        <span
                          className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded uppercase ${
                            alert.state === 'NEW'
                              ? 'bg-amber-500/20 text-amber-300'
                              : alert.state === 'ACKNOWLEDGED'
                              ? 'bg-accent-info/20 text-accent-info'
                              : 'bg-hazard-normal/20 text-hazard-normal'
                          }`}
                        >
                          {alert.state}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end space-x-1.5">
                          {alert.state === 'NEW' && (
                            <button
                              onClick={() => handleAcknowledge(alert.id)}
                              className="px-2.5 py-1 bg-accent-info/20 hover:bg-accent-info/30 text-accent-info text-[10px] font-bold rounded border border-accent-info/40 transition-colors"
                            >
                              ACKNOWLEDGE
                            </button>
                          )}
                          {alert.state === 'ACKNOWLEDGED' && (
                            <button
                              onClick={() => {
                                setSelectedAlert(alert);
                                setResolveModalOpen(true);
                              }}
                              className="px-2.5 py-1 bg-hazard-normal/20 hover:bg-hazard-normal/30 text-hazard-normal text-[10px] font-bold rounded border border-hazard-normal/40 transition-colors"
                            >
                              RESOLVE
                            </button>
                          )}
                          <button
                            onClick={() => setSelectedAlert(alert)}
                            className="p-1 rounded text-text-muted hover:text-text-primary hover:bg-bg-surface"
                            title="View Incident Evidence"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Detail Modal / Drawer */}
      {selectedAlert && !resolveModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-bg-secondary border border-border-subtle rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden select-text">
            {/* Modal Header */}
            <div className="p-4 bg-bg-surface border-b border-border-subtle flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-accent-info text-sm">{selectedAlert.id}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded border uppercase bg-hazard-critical/20 text-hazard-critical border-hazard-critical/40">
                    {selectedAlert.severity} • {selectedAlert.hazard}
                  </span>
                </div>
                <h2 className="text-sm font-bold text-text-primary mt-1">{selectedAlert.headline}</h2>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="p-1 rounded text-text-muted hover:text-text-primary hover:bg-bg-elevated"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-4 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-bg-surface p-2.5 rounded border border-border-subtle text-center">
                <div>
                  <div className="text-[10px] text-text-muted">Origin Node</div>
                  <div className="font-bold text-text-primary">{selectedAlert.node_id}</div>
                </div>
                <div>
                  <div className="text-[10px] text-text-muted">Risk Score</div>
                  <div className="font-bold text-hazard-critical">{selectedAlert.risk_score}%</div>
                </div>
                <div>
                  <div className="text-[10px] text-text-muted">Confidence</div>
                  <div className="font-bold text-text-primary">{selectedAlert.confidence}%</div>
                </div>
                <div>
                  <div className="text-[10px] text-text-muted">State</div>
                  <div className="font-bold text-accent-info uppercase">{selectedAlert.state}</div>
                </div>
              </div>

              <div>
                <h4 className="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-1">
                  Incident Summary & Causal Evidence
                </h4>
                <div className="bg-bg-surface p-3 rounded border border-border-subtle font-mono text-[11px] leading-relaxed whitespace-pre-line text-text-secondary">
                  {selectedAlert.summary}
                </div>
              </div>

              <div>
                <h4 className="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-1">
                  Recommended Operational Protocol
                </h4>
                <div className="bg-bg-surface p-3 rounded border border-border-subtle text-text-primary font-medium">
                  {selectedAlert.action_recommended}
                </div>
              </div>

              {selectedAlert.resolution_notes && (
                <div>
                  <h4 className="text-[11px] font-semibold text-hazard-normal uppercase tracking-wider mb-1">
                    Resolution Documentation
                  </h4>
                  <div className="bg-bg-surface p-3 rounded border border-hazard-normal/30 font-mono text-[11px] text-text-secondary">
                    {selectedAlert.resolution_notes}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-3 bg-bg-surface border-t border-border-subtle flex items-center justify-between">
              <span className="text-[11px] text-text-muted">
                Detected: {new Date(selectedAlert.created_at).toLocaleString()}
              </span>
              <div className="flex items-center space-x-2">
                {selectedAlert.state === 'NEW' && (
                  <button
                    onClick={() => handleAcknowledge(selectedAlert.id)}
                    className="px-3 py-1.5 bg-accent-info text-bg-primary font-bold rounded text-xs hover:bg-cyan-300 transition-colors"
                  >
                    Acknowledge Incident
                  </button>
                )}
                {selectedAlert.state === 'ACKNOWLEDGED' && (
                  <button
                    onClick={() => setResolveModalOpen(true)}
                    className="px-3 py-1.5 bg-hazard-normal text-bg-primary font-bold rounded text-xs hover:bg-emerald-400 transition-colors"
                  >
                    Resolve Incident
                  </button>
                )}
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="px-3 py-1.5 bg-bg-secondary text-text-secondary hover:text-text-primary rounded text-xs border border-border-subtle"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Resolve Incident Dialog */}
      {resolveModalOpen && selectedAlert && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-bg-secondary border border-border-subtle rounded-xl max-w-md w-full p-4 shadow-2xl space-y-3">
            <h3 className="text-sm font-bold text-text-primary flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-hazard-normal" />
              <span>Resolve Incident {selectedAlert.id}</span>
            </h3>
            <p className="text-xs text-text-muted">
              Document field verification actions taken before marking this incident as RESOLVED.
            </p>

            <textarea
              rows={3}
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              placeholder="e.g. Field ranger dispatched to Similipal Ridge; confirmed controlled leaf burning; fire hazard mitigated."
              className="w-full bg-bg-surface border border-border-subtle rounded p-2.5 text-xs text-text-primary focus:outline-none focus:border-hazard-normal"
            />

            <div className="flex justify-end space-x-2 pt-2 border-t border-border-subtle">
              <button
                onClick={() => setResolveModalOpen(false)}
                className="px-3 py-1.5 bg-bg-surface hover:bg-bg-elevated text-text-secondary text-xs rounded border border-border-subtle"
              >
                Cancel
              </button>
              <button
                onClick={handleResolveSubmit}
                disabled={!resolutionNotes.trim()}
                className="px-3 py-1.5 bg-hazard-normal hover:bg-emerald-400 text-bg-primary font-bold text-xs rounded disabled:opacity-50"
              >
                Submit Resolution
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
