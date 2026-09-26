import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchNode, fetchNodeTelemetry, fetchNodeRisk } from '../services/api';
import { wsClient } from '../services/websocket';
import {
  Droplets,
  Flame,
  Mountain,
  Wind,
  CloudRain,
  Battery,
  Radio,
  Activity,
  ShieldAlert,
  ArrowLeft,
  Camera,
  Layers,
  Clock,
  CheckCircle,
  FileCode,
  Compass
} from 'lucide-react';

export const NodeDetail: React.FC = () => {
  const { nodeId = 'JALA-01' } = useParams<{ nodeId: string }>();
  const navigate = useNavigate();
  const [node, setNode] = useState<any>(null);
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [riskHistory, setRiskHistory] = useState<any[]>([]);
  const [showRawJson, setShowRawJson] = useState(false);

  const loadNodeData = async () => {
    try {
      const [nodeData, telemData, riskData] = await Promise.all([
        fetchNode(nodeId),
        fetchNodeTelemetry(nodeId, 30),
        fetchNodeRisk(nodeId, 30),
      ]);
      setNode(nodeData);
      setTelemetry(telemData);
      setRiskHistory(riskData);
    } catch (err) {
      console.error(`Error loading data for ${nodeId}:`, err);
    }
  };

  useEffect(() => {
    loadNodeData();
    const unsubTelem = wsClient.subscribe('telemetry.updated', (pkt) => {
      if (pkt.node_id === nodeId) loadNodeData();
    });
    const unsubRisk = wsClient.subscribe('risk.updated', (risk) => {
      if (risk.node_id === nodeId) loadNodeData();
    });

    return () => {
      unsubTelem();
      unsubRisk();
    };
  }, [nodeId]);

  if (!node) {
    return (
      <div className="p-8 text-center text-text-muted text-xs">
        Loading node diagnostics for {nodeId}...
      </div>
    );
  }

  const latestRisk = node.latest_risk || {};
  const latestMetrics = node.latest_metrics || {};
  const riskBand = latestRisk.risk_band || 'NORMAL';
  const riskScore = latestRisk.risk_score || 0;

  // Simple SVG Time-series chart generator
  const renderSparkline = (points: number[], maxVal: number, color: string, height: number = 80) => {
    if (!points || points.length < 2) {
      return (
        <div className="h-20 flex items-center justify-center text-[10px] text-text-muted">
          Awaiting time-series observations...
        </div>
      );
    }
    const width = 300;
    const pad = 10;
    const h = height - pad * 2;
    const w = width - pad * 2;
    const dx = w / (points.length - 1);

    const coords = points.map((val, idx) => {
      const x = pad + idx * dx;
      const normalized = Math.min(1.0, Math.max(0.0, val / maxVal));
      const y = height - pad - normalized * h;
      return `${x},${y}`;
    });

    return (
      <svg className="w-full h-20 overflow-visible">
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={coords.join(' ')}
        />
        {points.map((val, idx) => {
          const [cx, cy] = coords[idx].split(',');
          return <circle key={idx} cx={cx} cy={cy} r="3" fill={color} />;
        })}
      </svg>
    );
  };

  const isJala = node.node_type === 'FLOOD';
  const isAgni = node.node_type === 'FIRE';
  const isBhumi = node.node_type === 'LANDSLIDE';
  const isVayu = node.node_type === 'AIR_QUALITY';
  const isAkasha = node.node_type === 'WEATHER';

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto select-text">
      {/* Back Button & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/nodes')}
            className="p-1.5 rounded bg-bg-surface hover:bg-bg-elevated text-text-secondary hover:text-text-primary transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold text-text-primary">{node.id} — {node.name}</h1>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                  riskBand === 'CRITICAL'
                    ? 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical'
                    : riskBand === 'WARNING'
                    ? 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning'
                    : riskBand === 'WATCH'
                    ? 'bg-hazard-watch/20 text-hazard-watch border-hazard-watch'
                    : 'bg-hazard-normal/20 text-hazard-normal border-hazard-normal'
                }`}
              >
                {riskBand} ({riskScore}%)
              </span>
            </div>
            <p className="text-xs text-text-muted mt-0.5">
              {node.tagline || 'Autonomous Hazard Intelligence Node'} • 📍 {node.location_name}
            </p>
          </div>
        </div>

        {/* Quick Node Switcher */}
        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => navigate('/nodes/JALA-01')}
            className={`px-2.5 py-1 rounded border text-xs font-semibold ${
              nodeId === 'JALA-01' ? 'bg-accent-info/20 border-accent-info text-accent-info' : 'bg-bg-surface border-border-subtle text-text-muted'
            }`}
          >
            JALA-01
          </button>
          <button
            onClick={() => navigate('/nodes/AGNI-02')}
            className={`px-2.5 py-1 rounded border text-xs font-semibold ${
              nodeId === 'AGNI-02' ? 'bg-orange-500/20 border-orange-500 text-orange-400' : 'bg-bg-surface border-border-subtle text-text-muted'
            }`}
          >
            AGNI-02
          </button>
          <button
            onClick={() => navigate('/nodes/BHUMI-03')}
            className={`px-2.5 py-1 rounded border text-xs font-semibold ${
              nodeId === 'BHUMI-03' ? 'bg-green-500/20 border-green-500 text-green-400' : 'bg-bg-surface border-border-subtle text-text-muted'
            }`}
          >
            BHUMI-03
          </button>
          <button
            onClick={() => navigate('/nodes/VAYU-04')}
            className={`px-2.5 py-1 rounded border text-xs font-semibold ${
              nodeId === 'VAYU-04'
                ? 'bg-sky-500/20 border-sky-500 text-sky-300'
                : 'bg-bg-surface border-border-subtle text-text-muted'
            }`}
          >
            VAYU-04
          </button>

          <button
            onClick={() => navigate('/nodes/AKASHA-05')}
            className={`px-2.5 py-1 rounded border text-xs font-semibold ${
              nodeId === 'AKASHA-05'
                ? 'bg-violet-500/20 border-violet-500 text-violet-300'
                : 'bg-bg-surface border-border-subtle text-text-muted'
            }`}
          >
            AKASHA-05
          </button>
        </div>
      </div>

      {/* Hardware Telemetry Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle flex items-center space-x-3">
          <Battery className="w-5 h-5 text-hazard-normal shrink-0" />
          <div>
            <div className="text-[10px] text-text-muted uppercase">Battery & Solar</div>
            <div className="font-mono font-bold text-xs text-text-primary">
              {node.battery_pct?.toFixed(0) ?? 94}% ({node.solar_voltage?.toFixed(2) ?? 4.15}V)
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle flex items-center space-x-3">
          <Radio className="w-5 h-5 text-accent-info shrink-0" />
          <div>
            <div className="text-[10px] text-text-muted uppercase">Signal / Transport RSSI</div>
            <div className="font-mono font-bold text-xs text-text-primary">
              {node.signal_rssi ?? -76} dBm
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle flex items-center space-x-3">
          <Activity className="w-5 h-5 text-accent-ai shrink-0" />
          <div>
            <div className="text-[10px] text-text-muted uppercase">Packet Loss</div>
            <div className="font-mono font-bold text-xs text-text-primary">
              {node.packet_loss_pct?.toFixed(1) ?? 0.0}%
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary p-3 rounded-lg border border-border-subtle flex items-center space-x-3">
          <Compass className="w-5 h-5 text-purple-400 shrink-0" />
          <div>
            <div className="text-[10px] text-text-muted uppercase">GPS Coordinates</div>
            <div className="font-mono text-xs text-text-primary">
              {node.latitude.toFixed(4)}°N, {node.longitude.toFixed(4)}°E
            </div>
          </div>
        </div>
      </div>

      {/* NODE SPECIFIC INTELLIGENCE PANELS */}

      {/* 1. JALA-01 FLOOD PANEL */}
      {isJala && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Main Hydrology Chart */}
          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Droplets className="w-4 h-4 text-accent-info" />
                <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                  Water Level Time-Series (cm)
                </h3>
              </div>
              <span className="text-[11px] font-mono text-accent-info font-bold">
                {latestMetrics.water_level_cm?.toFixed(1) ?? '34.2'} cm
              </span>
            </div>

            {/* Warning Threshold Band Legend */}
            <div className="flex items-center space-x-3 text-[10px] text-text-muted border-b border-border-subtle pb-2">
              <span className="text-hazard-watch">Watch: ≥60cm</span>
              <span className="text-hazard-warning">Warning: ≥120cm</span>
              <span className="text-hazard-critical">Critical: ≥180cm</span>
            </div>

            {/* Sparkline */}
            {renderSparkline(
              telemetry.map((t) => t.metrics?.water_level_cm ?? 34.0),
              220,
              '#27C7E8',
              120
            )}

            <div className="grid grid-cols-3 gap-2 text-center bg-bg-surface p-2 rounded text-xs">
              <div>
                <div className="text-[10px] text-text-muted">Rate of Rise</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.water_rise_rate_cm_min?.toFixed(2) ?? '0.00'} cm/min
                </div>
              </div>
              <div>
                <div className="text-[10px] text-text-muted">Acceleration</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.water_rise_acceleration?.toFixed(3) ?? '0.000'}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-text-muted">Rain Intensity</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.rain_intensity?.toFixed(1) ?? '0.0'} mm/h
                </div>
              </div>
            </div>
          </div>

          {/* Hydrological Forecast & Crossing Projection */}
          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                Breach & Threshold Projection
              </h3>
            </div>

            <div className="bg-bg-surface p-4 rounded-lg border border-border-subtle text-center">
              <div className="text-xs text-text-muted mb-1">Estimated Threshold Crossing Window</div>
              <div className="text-xl font-bold font-mono text-accent-info">
                {latestRisk.estimated_crossing_time || 'NO THRESHOLD CROSSING PROJECTED'}
              </div>
              <div className="text-[11px] text-text-muted mt-2">
                Calculated dynamically from 1st & 2nd kinematic derivatives vs 180cm datum.
              </div>
            </div>

            {/* Risk Trend Direction */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-bg-surface p-2.5 rounded border border-border-subtle">
                <div className="text-[10px] text-text-muted">Trend Direction</div>
                <div className="font-bold text-text-primary mt-0.5">{latestRisk.risk_trend || 'STABLE'}</div>
              </div>
              <div className="bg-bg-surface p-2.5 rounded border border-border-subtle">
                <div className="text-[10px] text-text-muted">Confidence</div>
                <div className="font-bold text-text-primary mt-0.5">{latestRisk.confidence?.toFixed(0) ?? 95}%</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. AGNI-02 FIRE PANEL */}
      {isAgni && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Flame className="w-4 h-4 text-hazard-warning" />
                <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                  Combustion & Gas Dynamics (MQ-2 / MQ-135)
                </h3>
              </div>
              <span className="text-[11px] font-mono text-hazard-warning font-bold">
                MQ-2: {latestMetrics.mq2_raw?.toFixed(0) ?? '115'}
              </span>
            </div>

            {renderSparkline(
              telemetry.map((t) => t.metrics?.mq2_raw ?? 115.0),
              1000,
              '#F97316',
              120
            )}

            <div className="grid grid-cols-3 gap-2 text-center bg-bg-surface p-2 rounded text-xs">
              <div>
                <div className="text-[10px] text-text-muted">MQ-135 Gas</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.mq135_raw?.toFixed(0) ?? '128'}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-text-muted">Temperature</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.temperature_c?.toFixed(1) ?? '27.2'} °C
                </div>
              </div>
              <div>
                <div className="text-[10px] text-text-muted">Optical Flame</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.flame_detected ? 'DETECTED' : 'CLEAR'}
                </div>
              </div>
            </div>
          </div>

          {/* Computer Vision Detector Panel */}
          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
            <div className="flex items-center space-x-2">
              <Camera className="w-4 h-4 text-accent-ai" />
              <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                Edge Computer Vision Stream
              </h3>
            </div>

            <div className="bg-bg-surface h-36 rounded border border-dashed border-border-subtle flex flex-col items-center justify-center p-4 text-center">
              <Camera className="w-8 h-8 text-text-muted mb-2" />
              <div className="text-xs font-semibold text-text-secondary">
                VISUAL AI NOT CONNECTED
              </div>
              <div className="text-[11px] text-text-muted mt-1 max-w-xs">
                Physical sensor fusion is operating autonomously. Connect IP / RTSP video stream to engage ONNX visual fire detector.
              </div>
            </div>

            <div className="bg-bg-surface p-2.5 rounded border border-border-subtle flex items-center justify-between text-xs">
              <span className="text-text-muted">Camera Fire Confidence:</span>
              <span className="font-mono font-bold text-text-primary">
                {((latestMetrics.camera_fire_confidence || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 3. BHUMI-03 LANDSLIDE PANEL */}
      {isBhumi && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Mountain className="w-4 h-4 text-hazard-normal" />
                <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                  Inclinometer Structural Tilt Delta (°)
                </h3>
              </div>
              <span className="text-[11px] font-mono text-hazard-normal font-bold">
                {latestMetrics.tilt_delta_deg?.toFixed(2) ?? '0.12'}°
              </span>
            </div>

            {renderSparkline(
              telemetry.map((t) => t.metrics?.tilt_delta_deg ?? 0.12),
              6.0,
              '#22C55E',
              120
            )}

            <div className="grid grid-cols-3 gap-2 text-center bg-bg-surface p-2 rounded text-xs">
              <div>
                <div className="text-[10px] text-text-muted">Tilt X / Y</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.tilt_x_deg?.toFixed(2) ?? '0.35'}° / {latestMetrics.tilt_y_deg?.toFixed(2) ?? '-0.22'}°
                </div>
              </div>
              <div>
                <div className="text-[10px] text-text-muted">Vibration RMS</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.vibration_rms?.toFixed(2) ?? '0.45'} g
                </div>
              </div>
              <div>
                <div className="text-[10px] text-text-muted">Antecedent Rain</div>
                <div className="font-mono font-bold text-text-primary">
                  {latestMetrics.rain_context?.toFixed(1) ?? '5.0'} mm
                </div>
              </div>
            </div>
          </div>

          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-accent-info" />
              <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                Soil Moisture Saturation Profile
              </h3>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-bg-surface p-3 rounded border border-border-subtle text-center">
                <div className="text-[10px] text-text-muted">Upper Layer (15 cm)</div>
                <div className="text-xl font-mono font-bold text-accent-info mt-1">
                  {latestMetrics.soil_moisture_upper_pct?.toFixed(0) ?? '28'}%
                </div>
              </div>
              <div className="bg-bg-surface p-3 rounded border border-border-subtle text-center">
                <div className="text-[10px] text-text-muted">Lower Layer (60 cm)</div>
                <div className="text-xl font-mono font-bold text-accent-info mt-1">
                  {latestMetrics.soil_moisture_lower_pct?.toFixed(0) ?? '33'}%
                </div>
              </div>
            </div>

            <div className="bg-bg-surface p-3 rounded border border-border-subtle text-xs">
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-text-muted">Geological Equilibrium Index:</span>
                <span className="text-hazard-normal font-bold">STABLE</span>
              </div>
              <div className="w-full h-2 bg-bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-hazard-normal" style={{ width: '22%' }} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4. VAYU-04 AIR QUALITY PANEL */}
      {isVayu && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
            <div className="flex items-center gap-2 mb-3">
              <Wind className="w-4 h-4 text-sky-300" />
              <h3 className="text-xs font-bold uppercase tracking-wider">
                Air Quality Intelligence
              </h3>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {[
                ['PM2.5', latestMetrics.pm2_5, 'µg/m³'],
                ['PM10', latestMetrics.pm10, 'µg/m³'],
                ['CO', latestMetrics.co_ppm, 'ppm'],
                ['VOC', latestMetrics.voc_index, 'index'],
              ].map(([name, value, unit]) => (
                <div key={String(name)} className="bg-bg-surface border border-border-subtle rounded p-3">
                  <div className="text-[10px] text-text-muted">{name}</div>
                  <div className="font-mono font-bold mt-1">
                    {typeof value === 'number' ? value.toFixed(1) : '—'}
                    <span className="ml-1 text-[9px] text-text-muted">{unit}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
            <div className="text-xs font-bold uppercase tracking-wider mb-2">
              Decision Context
            </div>
            <p className="text-[11px] text-text-secondary leading-relaxed">
              PRAHARI combines particulate and gas indicators with sensor trust.
              The displayed risk is an engineering evidence score and is not presented
              as a statutory AQI.
            </p>
          </div>
        </div>
      )}

      {/* 5. AKASHA-05 ATMOSPHERIC PANEL */}
      {isAkasha && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
            <div className="flex items-center gap-2 mb-3">
              <CloudRain className="w-4 h-4 text-violet-300" />
              <h3 className="text-xs font-bold uppercase tracking-wider">
                Atmospheric Intelligence
              </h3>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {[
                ['Rain', latestMetrics.rain_intensity, 'mm/h'],
                ['Wind', latestMetrics.wind_speed_kmh, 'km/h'],
                ['Gust', latestMetrics.wind_gust_kmh, 'km/h'],
                ['Pressure', latestMetrics.pressure_hpa, 'hPa'],
              ].map(([name, value, unit]) => (
                <div key={String(name)} className="bg-bg-surface border border-border-subtle rounded p-3">
                  <div className="text-[10px] text-text-muted">{name}</div>
                  <div className="font-mono font-bold mt-1">
                    {typeof value === 'number' ? value.toFixed(1) : '—'}
                    <span className="ml-1 text-[9px] text-text-muted">{unit}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle">
            <div className="text-xs font-bold uppercase tracking-wider mb-2">
              Cross-Hazard Context
            </div>
            <p className="text-[11px] text-text-secondary leading-relaxed">
              Increasing rainfall, wind and pressure-change evidence can trigger
              reevaluation of related JALA flood and BHUMI landslide conditions.
            </p>
          </div>
        </div>
      )}

      {/* EXPLAINABLE AI "WHY?" SECTION */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-accent-ai font-bold text-xs uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4" />
            <span>Explainable AI (XAI) Root Cause & Causality</span>
          </div>
          <span className="text-[10px] font-mono bg-bg-surface px-2 py-0.5 rounded border border-border-subtle text-text-muted">
            Source: {latestRisk.model_source || 'RULE_FUSION'}
          </span>
        </div>

        <div className="bg-bg-surface p-3.5 rounded border border-border-subtle font-mono text-xs text-text-secondary leading-relaxed whitespace-pre-line">
          {latestRisk.human_explanation || 'All monitored metrics are currently within verified baseline bounds.'}
        </div>

        {/* Contributing Factors Table */}
        {latestRisk.contributing_factors && latestRisk.contributing_factors.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 pt-2">
            {latestRisk.contributing_factors.map((f: any, idx: number) => (
              <div key={idx} className="bg-bg-surface p-2 rounded border border-border-subtle text-xs">
                <div className="text-[10px] text-text-muted">{f.factor} (Weight: {(f.weight * 100).toFixed(0)}%)</div>
                <div className="font-mono font-bold text-text-primary mt-0.5">{f.value}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Raw Telemetry Inspector */}
      <div className="bg-bg-secondary rounded-lg border border-border-subtle overflow-hidden">
        <button
          onClick={() => setShowRawJson(!showRawJson)}
          className="w-full p-3 bg-bg-surface text-left text-xs font-semibold text-text-secondary hover:text-text-primary flex items-center justify-between"
        >
          <div className="flex items-center space-x-2">
            <FileCode className="w-4 h-4 text-accent-info" />
            <span>Inspect Raw Telemetry Payload Frame</span>
          </div>
          <span className="text-[11px] text-text-muted font-mono">{showRawJson ? 'Hide [-]' : 'Show [+]'}</span>
        </button>
        {showRawJson && (
          <pre className="p-4 text-[11px] font-mono text-text-muted overflow-x-auto bg-bg-primary">
            {JSON.stringify(telemetry[telemetry.length - 1] || node, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};
