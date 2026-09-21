import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { triggerScenario, resetSimulator } from '../services/api';
import { PlaySquare, CheckCircle, ArrowRight, RotateCcw, AlertTriangle, ShieldCheck, WifiOff, Radio, Droplets, Flame, Mountain } from 'lucide-react';

export const DemoWalkthroughPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [running, setRunning] = useState<boolean>(false);

  const steps = [
    {
      num: 1,
      title: 'Nominal Baseline Fleet State',
      scenario: 'ALL_NORMAL',
      desc: 'All 3 edge nodes report green nominal baseline telemetry over LoRa.',
      expected: 'JALA < 40cm, AGNI MQ-2 ~115, BHUMI tilt ~0.12° (Risk < 25% NORMAL)',
      hazard: 'ALL',
    },
    {
      num: 2,
      title: 'JALA-01 Hydrological Rise (Normal → Watch)',
      scenario: 'FLOOD_RAMP',
      desc: 'Upstream catchment rainfall initiates gradual river rise to 75 cm.',
      expected: 'Kinematic rate of rise detected; transitions to WATCH (score ~38%)',
      hazard: 'FLOOD',
    },
    {
      num: 3,
      title: 'Flash Flood Escalation (Watch → Warning → Critical)',
      scenario: 'FLASH_FLOOD',
      desc: 'Torrential 115 mm/hr downpour accelerates water rise over 180cm threshold.',
      expected: 'Breach window estimated ~12–16 min; CRITICAL FLOOD alert created',
      hazard: 'FLOOD',
    },
    {
      num: 4,
      title: 'Mitigation & Reset',
      scenario: 'RESET',
      desc: 'Flood waters recede back to nominal river bed datum.',
      expected: 'Alert auto-resolves or awaits operator acknowledge; state returns to NORMAL',
      hazard: 'ALL',
    },
    {
      num: 5,
      title: 'Sensor Trust Innovation: False Smoke Spike Suppressed',
      scenario: 'FALSE_SMOKE_SENSOR_SPIKE',
      desc: 'Isolated MQ-2 sensor glitch spikes to 850, but heat & optical flame are clear.',
      expected: 'Trust Engine lowers MQ-2 trust to 25%; avoids false critical panic siren!',
      hazard: 'FIRE',
    },
    {
      num: 6,
      title: 'Corroborated Wildfire Combustion (Critical Fire)',
      scenario: 'FIRE_DEVELOPMENT',
      desc: 'Active fire event: thermal rise + optical IR flame + 94% visual AI stream.',
      expected: 'Multi-Sensor Fusion corroborates; sounds rapid CRITICAL FIRE alarm',
      hazard: 'FIRE',
    },
    {
      num: 7,
      title: 'Mitigation & Reset',
      scenario: 'RESET',
      desc: 'Forest perimeter secured by response team; fire suppressed.',
      expected: 'Atmospheric sensors clear to baseline.',
      hazard: 'ALL',
    },
    {
      num: 8,
      title: 'BHUMI-03 Pore Saturation (Normal → Warning)',
      scenario: 'LANDSLIDE_SATURATION',
      desc: 'Prolonged rainfall context saturates hillside soil pore-water to 88%.',
      expected: 'Soil saturation warning flagged; inclinometer starts drift tracking',
      hazard: 'LANDSLIDE',
    },
    {
      num: 9,
      title: 'Slope Shear Movement (Critical Landslide)',
      scenario: 'LANDSLIDE_MOVEMENT',
      desc: 'Saturated slope experiences structural shear slip; tilt > 4.5°, geophone vib > 14g.',
      expected: 'CRITICAL LANDSLIDE alarm sounds; road closure advisory triggered',
      hazard: 'LANDSLIDE',
    },
    {
      num: 10,
      title: 'Internet Severed (Local Edge Sovereignty)',
      scenario: 'INTERNET_OUTAGE',
      desc: 'External WAN cable cut simulated; zero internet access available.',
      expected: 'System switches to LOCAL EDGE badge; sensing, LoRa, backend, alerts continue 100% locally!',
      hazard: 'NETWORK',
    },
    {
      num: 11,
      title: 'Full Recovery & Factory Reset',
      scenario: 'RECOVERY',
      desc: 'WAN connectivity restored; queued sync items processed; nominal baseline restored.',
      expected: 'All 3 nodes online, zero unacknowledged alarms, green healthy status.',
      hazard: 'ALL',
    },
  ];

  const handleStepClick = async (step: any) => {
    setCurrentStep(step.num);
    setRunning(true);
    try {
      if (step.scenario === 'RESET' || step.scenario === 'RECOVERY') {
        await resetSimulator();
      } else {
        await triggerScenario(step.scenario);
      }
    } catch (e) {
      console.error('Error triggering step:', e);
    } finally {
      setRunning(false);
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      const nextStep = steps.find((s) => s.num === currentStep + 1);
      if (nextStep) handleStepClick(nextStep);
    }
  };

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
              <PlaySquare className="w-5 h-5 text-accent-ai" />
              <span>Smart India Hackathon 2026 — Official 5-Minute Jury Demonstration</span>
            </h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded border bg-purple-500/20 text-purple-300 border-purple-400/40">
              SIH26178 • QUALCOMM
            </span>
          </div>
          <p className="text-xs text-text-muted mt-0.5">
            Structured step-by-step evaluation demonstrating Flood, Fire, Landslide, Sensor Trust, and Zero-Internet Edge Resilience.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => navigate('/')}
            className="px-3 py-1.5 bg-bg-surface hover:bg-bg-elevated text-text-primary rounded border border-border-subtle transition-colors"
          >
            Open Command Centre
          </button>
          <button
            onClick={handleNext}
            disabled={currentStep >= steps.length || running}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-accent-ai hover:bg-purple-600 text-white font-bold rounded transition-colors disabled:opacity-50"
          >
            <span>Execute Next Step</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Step Sequence Timeline */}
      <div className="space-y-2.5">
        {steps.map((s) => {
          const isCurrent = currentStep === s.num;
          const isPassed = currentStep > s.num;

          return (
            <div
              key={s.num}
              onClick={() => handleStepClick(s)}
              className={`p-4 rounded-lg border transition-all cursor-pointer flex flex-col md:flex-row items-start md:items-center justify-between gap-3 ${
                isCurrent
                  ? 'bg-bg-surface border-accent-ai shadow-xl'
                  : isPassed
                  ? 'bg-bg-secondary/70 border-hazard-normal/30 opacity-80'
                  : 'bg-bg-secondary border-border-subtle hover:border-border-active'
              }`}
            >
              <div className="flex items-start space-x-3.5">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 font-bold text-xs ${
                    isCurrent
                      ? 'bg-accent-ai text-white'
                      : isPassed
                      ? 'bg-hazard-normal/20 text-hazard-normal border border-hazard-normal'
                      : 'bg-bg-surface text-text-muted border border-border-subtle'
                  }`}
                >
                  {isPassed ? <CheckCircle className="w-4 h-4" /> : s.num}
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-xs font-bold text-text-primary">{s.title}</h3>
                    <span className="text-[10px] font-mono bg-bg-surface px-2 py-0.2 rounded border border-border-subtle text-text-muted">
                      {s.scenario}
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary mt-0.5">{s.desc}</p>
                  <p className="text-[11px] text-accent-info font-mono mt-1">Expected: {s.expected}</p>
                </div>
              </div>

              <div className="shrink-0 flex items-center space-x-2 self-end md:self-center">
                {isCurrent && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-accent-ai text-white uppercase animate-pulse">
                    ACTIVE STAGE
                  </span>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleStepClick(s);
                  }}
                  className="px-2.5 py-1 text-[11px] rounded bg-bg-surface hover:bg-bg-elevated border border-border-subtle text-text-primary font-semibold"
                >
                  Trigger
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
