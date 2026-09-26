import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Droplets, Flame, Mountain, Wind, CloudRain, ArrowUpRight, ShieldCheck, AlertTriangle } from 'lucide-react';

interface LiveNodeStripsProps {
  nodes: any[];
}

export const LiveNodeStrips: React.FC<LiveNodeStripsProps> = ({ nodes }) => {
  const navigate = useNavigate();

  const getNode = (id: string) => nodes.find((n) => n.id === id) || { id, name: id };

  const jala = getNode('JALA-01');
  const agni = getNode('AGNI-02');
  const bhumi = getNode('BHUMI-03');
  const vayu = getNode('VAYU-04');
  const akasha = getNode('AKASHA-05');

  const getRiskBadge = (riskBand: string = 'NORMAL', score: number = 0) => {
    let color = 'bg-hazard-normal/20 text-hazard-normal border-hazard-normal/40';
    if (riskBand === 'CRITICAL') color = 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical/40 animate-pulse';
    else if (riskBand === 'WARNING') color = 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning/40';
    else if (riskBand === 'WATCH') color = 'bg-hazard-watch/20 text-hazard-watch border-hazard-watch/40';

    return (
      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${color}`}>
        {riskBand} ({score.toFixed(0)}%)
      </span>
    );
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5 gap-2">
      {/* JALA-01 STRIP */}
      <div
        onClick={() => navigate('/nodes/JALA-01')}
        className="bg-bg-secondary p-2.5 rounded-lg border border-border-subtle hover:border-accent-info/50 cursor-pointer transition-all flex flex-col justify-between"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded bg-blue-500/15 text-accent-info flex items-center justify-center">
              <Droplets className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-text-primary flex items-center space-x-1">
                <span>JALA-01</span>
                <span className="text-[10px] text-text-muted font-normal">FLOOD</span>
              </div>
              <div className="text-[10px] text-text-muted truncate max-w-[140px]">
                {jala.location_name || 'Brahmaputra Basin'}
              </div>
            </div>
          </div>
          {getRiskBadge(jala.latest_risk?.risk_band, jala.latest_risk?.risk_score)}
        </div>

        {/* Telemetry Metrics */}
        <div className="grid grid-cols-3 gap-2 bg-bg-surface p-2 rounded border border-border-subtle text-center text-xs">
          <div>
            <div className="text-[10px] text-text-muted">Water Level</div>
            <div className="font-mono font-semibold text-text-primary">
              {jala.latest_metrics?.water_level_cm?.toFixed(1) ?? '34.2'} <span className="text-[9px] text-text-muted">cm</span>
            </div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted">Rise Rate</div>
            <div className="font-mono font-semibold text-text-primary">
              {jala.latest_metrics?.water_rise_rate_cm_min?.toFixed(2) ?? '0.00'} <span className="text-[9px] text-text-muted">cm/m</span>
            </div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted">Rain</div>
            <div className="font-mono font-semibold text-text-primary">
              {jala.latest_metrics?.rain_intensity?.toFixed(1) ?? '0.0'} <span className="text-[9px] text-text-muted">mm/h</span>
            </div>
          </div>
        </div>

        <div className="mt-2 text-[10px] text-text-secondary flex items-center justify-between">
          <span className="truncate">
            Projection: <strong className="text-accent-info">{jala.latest_risk?.estimated_crossing_time || 'Stable'}</strong>
          </span>
          <ArrowUpRight className="w-3.5 h-3.5 text-text-muted" />
        </div>
      </div>

      {/* AGNI-02 STRIP */}
      <div
        onClick={() => navigate('/nodes/AGNI-02')}
        className="bg-bg-secondary p-2.5 rounded-lg border border-border-subtle hover:border-accent-info/50 cursor-pointer transition-all flex flex-col justify-between"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded bg-orange-500/15 text-hazard-warning flex items-center justify-center">
              <Flame className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-text-primary flex items-center space-x-1">
                <span>AGNI-02</span>
                <span className="text-[10px] text-text-muted font-normal">FIRE / GAS</span>
              </div>
              <div className="text-[10px] text-text-muted truncate max-w-[140px]">
                {agni.location_name || 'Similipal Ridge'}
              </div>
            </div>
          </div>
          {getRiskBadge(agni.latest_risk?.risk_band, agni.latest_risk?.risk_score)}
        </div>

        {/* Telemetry Metrics */}
        <div className="grid grid-cols-3 gap-2 bg-bg-surface p-2 rounded border border-border-subtle text-center text-xs">
          <div>
            <div className="text-[10px] text-text-muted">Smoke MQ-2</div>
            <div className="font-mono font-semibold text-text-primary">
              {agni.latest_metrics?.mq2_raw?.toFixed(0) ?? '115'}
            </div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted">Temp</div>
            <div className="font-mono font-semibold text-text-primary">
              {agni.latest_metrics?.temperature_c?.toFixed(1) ?? '27.2'} <span className="text-[9px] text-text-muted">°C</span>
            </div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted">Flame / AI</div>
            <div className="font-mono font-semibold text-text-primary">
              {agni.latest_metrics?.flame_detected ? 'ACTIVE' : 'CLEAR'}
            </div>
          </div>
        </div>

        <div className="mt-2 text-[10px] text-text-secondary flex items-center justify-between">
          <span className="truncate">
            Trust: MQ-2 <strong className="text-accent-info">{agni.latest_risk?.sensor_trust?.mq2_smoke_sensor?.toFixed(0) || 98}%</strong>
          </span>
          <ArrowUpRight className="w-3.5 h-3.5 text-text-muted" />
        </div>
      </div>

      {/* BHUMI-03 STRIP */}
      <div
        onClick={() => navigate('/nodes/BHUMI-03')}
        className="bg-bg-secondary p-2.5 rounded-lg border border-border-subtle hover:border-accent-info/50 cursor-pointer transition-all flex flex-col justify-between"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded bg-green-500/15 text-hazard-normal flex items-center justify-center">
              <Mountain className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-text-primary flex items-center space-x-1">
                <span>BHUMI-03</span>
                <span className="text-[10px] text-text-muted font-normal">LANDSLIDE</span>
              </div>
              <div className="text-[10px] text-text-muted truncate max-w-[140px]">
                {bhumi.location_name || 'NH-58 Ghat Section'}
              </div>
            </div>
          </div>
          {getRiskBadge(bhumi.latest_risk?.risk_band, bhumi.latest_risk?.risk_score)}
        </div>

        {/* Telemetry Metrics */}
        <div className="grid grid-cols-3 gap-2 bg-bg-surface p-2 rounded border border-border-subtle text-center text-xs">
          <div>
            <div className="text-[10px] text-text-muted">Soil Saturation</div>
            <div className="font-mono font-semibold text-text-primary">
              {bhumi.latest_metrics?.soil_moisture_upper_pct?.toFixed(0) ?? '28'} <span className="text-[9px] text-text-muted">%</span>
            </div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted">Tilt Delta</div>
            <div className="font-mono font-semibold text-text-primary">
              {bhumi.latest_metrics?.tilt_delta_deg?.toFixed(2) ?? '0.12'} <span className="text-[9px] text-text-muted">°</span>
            </div>
          </div>
          <div>
            <div className="text-[10px] text-text-muted">Vib RMS</div>
            <div className="font-mono font-semibold text-text-primary">
              {bhumi.latest_metrics?.vibration_rms?.toFixed(2) ?? '0.45'} <span className="text-[9px] text-text-muted">g</span>
            </div>
          </div>
        </div>

        <div className="mt-2 text-[10px] text-text-secondary flex items-center justify-between">
          <span className="truncate">
            Slope Equilibrium: <strong className="text-hazard-normal">STABLE</strong>
          </span>
          <ArrowUpRight className="w-3.5 h-3.5 text-text-muted" />
        </div>
      </div>

      {/* VAYU-04 STRIP */}
      <div
        onClick={() => navigate('/nodes/VAYU-04')}
        className="bg-bg-secondary p-2.5 rounded-lg border border-border-subtle hover:border-accent-info/50 cursor-pointer transition-all flex flex-col justify-between"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded bg-sky-500/15 text-sky-300 flex items-center justify-center">
              <Wind className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-text-primary">
                VAYU-04
                <span className="ml-1 text-[10px] text-text-muted font-normal">
                  AIR
                </span>
              </div>
              <div className="text-[10px] text-text-muted">
                Air Quality Intelligence
              </div>
            </div>
          </div>
          {getRiskBadge(
            vayu.latest_risk?.risk_band,
            vayu.latest_risk?.risk_score
          )}
        </div>

        <div className="grid grid-cols-3 gap-2 bg-bg-surface p-2 rounded border border-border-subtle text-center text-xs">
          <div>
            <div className="text-[10px] text-text-muted">PM2.5</div>
            <div className="font-mono font-semibold text-text-primary">
              {vayu.latest_metrics?.pm2_5?.toFixed?.(1) ?? '—'}
            </div>
          </div>

          <div>
            <div className="text-[10px] text-text-muted">PM10</div>
            <div className="font-mono font-semibold text-text-primary">
              {vayu.latest_metrics?.pm10?.toFixed?.(1) ?? '—'}
            </div>
          </div>

          <div>
            <div className="text-[10px] text-text-muted">CO</div>
            <div className="font-mono font-semibold text-text-primary">
              {vayu.latest_metrics?.co_ppm?.toFixed?.(1) ?? '—'}
            </div>
          </div>
        </div>

        <div className="mt-2 text-[10px] text-text-secondary flex items-center justify-between">
          <span>VAYU Environmental Node</span>
          <ArrowUpRight className="w-3.5 h-3.5 text-text-muted" />
        </div>
      </div>

      {/* AKASHA-05 STRIP */}
      <div
        onClick={() => navigate('/nodes/AKASHA-05')}
        className="bg-bg-secondary p-2.5 rounded-lg border border-border-subtle hover:border-accent-info/50 cursor-pointer transition-all flex flex-col justify-between"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded bg-violet-500/15 text-violet-300 flex items-center justify-center">
              <CloudRain className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-text-primary">
                AKASHA-05
                <span className="ml-1 text-[10px] text-text-muted font-normal">
                  ATMOSPHERE
                </span>
              </div>
              <div className="text-[10px] text-text-muted">
                Weather Intelligence
              </div>
            </div>
          </div>
          {getRiskBadge(
            akasha.latest_risk?.risk_band,
            akasha.latest_risk?.risk_score
          )}
        </div>

        <div className="grid grid-cols-3 gap-2 bg-bg-surface p-2 rounded border border-border-subtle text-center text-xs">
          <div>
            <div className="text-[10px] text-text-muted">Rain</div>
            <div className="font-mono font-semibold text-text-primary">
              {akasha.latest_metrics?.rain_intensity?.toFixed?.(1) ?? '—'}
            </div>
          </div>

          <div>
            <div className="text-[10px] text-text-muted">Wind</div>
            <div className="font-mono font-semibold text-text-primary">
              {akasha.latest_metrics?.wind_speed_kmh?.toFixed?.(1) ?? '—'}
            </div>
          </div>

          <div>
            <div className="text-[10px] text-text-muted">Pressure</div>
            <div className="font-mono font-semibold text-text-primary">
              {akasha.latest_metrics?.pressure_hpa?.toFixed?.(0) ?? '—'}
            </div>
          </div>
        </div>

        <div className="mt-2 text-[10px] text-text-secondary flex items-center justify-between">
          <span>AKASHA Environmental Node</span>
          <ArrowUpRight className="w-3.5 h-3.5 text-text-muted" />
        </div>
      </div>
    </div>
  );
};
