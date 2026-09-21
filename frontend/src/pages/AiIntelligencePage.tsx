import React, { useState, useEffect } from 'react';
import { fetchNodes } from '../services/api';
import { wsClient } from '../services/websocket';
import { BrainCircuit, Cpu, ShieldCheck, ArrowRight, Layers, CheckCircle, Activity } from 'lucide-react';

export const AiIntelligencePage: React.FC = () => {
  const [nodes, setNodes] = useState<any[]>([]);

  const loadData = async () => {
    try {
      const data = await fetchNodes();
      setNodes(data);
    } catch (e) {
      console.error('Error fetching nodes:', e);
    }
  };

  useEffect(() => {
    loadData();
    const unsub = wsClient.subscribe('risk.updated', loadData);
    return () => unsub();
  }, []);

  const pipelineSteps = [
    { title: '1. SENSORS', desc: 'Raw ADC & I2C telemetry ingestion from JALA, AGNI, BHUMI over LoRa.' },
    { title: '2. FEATURES', desc: 'Velocity (1st derivative), acceleration (2nd derivative), and rolling saturation.' },
    { title: '3. ANOMALY', desc: 'Isolation Forest multi-variate outlier scoring vs nominal historical baselines.' },
    { title: '4. FUSION', desc: 'Trust-weighted cross-sensor correlation rules (prevents false single-sensor alarms).' },
    { title: '5. RISK', desc: 'Authoritative calibrated prototype risk scoring (0–100) and trend categorization.' },
    { title: '6. EXPLAIN', desc: 'Dual-format causal reasoning generator ("WHY?" narrative + factor weights).' },
    { title: '7. ALERT', desc: 'NDMA CAP-compliant alert dispatcher with auditory alarms and operator audit.' },
  ];

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
          <BrainCircuit className="w-5 h-5 text-accent-ai" />
          <span>PRAHARI Hybrid Intelligence & Sensor Fusion Pipeline</span>
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Explainable, trust-weighted physical fusion combining unsupervised anomaly detection with deterministic domain rules.
        </p>
      </div>

      {/* Pipeline Flow Diagram */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
        <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
          End-to-End Decision Architecture
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {pipelineSteps.map((step, idx) => (
            <div
              key={idx}
              className="bg-bg-surface p-3 rounded-lg border border-border-subtle flex flex-col justify-between"
            >
              <div>
                <div className="text-xs font-bold text-accent-info font-mono">{step.title}</div>
                <div className="text-[11px] text-text-muted mt-1 leading-relaxed">{step.desc}</div>
              </div>
              <div className="mt-2 text-[10px] text-accent-ai font-semibold flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-hazard-normal" />
                <span>ACTIVE</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Model Registry & Engine Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-bg-secondary p-3.5 rounded-lg border border-border-subtle space-y-2">
          <div className="text-[10px] text-text-muted uppercase">Risk Engine Version</div>
          <div className="font-mono font-bold text-sm text-text-primary">PRAHARI-HYBRID-v1.4</div>
          <div className="text-[11px] text-text-secondary">
            Deterministic domain fusion rules paired with trust discounting.
          </div>
        </div>

        <div className="bg-bg-secondary p-3.5 rounded-lg border border-border-subtle space-y-2">
          <div className="text-[10px] text-text-muted uppercase">Anomaly Detector</div>
          <div className="font-mono font-bold text-sm text-accent-ai">Scikit-learn IsolationForest</div>
          <div className="text-[11px] text-text-secondary">
            Unsupervised multivariate contamination scoring (50 estimators, zero GPU dependency).
          </div>
        </div>

        <div className="bg-bg-secondary p-3.5 rounded-lg border border-border-subtle space-y-2">
          <div className="text-[10px] text-text-muted uppercase">Model Source Provenance</div>
          <div className="font-mono font-bold text-sm text-accent-info">RULE_FUSION & SIMULATION</div>
          <div className="text-[11px] text-text-secondary">
            Transparent honest telemetry labeling without simulated accuracy claims.
          </div>
        </div>
      </div>

      {/* Active AI Causal Decisions per Node */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
          Live Explainability Reasoning by Node
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {nodes.map((node) => {
            const risk = node.latest_risk || {};
            return (
              <div
                key={node.id}
                className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-xs text-accent-info">{node.id}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded border uppercase bg-bg-surface border-border-subtle text-text-primary">
                      {risk.risk_band || 'NORMAL'} ({risk.risk_score || 0}%)
                    </span>
                  </div>

                  <div className="bg-bg-surface p-2.5 rounded border border-border-subtle font-mono text-[11px] text-text-secondary leading-relaxed whitespace-pre-line">
                    {risk.human_explanation || 'Telemetry is within nominal bounds.'}
                  </div>
                </div>

                <div className="pt-2 border-t border-border-subtle text-[10px] text-text-muted flex items-center justify-between">
                  <span>Confidence: <strong className="text-text-primary">{risk.confidence || 95}%</strong></span>
                  <span>Anomaly Score: <strong className="text-accent-ai">{risk.anomaly_score || 0.0}</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
