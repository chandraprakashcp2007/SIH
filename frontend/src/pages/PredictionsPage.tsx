import React, { useState, useEffect } from 'react';
import { fetchPredictions } from '../services/api';
import { wsClient } from '../services/websocket';
import { TrendingUp, Clock, AlertCircle, ShieldCheck, ArrowUpRight, Droplets, Flame, Mountain } from 'lucide-react';

export const PredictionsPage: React.FC = () => {
  const [predictions, setPredictions] = useState<any[]>([]);

  const loadPredictions = async () => {
    try {
      const data = await fetchPredictions();
      setPredictions(data);
    } catch (err) {
      console.error('Error fetching predictions:', err);
    }
  };

  useEffect(() => {
    loadPredictions();
    const unsub = wsClient.subscribe('risk.updated', loadPredictions);
    return () => unsub();
  }, []);

  const getHazardIcon = (hazard: string) => {
    if (hazard === 'FLOOD') return <Droplets className="w-5 h-5 text-accent-info" />;
    if (hazard === 'FIRE') return <Flame className="w-5 h-5 text-hazard-warning" />;
    return <Mountain className="w-5 h-5 text-hazard-normal" />;
  };

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-accent-ai" />
          <span>Proactive Hazard Predictions & Trend Projections</span>
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Kinematic trajectory forecasting and honest time-to-threshold extrapolations without false precision.
        </p>
      </div>

      {/* Prediction Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {predictions.map((p) => {
          const isInsufficient = p.status === 'INSUFFICIENT DATA';
          return (
            <div
              key={p.node_id}
              className="bg-bg-secondary p-4 rounded-lg border border-border-subtle flex flex-col justify-between space-y-4"
            >
              {/* Card Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-9 h-9 rounded bg-bg-surface flex items-center justify-center border border-border-subtle">
                    {getHazardIcon(p.hazard)}
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-text-primary">{p.node_id}</h3>
                    <p className="text-[11px] text-text-muted truncate max-w-[160px]">{p.node_name}</p>
                  </div>
                </div>

                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                    isInsufficient
                      ? 'bg-bg-surface text-text-muted border-border-subtle'
                      : 'bg-accent-ai/20 text-accent-ai border-accent-ai/40'
                  }`}
                >
                  {p.hazard}
                </span>
              </div>

              {/* Status / Forecast */}
              {isInsufficient ? (
                <div className="bg-bg-surface p-6 rounded border border-dashed border-border-subtle text-center">
                  <AlertCircle className="w-6 h-6 text-text-muted mx-auto mb-1.5" />
                  <div className="font-mono font-bold text-xs text-text-muted uppercase">
                    INSUFFICIENT DATA
                  </div>
                  <div className="text-[10px] text-text-muted mt-1">
                    Awaiting additional sequential telemetry frames to calibrate derivative trend slopes.
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Current vs Projected Change */}
                  <div className="grid grid-cols-2 gap-2 bg-bg-surface p-2.5 rounded border border-border-subtle text-center">
                    <div>
                      <div className="text-[10px] text-text-muted">Current Risk</div>
                      <div className="font-mono font-bold text-sm text-text-primary mt-0.5">
                        {p.current_risk?.toFixed(0) ?? 0}%
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-text-muted">5-Min Delta</div>
                      <div
                        className={`font-mono font-bold text-sm mt-0.5 ${
                          p.projected_5min_change > 0 ? 'text-hazard-warning' : 'text-hazard-normal'
                        }`}
                      >
                        {p.projected_5min_change > 0 ? `+${p.projected_5min_change}%` : `${p.projected_5min_change}%`}
                      </div>
                    </div>
                  </div>

                  {/* Threshold Crossing Window */}
                  <div className="bg-bg-surface p-3 rounded border border-border-subtle">
                    <div className="text-[10px] text-text-muted flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-accent-info" />
                      <span>Projected Threshold Crossing:</span>
                    </div>
                    <div className="text-sm font-bold font-mono text-accent-info mt-1">
                      {p.threshold_crossing_window}
                    </div>
                  </div>

                  {/* Meta Indicators */}
                  <div className="grid grid-cols-2 gap-2 text-[11px] text-text-secondary">
                    <div className="bg-bg-surface p-2 rounded border border-border-subtle">
                      <span className="text-text-muted text-[10px]">Trend Trajectory:</span>
                      <div className="font-bold text-text-primary mt-0.5">{p.trend_direction}</div>
                    </div>
                    <div className="bg-bg-surface p-2 rounded border border-border-subtle">
                      <span className="text-text-muted text-[10px]">Confidence:</span>
                      <div className="font-bold text-text-primary mt-0.5">{p.prediction_confidence}%</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Model Source Footer */}
              <div className="text-[10px] text-text-muted flex items-center justify-between border-t border-border-subtle pt-2">
                <span>Model: <strong className="text-text-secondary">{p.model_source}</strong></span>
                <span>{p.last_execution ? new Date(p.last_execution).toLocaleTimeString() : 'Awaiting'}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
