import React, { useState, useEffect } from 'react';
import { fetchAnalytics } from '../services/api';
import { BarChart2, Radio, CheckCircle, Activity, AlertTriangle, ShieldCheck, Clock } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    fetchAnalytics().then(setAnalytics).catch(console.error);
  }, []);

  if (!analytics) {
    return <div className="p-8 text-center text-text-muted text-xs">Loading operational analytics...</div>;
  }

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
          <BarChart2 className="w-5 h-5 text-accent-info" />
          <span>Operational Analytics & Fleet Reliability</span>
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Quantifiable telemetry processing benchmarks, RF packet delivery ratios, and incident triage velocity.
        </p>
      </div>

      {/* Top Benchmark KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Fleet Uptime</div>
          <div className="text-xl font-mono font-bold text-hazard-normal mt-1">{analytics.fleet_uptime_pct}%</div>
          <div className="text-[10px] text-text-muted mt-1">Local edge continuous</div>
        </div>

        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Packet Delivery</div>
          <div className="text-xl font-mono font-bold text-accent-info mt-1">
            {analytics.packet_delivery_rate_pct}%
          </div>
          <div className="text-[10px] text-text-muted mt-1">LoRa RF link integrity</div>
        </div>

        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Avg Ack Time</div>
          <div className="text-xl font-mono font-bold text-purple-400 mt-1">
            {analytics.average_ack_time_sec}s
          </div>
          <div className="text-[10px] text-text-muted mt-1">Operator triage velocity</div>
        </div>

        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle">
          <div className="text-[10px] text-text-muted uppercase">Avg RF Signal</div>
          <div className="text-xl font-mono font-bold text-text-primary mt-1">
            {analytics.average_rssi_dbm} dBm
          </div>
          <div className="text-[10px] text-text-muted mt-1">Sub-GHz RSSI health</div>
        </div>
      </div>

      {/* Distribution Grids */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Alerts by Hazard */}
        <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
            Incident Distribution by Hazard Category
          </h3>
          <div className="space-y-2 text-xs">
            {Object.entries(analytics.alerts_by_hazard || {}).map(([hazard, count]: [string, any]) => (
              <div key={hazard} className="space-y-1">
                <div className="flex justify-between text-[11px]">
                  <span className="text-text-secondary">{hazard}</span>
                  <span className="font-mono font-bold text-text-primary">{count} incidents</span>
                </div>
                <div className="w-full h-2 bg-bg-surface rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      hazard === 'FLOOD' ? 'bg-accent-info' : hazard === 'FIRE' ? 'bg-hazard-warning' : 'bg-hazard-normal'
                    }`}
                    style={{ width: `${Math.min(100, (count / Math.max(1, analytics.total_alerts || 1)) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alerts by Severity */}
        <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
            Incident Classification by Severity Band
          </h3>
          <div className="space-y-2 text-xs">
            {Object.entries(analytics.alerts_by_severity || {}).map(([sev, count]: [string, any]) => (
              <div key={sev} className="space-y-1">
                <div className="flex justify-between text-[11px]">
                  <span className="text-text-secondary">{sev}</span>
                  <span className="font-mono font-bold text-text-primary">{count} events</span>
                </div>
                <div className="w-full h-2 bg-bg-surface rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      sev === 'CRITICAL' ? 'bg-hazard-critical' : sev === 'WARNING' ? 'bg-hazard-warning' : 'bg-hazard-watch'
                    }`}
                    style={{ width: `${Math.min(100, (count / Math.max(1, analytics.total_alerts || 1)) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Weekly Activity Histogram Table */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
        <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
          7-Day Hazard Observation & Triage Histogram
        </h3>
        <div className="grid grid-cols-7 gap-2 text-center text-xs">
          {analytics.daily_event_counts?.map((d: any, i: number) => (
            <div key={i} className="bg-bg-surface p-3 rounded border border-border-subtle flex flex-col justify-end h-28">
              <div
                className="w-full bg-accent-info/30 rounded-t mb-2 transition-all"
                style={{ height: `${Math.min(100, d.count * 12 + 10)}%` }}
              />
              <div className="font-mono font-bold text-text-primary">{d.count}</div>
              <div className="text-[10px] text-text-muted mt-0.5">{d.day}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
