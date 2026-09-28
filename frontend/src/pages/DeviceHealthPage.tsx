import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, Battery, Radio, ShieldCheck } from 'lucide-react';
import { fetchSensorHealth } from '../services/api';
import { wsClient } from '../services/websocket';

export const DeviceHealthPage: React.FC = () => {
  const [sensors, setSensors] = useState<any[]>([]);
  const [error, setError] = useState('');
  const load = () => fetchSensorHealth().then(setSensors).catch((reason) => setError(reason.message));
  useEffect(() => {
    load();
    const unsub = wsClient.subscribe('sensor.health.changed', load);
    return () => unsub();
  }, []);

  return <div className="command-page command-reveal p-3 lg:p-5 space-y-4 max-w-[1600px] mx-auto">
    <header className="rounded-lg border border-border-subtle bg-bg-secondary p-4">
      <h1 className="flex items-center gap-2 text-base font-bold"><Activity className="h-5 w-5 text-hazard-normal" />Sensor Health Digital Twin</h1>
      <p className="mt-1 text-xs text-text-muted">Persisted fleet trust, connectivity, calibration and fault-reason evidence.</p>
    </header>
    {error && <div role="alert" className="rounded border border-red-500/30 p-3 text-red-300"><AlertTriangle className="mr-2 inline h-4 w-4" />{error}</div>}
    {!error && sensors.length === 0 && <div className="rounded border border-border-subtle p-5 text-sm text-text-muted">NO SENSOR HEALTH SNAPSHOTS — awaiting accepted telemetry.</div>}
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {sensors.map(sensor => <article key={sensor.sensor_id} className="rounded-lg border border-border-subtle bg-bg-secondary p-4">
        <div className="flex items-start justify-between gap-3"><div><div className="font-mono text-xs font-semibold">{sensor.sensor_id}</div><div className="text-[10px] text-text-muted">{sensor.node_id} · {sensor.firmware_version || 'FIRMWARE UNKNOWN'}</div></div><span className={`rounded border px-2 py-1 text-[10px] font-bold ${sensor.state === 'HEALTHY' ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/40 text-amber-300'}`}>{sensor.state}</span></div>
        <div className="my-3 grid grid-cols-3 gap-2 text-xs"><div className="rounded bg-bg-surface p-2"><ShieldCheck className="mb-1 h-4 w-4" /><div className="text-[10px] text-text-muted">Trust</div><div className="font-mono">{sensor.trust_score}%</div></div><div className="rounded bg-bg-surface p-2"><Battery className="mb-1 h-4 w-4" /><div className="text-[10px] text-text-muted">Battery</div><div className="font-mono">{sensor.battery_pct == null ? 'N/A' : `${sensor.battery_pct}%`}</div></div><div className="rounded bg-bg-surface p-2"><Radio className="mb-1 h-4 w-4" /><div className="text-[10px] text-text-muted">RSSI</div><div className="font-mono">{sensor.rssi == null ? 'N/A' : `${sensor.rssi} dBm`}</div></div></div>
        <dl className="grid grid-cols-2 gap-2 text-[10px]"><div><dt className="text-text-muted">Calibration</dt><dd>{sensor.calibration_state}</dd></div><div><dt className="text-text-muted">Provenance</dt><dd>{sensor.provenance}</dd></div><div><dt className="text-text-muted">Noise / drift</dt><dd>{sensor.noise_score == null ? 'INSUFFICIENT HISTORY' : sensor.noise_score} / {sensor.drift_score == null ? 'INSUFFICIENT HISTORY' : sensor.drift_score}</dd></div><div><dt className="text-text-muted">Missing data</dt><dd>{sensor.missing_data_pct}%</dd></div></dl>
        <div className="mt-3 text-[10px] text-text-muted">Reasons: {sensor.reason_codes.length ? sensor.reason_codes.join(', ') : 'NONE'}</div>
      </article>)}
    </div>
  </div>;
};
