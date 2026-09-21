import React, { useState, useEffect } from 'react';
import { fetchAlerts } from '../services/api';
import { History, ShieldAlert, ArrowRight, Clock, CheckCircle } from 'lucide-react';

export const EventHistoryPage: React.FC = () => {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    fetchAlerts().then(setEvents).catch(console.error);
  }, []);

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto select-text">
      {/* Header */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
          <History className="w-5 h-5 text-purple-400" />
          <span>Chronological Hazard Event Timeline</span>
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Audited lifecycle history of environmental hazard transitions, escalations, and operator mitigations.
        </p>
      </div>

      {/* Timeline List */}
      <div className="relative pl-6 border-l-2 border-border-subtle space-y-6">
        {events.map((evt) => {
          const isCritical = evt.severity === 'CRITICAL';
          const isWarning = evt.severity === 'WARNING';
          const dotColor = isCritical ? 'bg-hazard-critical' : isWarning ? 'bg-hazard-warning' : 'bg-hazard-watch';

          return (
            <div key={evt.id} className="relative group">
              {/* Timeline Marker Dot */}
              <div
                className={`absolute -left-[31px] top-1.5 w-4 h-4 rounded-full border-2 border-bg-primary ${dotColor}`}
              />

              <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle hover:border-accent-info/40 transition-colors space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-accent-info text-xs">{evt.id}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                        isCritical
                          ? 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical'
                          : isWarning
                          ? 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning'
                          : 'bg-hazard-watch/20 text-hazard-watch border-hazard-watch'
                      }`}
                    >
                      {evt.severity} • {evt.hazard}
                    </span>
                    <span className="text-xs font-bold text-text-primary">at {evt.node_id}</span>
                  </div>

                  <span className="text-[11px] font-mono text-text-muted">
                    {new Date(evt.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="text-xs font-semibold text-text-primary">{evt.headline}</div>
                <div className="text-[11px] text-text-secondary leading-relaxed font-mono whitespace-pre-line bg-bg-surface p-2.5 rounded border border-border-subtle">
                  {evt.summary}
                </div>

                <div className="pt-2 flex flex-wrap items-center justify-between gap-2 text-[11px] text-text-muted border-t border-border-subtle">
                  <div>
                    Confidence: <strong className="text-text-primary">{evt.confidence}%</strong> • Risk Score:{' '}
                    <strong className="text-text-primary">{evt.risk_score}%</strong>
                  </div>
                  <div>
                    Status: <span className="font-bold uppercase text-accent-info">{evt.state}</span>
                    {evt.resolved_by && <span> • Resolved by {evt.resolved_by}</span>}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
