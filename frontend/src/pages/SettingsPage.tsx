import React, { useState, useEffect } from 'react';
import { fetchSettings, saveSettings } from '../services/api';
import { Sliders, Save, RotateCcw, ShieldAlert, Radio, Volume2, Cpu, CheckCircle } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<any>(null);
  const [savedStatus, setSavedStatus] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings().then(setSettings).catch(console.error);
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await saveSettings(settings);
      setSavedStatus('Settings successfully saved & synced across active nodes.');
      setTimeout(() => setSavedStatus(null), 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
    }
  };

  if (!settings) {
    return <div className="p-8 text-center text-text-muted text-xs">Loading system settings...</div>;
  }

  return (
    <div className="p-4 space-y-4 max-w-5xl mx-auto select-text">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <div>
          <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-accent-info" />
            <span>Platform Configuration & Prototype Thresholds</span>
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Calibrate operational risk bands, physical sensor thresholds, and hardware serial communication parameters.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="flex items-center space-x-1.5 px-4 py-2 bg-accent-info hover:bg-cyan-400 text-bg-primary font-bold rounded text-xs transition-colors"
        >
          <Save className="w-4 h-4" />
          <span>Save System Settings</span>
        </button>
      </div>

      {savedStatus && (
        <div className="bg-hazard-normal/20 border border-hazard-normal text-hazard-normal p-3 rounded-lg text-xs flex items-center space-x-2">
          <CheckCircle className="w-4 h-4" />
          <span>{savedStatus}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-4">
        {/* Prototype Risk Bands */}
        <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-purple-400" />
            <span>Prototype Risk Assessment Bands (0 - 100)</span>
          </h3>
          <p className="text-[11px] text-text-muted">
            *Explicit disclaimer: These are engineering prototype thresholds and do not supersede official government disaster guidelines.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <label className="text-[10px] text-text-muted uppercase">Normal Ceiling</label>
              <input
                type="number"
                value={settings.risk_bands?.normal_max || 25}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    risk_bands: { ...settings.risk_bands, normal_max: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted uppercase">Watch Ceiling</label>
              <input
                type="number"
                value={settings.risk_bands?.watch_max || 50}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    risk_bands: { ...settings.risk_bands, watch_max: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted uppercase">Warning Ceiling</label>
              <input
                type="number"
                value={settings.risk_bands?.warning_max || 75}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    risk_bands: { ...settings.risk_bands, warning_max: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted uppercase">Critical Ceiling</label>
              <input
                type="number"
                value={settings.risk_bands?.critical_max || 100}
                disabled
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-muted mt-1 font-mono opacity-60"
              />
            </div>
          </div>
        </div>

        {/* JALA-01 Flood Thresholds */}
        <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
          <h3 className="text-xs font-bold text-accent-info uppercase tracking-wider">
            JALA-01 Hydrological Thresholds
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <label className="text-[10px] text-text-muted">Watch Water Level (cm)</label>
              <input
                type="number"
                value={settings.jala_thresholds?.watch_level_cm || 60}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    jala_thresholds: { ...settings.jala_thresholds, watch_level_cm: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted">Warning Water Level (cm)</label>
              <input
                type="number"
                value={settings.jala_thresholds?.warning_level_cm || 120}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    jala_thresholds: { ...settings.jala_thresholds, warning_level_cm: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted">Critical River Datum (cm)</label>
              <input
                type="number"
                value={settings.jala_thresholds?.critical_level_cm || 180}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    jala_thresholds: { ...settings.jala_thresholds, critical_level_cm: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
          </div>
        </div>

        {/* AGNI-02 Fire Thresholds */}
        <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
          <h3 className="text-xs font-bold text-hazard-warning uppercase tracking-wider">
            AGNI-02 Combustion Gas & Smoke Thresholds
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <label className="text-[10px] text-text-muted">MQ-2 Smoke Warning Threshold (ADC)</label>
              <input
                type="number"
                value={settings.agni_thresholds?.mq2_warning_raw || 600}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    agni_thresholds: { ...settings.agni_thresholds, mq2_warning_raw: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted">Critical Thermal Spike (°C)</label>
              <input
                type="number"
                value={settings.agni_thresholds?.critical_temp_c || 50.0}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    agni_thresholds: { ...settings.agni_thresholds, critical_temp_c: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted">Visual AI Edge Confidence Trigger</label>
              <input
                type="number"
                step="0.05"
                value={settings.agni_thresholds?.vision_confidence_threshold || 0.70}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    agni_thresholds: { ...settings.agni_thresholds, vision_confidence_threshold: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
          </div>
        </div>

        {/* Hardware Serial Gateway */}
        <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle space-y-3">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-accent-info" />
            <span>LoRa USB Serial Concentrator Interface</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <label className="text-[10px] text-text-muted">COM Port (Windows)</label>
              <input
                type="text"
                value={settings.gateway?.port || 'COM3'}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    gateway: { ...settings.gateway, port: e.target.value },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted">Baud Rate</label>
              <input
                type="number"
                value={settings.gateway?.baud || 115200}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    gateway: { ...settings.gateway, baud: Number(e.target.value) },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-primary mt-1 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-text-muted">Gateway Operational Mode</label>
              <select
                value={settings.gateway?.mode || 'SIMULATOR'}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    gateway: { ...settings.gateway, mode: e.target.value },
                  })
                }
                className="w-full bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-secondary mt-1 font-mono focus:outline-none"
              >
                <option value="SIMULATOR">SIMULATOR (Autonomous In-Process)</option>
                <option value="REAL">REAL (Hardware USB Serial)</option>
              </select>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};
