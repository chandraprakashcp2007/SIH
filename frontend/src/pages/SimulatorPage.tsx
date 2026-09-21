import React, { useState, useEffect } from 'react';
import { fetchScenarios, triggerScenario, resetSimulator } from '../services/api';
import { wsClient } from '../services/websocket';
import { PlaySquare, RotateCcw, AlertTriangle, ShieldCheck, Flame, Droplets, Mountain, Activity, WifiOff } from 'lucide-react';

export const SimulatorPage: React.FC = () => {
  const [scenarioData, setScenarioData] = useState<any>(null);
  const [activeScenario, setActiveScenario] = useState<string>('ALL_NORMAL');
  const [loadingScenario, setLoadingScenario] = useState<string | null>(null);

  const loadScenarios = async () => {
    try {
      const data = await fetchScenarios();
      setScenarioData(data);
      setActiveScenario(data.active_scenario);
    } catch (err) {
      console.error('Error fetching scenarios:', err);
    }
  };

  useEffect(() => {
    loadScenarios();
    const unsub = wsClient.subscribe('simulation.updated', (data) => {
      setActiveScenario(data.active_scenario);
    });
    return () => unsub();
  }, []);

  const handleTrigger = async (scId: string) => {
    setLoadingScenario(scId);
    try {
      await triggerScenario(scId);
      setActiveScenario(scId);
    } catch (err) {
      console.error(`Failed to trigger ${scId}:`, err);
    } finally {
      setLoadingScenario(null);
    }
  };

  const handleReset = async () => {
    setLoadingScenario('RESET');
    try {
      await resetSimulator();
      setActiveScenario('ALL_NORMAL');
    } catch (err) {
      console.error('Failed to reset simulation:', err);
    } finally {
      setLoadingScenario(null);
    }
  };

  const scenarios = scenarioData?.scenarios || [];

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header & Prominent Simulation Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
              <PlaySquare className="w-5 h-5 text-accent-info" />
              <span>PRAHARI Hardware & Disaster Simulator</span>
            </h1>
            <span className="text-[10px] font-bold px-2.5 py-0.5 rounded border uppercase bg-accent-info/20 text-accent-info border-accent-info/40 animate-pulse">
              SIMULATION ENGINE ACTIVE
            </span>
          </div>
          <p className="text-xs text-text-muted mt-0.5">
            Feeds physically continuous synthetic disaster kinetics into the identical LoRa telemetry ingestion pipeline.
          </p>
        </div>

        {/* Global Reset */}
        <button
          onClick={handleReset}
          disabled={loadingScenario === 'RESET'}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-bg-surface hover:bg-bg-elevated border border-border-subtle rounded text-xs text-text-primary transition-colors disabled:opacity-50"
        >
          <RotateCcw className="w-4 h-4 text-accent-info" />
          <span>Reset All to Nominal</span>
        </button>
      </div>

      {/* Active Scenario Indicator Banner */}
      <div className="bg-bg-secondary p-3.5 rounded-lg border border-accent-info/40 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-3">
          <span className="text-text-muted">Currently Engaged Scenario:</span>
          <span className="font-mono font-bold text-accent-info text-sm uppercase">
            {activeScenario}
          </span>
        </div>
        <span className="text-[11px] text-text-muted">
          Telemetric tick rate: 2.0s • Zero artificial jumps
        </span>
      </div>

      {/* Scenarios Grid by Category */}
      <div className="space-y-4">
        {/* Flood Scenarios */}
        <div>
          <h3 className="text-xs font-bold text-accent-info uppercase tracking-wider mb-2 flex items-center space-x-1.5">
            <Droplets className="w-4 h-4" />
            <span>JALA-01 Hydrology & Inundation Scenarios</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {scenarios
              .filter((s: any) => s.hazard === 'FLOOD')
              .map((sc: any) => (
                <div
                  key={sc.id}
                  className={`bg-bg-secondary p-3.5 rounded-lg border transition-all flex flex-col justify-between ${
                    activeScenario === sc.id ? 'border-accent-info bg-accent-info/5 shadow-lg' : 'border-border-subtle'
                  }`}
                >
                  <div>
                    <div className="font-bold text-xs text-text-primary">{sc.name}</div>
                    <div className="text-[11px] text-text-muted mt-1 leading-relaxed">{sc.desc}</div>
                  </div>
                  <button
                    aria-label={`Engage ${sc.name}`}
                    onClick={() => handleTrigger(sc.id)}
                    disabled={loadingScenario === sc.id}
                    className={`mt-3 w-full py-1.5 rounded text-xs font-bold transition-colors ${
                      activeScenario === sc.id
                        ? 'bg-accent-info text-bg-primary'
                        : 'bg-bg-surface hover:bg-bg-elevated text-text-primary border border-border-subtle'
                    }`}
                  >
                    {activeScenario === sc.id ? 'Engaged (Active)' : 'Engage Scenario'}
                  </button>
                </div>
              ))}
          </div>
        </div>

        {/* Fire Scenarios */}
        <div>
          <h3 className="text-xs font-bold text-hazard-warning uppercase tracking-wider mb-2 flex items-center space-x-1.5">
            <Flame className="w-4 h-4" />
            <span>AGNI-02 Combustion & Optical Plume Scenarios</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {scenarios
              .filter((s: any) => s.hazard === 'FIRE')
              .map((sc: any) => (
                <div
                  key={sc.id}
                  className={`bg-bg-secondary p-3.5 rounded-lg border transition-all flex flex-col justify-between ${
                    activeScenario === sc.id ? 'border-hazard-warning bg-hazard-warning/5 shadow-lg' : 'border-border-subtle'
                  }`}
                >
                  <div>
                    <div className="font-bold text-xs text-text-primary">{sc.name}</div>
                    <div className="text-[11px] text-text-muted mt-1 leading-relaxed">{sc.desc}</div>
                  </div>
                  <button
                    aria-label={`Engage ${sc.name}`}
                    onClick={() => handleTrigger(sc.id)}
                    disabled={loadingScenario === sc.id}
                    className={`mt-3 w-full py-1.5 rounded text-xs font-bold transition-colors ${
                      activeScenario === sc.id
                        ? 'bg-hazard-warning text-bg-primary'
                        : 'bg-bg-surface hover:bg-bg-elevated text-text-primary border border-border-subtle'
                    }`}
                  >
                    {activeScenario === sc.id ? 'Engaged (Active)' : 'Engage Scenario'}
                  </button>
                </div>
              ))}
          </div>
        </div>

        {/* Landslide Scenarios */}
        <div>
          <h3 className="text-xs font-bold text-hazard-normal uppercase tracking-wider mb-2 flex items-center space-x-1.5">
            <Mountain className="w-4 h-4" />
            <span>BHUMI-03 Geotechnical Slope & Pore-Pressure Scenarios</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {scenarios
              .filter((s: any) => s.hazard === 'LANDSLIDE')
              .map((sc: any) => (
                <div
                  key={sc.id}
                  className={`bg-bg-secondary p-3.5 rounded-lg border transition-all flex flex-col justify-between ${
                    activeScenario === sc.id ? 'border-hazard-normal bg-hazard-normal/5 shadow-lg' : 'border-border-subtle'
                  }`}
                >
                  <div>
                    <div className="font-bold text-xs text-text-primary">{sc.name}</div>
                    <div className="text-[11px] text-text-muted mt-1 leading-relaxed">{sc.desc}</div>
                  </div>
                  <button
                    aria-label={`Engage ${sc.name}`}
                    onClick={() => handleTrigger(sc.id)}
                    disabled={loadingScenario === sc.id}
                    className={`mt-3 w-full py-1.5 rounded text-xs font-bold transition-colors ${
                      activeScenario === sc.id
                        ? 'bg-hazard-normal text-bg-primary'
                        : 'bg-bg-surface hover:bg-bg-elevated text-text-primary border border-border-subtle'
                    }`}
                  >
                    {activeScenario === sc.id ? 'Engaged (Active)' : 'Engage Scenario'}
                  </button>
                </div>
              ))}
          </div>
        </div>

        {/* Infrastructure & Network Failure Scenarios */}
        <div>
          <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
            <WifiOff className="w-4 h-4" />
            <span>Infrastructure Fault & Offline Edge Resiliency Scenarios</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {scenarios
              .filter((s: any) => s.hazard === 'GENERAL' && s.id !== 'RESET')
              .map((sc: any) => (
                <div
                  key={sc.id}
                  className={`bg-bg-secondary p-3 rounded-lg border transition-all flex flex-col justify-between ${
                    activeScenario === sc.id ? 'border-purple-400 bg-purple-500/10 shadow-lg' : 'border-border-subtle'
                  }`}
                >
                  <div>
                    <div className="font-bold text-xs text-text-primary">{sc.name}</div>
                    <div className="text-[10px] text-text-muted mt-1 leading-relaxed">{sc.desc}</div>
                  </div>
                  <button
                    aria-label={`Engage ${sc.name}`}
                    onClick={() => handleTrigger(sc.id)}
                    disabled={loadingScenario === sc.id}
                    className={`mt-3 w-full py-1 rounded text-xs font-bold transition-colors ${
                      activeScenario === sc.id
                        ? 'bg-purple-500 text-white'
                        : 'bg-bg-surface hover:bg-bg-elevated text-text-primary border border-border-subtle'
                    }`}
                  >
                    {activeScenario === sc.id ? 'Active' : 'Engage'}
                  </button>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};
