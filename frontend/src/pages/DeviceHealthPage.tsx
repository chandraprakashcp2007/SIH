import React, { useState, useEffect } from 'react';
import { fetchNodes } from '../services/api';
import { wsClient } from '../services/websocket';
import { Activity, Battery, Radio, Wrench, ShieldCheck, CheckCircle2, AlertTriangle, Cpu } from 'lucide-react';

export const DeviceHealthPage: React.FC = () => {
  const [nodes, setNodes] = useState<any[]>([]);

  const loadHealth = async () => {
    try {
      const data = await fetchNodes();
      setNodes(data);
    } catch (err) {
      console.error('Error fetching device health:', err);
    }
  };

  useEffect(() => {
    loadHealth();
    const unsub = wsClient.subscribe('node.status_changed', loadHealth);
    return () => unsub();
  }, []);

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
          <Activity className="w-5 h-5 text-hazard-normal" />
          <span>Device Health & Hardware Calibration Diagnostics</span>
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Power reserves, photovoltaic charging, sensor drift, and preventative maintenance alerts.
        </p>
      </div>

      {/* Node Health Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {nodes.map((n) => {
          const needsMaintenance = n.battery_pct < 20 || n.packet_loss_pct > 15 || n.status === 'OFFLINE';
          const trustScores = n.latest_risk?.sensor_trust || {};
          const minTrust = Math.min(...(Object.values(trustScores) as number[]), 100);

          return (
            <div
              key={n.id}
              className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-4 flex flex-col justify-between"
            >
              <div>
                {/* Node Title & Status */}
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="text-xs font-bold text-text-primary">{n.id}</h3>
                    <p className="text-[11px] text-text-muted">{n.name}</p>
                  </div>

                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                      needsMaintenance
                        ? 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical'
                        : 'bg-hazard-normal/20 text-hazard-normal border-hazard-normal'
                    }`}
                  >
                    {needsMaintenance ? 'MAINTENANCE REQUIRED' : 'HEALTHY'}
                  </span>
                </div>

                {/* Specs Grid */}
                <div className="grid grid-cols-2 gap-2 bg-bg-surface p-2.5 rounded border border-border-subtle text-xs my-3">
                  <div>
                    <div className="text-[10px] text-text-muted">Firmware Rev</div>
                    <div className="font-mono font-semibold text-text-primary">{n.firmware_version}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-text-muted">Hardware ASIC</div>
                    <div className="font-mono font-semibold text-text-primary">{n.hardware_rev}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-text-muted">Battery & Solar</div>
                    <div className="font-mono font-semibold text-text-primary">
                      {n.battery_pct?.toFixed(0)}% ({n.solar_voltage?.toFixed(2)}V)
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-text-muted">Min Sensor Trust</div>
                    <div className="font-mono font-semibold text-accent-info">{minTrust}%</div>
                  </div>
                </div>

                {/* Detailed Sensor Trust Ratings */}
                <div className="space-y-1.5 pt-1">
                  <div className="text-[10px] uppercase font-semibold text-text-muted tracking-wider">
                    Transducer Reliability & Trust
                  </div>
                  {Object.entries(trustScores).map(([sensor, score]: [string, any]) => (
                    <div key={sensor} className="flex items-center justify-between text-[11px]">
                      <span className="text-text-secondary truncate max-w-[140px]">{sensor}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 h-1.5 bg-bg-surface rounded-full overflow-hidden">
                          <div
                            className={`h-full ${score < 50 ? 'bg-hazard-critical' : score < 80 ? 'bg-hazard-warning' : 'bg-hazard-normal'}`}
                            style={{ width: `${score}%` }}
                          />
                        </div>
                        <span className="font-mono font-semibold text-text-primary">{score}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Maintenance Advice */}
              <div className="p-2.5 rounded bg-bg-surface border border-border-subtle text-[11px] text-text-secondary">
                {needsMaintenance ? (
                  <div className="text-hazard-critical flex items-center space-x-1.5">
                    <Wrench className="w-3.5 h-3.5 shrink-0" />
                    <span>Schedule field team to inspect solar charging circuit or antenna.</span>
                  </div>
                ) : (
                  <div className="text-hazard-normal flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                    <span>Nominal operation. Next scheduled sensor recalibration in 45 days.</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
