import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAuthMode, login } from '../services/api';
import { Radio, ShieldAlert, Key, User, ArrowRight } from 'lucide-react';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('operator');
  const [password, setPassword] = useState('prahari2026!');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [devBypass, setDevBypass] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAuthMode().then((data) => setDevBypass(Boolean(data.dev_auth_bypass))).catch(() => setDevBypass(false));
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await login(username, password);
      localStorage.setItem('prahari_token', data.access_token);
      localStorage.setItem('prahari_user', JSON.stringify(data.user));
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = (user: string) => {
    setUsername(user);
    setPassword('prahari2026!');
  };

  return (
    <div className="min-h-screen w-full flex bg-[#07111F] text-[#F1F5F9] select-none">
      {/* Left: Brand Identity & Problem Statement intent */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 bg-[#0B1726] border-r border-[#22364A] relative overflow-hidden">
        {/* Subtle background tactical radar motif */}
        <div
          className="absolute inset-0 pointer-events-none opacity-20"
          style={{
            backgroundImage: `radial-gradient(circle at 70% 30%, rgba(39, 199, 232, 0.15) 0%, transparent 60%),
                              linear-gradient(#102033 1px, transparent 1px),
                              linear-gradient(90deg, #102033 1px, transparent 1px)`,
            backgroundSize: '100% 100%, 40px 40px, 40px 40px',
          }}
        />

        <div className="relative z-10 space-y-6">
          <div className="flex items-center space-x-3">
            <img src="/logo.svg" alt="PRAHARI Logo" className="w-12 h-12" />
            <div>
              <h1 className="text-xl font-bold tracking-wider text-text-primary">PRAHARI-NET</h1>
              <div className="text-xs tracking-widest text-accent-info font-medium">
                SENSE • PREDICT • ALERT • PROTECT
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-8 max-w-lg">
            <span className="text-[11px] font-mono uppercase bg-accent-ai/20 text-accent-ai px-2.5 py-1 rounded font-bold border border-accent-ai/30">
              Smart India Hackathon 2026 • SIH26178
            </span>
            <h2 className="text-2xl font-bold text-text-primary leading-snug">
              Predictive Resilient Autonomous Hazard & Risk Intelligence Network
            </h2>
            <p className="text-xs text-text-secondary leading-relaxed pt-2">
              Empowering communities to shift from reactive disaster response to proactive risk prevention through localized multi-sensor LoRa networks, hybrid physical AI, and autonomous local edge computing.
            </p>
          </div>
        </div>

        {/* 3 Node Capabilities Strip */}
        <div className="relative z-10 grid grid-cols-3 gap-3 border-t border-[#22364A] pt-6 text-xs">
          <div>
            <div className="font-bold text-accent-info">JALA-01</div>
            <div className="text-[11px] text-text-muted mt-0.5">Flood & River Surge Hydrodynamics</div>
          </div>
          <div>
            <div className="font-bold text-hazard-warning">AGNI-02</div>
            <div className="text-[11px] text-text-muted mt-0.5">Fire, Smoke & Gas AI Inference</div>
          </div>
          <div>
            <div className="font-bold text-hazard-normal">BHUMI-03</div>
            <div className="text-[11px] text-text-muted mt-0.5">Geotechnical Slope & Landslide Shear</div>
          </div>
        </div>
      </div>

      {/* Right: Authentication Portal */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12">
        <div className="max-w-md w-full space-y-6 bg-bg-secondary p-8 rounded-xl border border-border-subtle shadow-2xl">
          {devBypass && (
            <div role="status" className="border border-hazard-watch/50 bg-hazard-watch/10 px-3 py-2 text-[11px] font-bold tracking-wider text-hazard-watch">
              DEV AUTH BYPASS — LOCAL DEVELOPMENT ONLY
            </div>
          )}
          <div>
            <div className="flex items-center space-x-2 text-accent-info text-xs font-semibold uppercase tracking-wider mb-1">
              <Radio className="w-4 h-4" />
              <span>Command & Control Access</span>
            </div>
            <h2 className="text-lg font-bold text-text-primary">Operator Authentication</h2>
            <p className="text-xs text-text-muted mt-0.5">
              Enter registered credentials to unlock local emergency command dispatch.
            </p>
          </div>

          {error && (
            <div className="bg-hazard-critical/20 border border-hazard-critical text-hazard-critical p-3 rounded text-xs flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="login-username" className="text-[11px] text-text-secondary uppercase tracking-wider block mb-1">
                Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-3 text-text-muted" />
                <input
                  id="login-username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-bg-surface border border-border-subtle rounded-lg pl-9 pr-3 py-2 text-xs text-text-primary focus:outline-none focus:border-accent-info"
                />
              </div>
            </div>

            <div>
              <label htmlFor="login-password" className="text-[11px] text-text-secondary uppercase tracking-wider block mb-1">
                Password
              </label>
              <div className="relative">
                <Key className="w-4 h-4 absolute left-3 top-3 text-text-muted" />
                <input
                  id="login-password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-bg-surface border border-border-subtle rounded-lg pl-9 pr-3 py-2 text-xs text-text-primary focus:outline-none focus:border-accent-info"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-accent-info hover:bg-cyan-400 text-bg-primary font-bold rounded-lg text-xs transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating...' : 'Access Command Centre'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Seed Demo Account Quick Selectors */}
          <div className="pt-4 border-t border-border-subtle text-xs space-y-2">
            <span className="text-[10px] uppercase font-semibold text-text-muted tracking-wider block">
              Fast Jury Demo Credentials
            </span>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => handleFillDemo('operator')}
                className="px-2.5 py-1 bg-bg-surface hover:bg-bg-elevated border border-border-subtle rounded text-[11px] text-text-secondary hover:text-text-primary transition-colors"
              >
                Operator (Field Officer)
              </button>
              <button
                type="button"
                onClick={() => handleFillDemo('admin')}
                className="px-2.5 py-1 bg-bg-surface hover:bg-bg-elevated border border-border-subtle rounded text-[11px] text-text-secondary hover:text-text-primary transition-colors"
              >
                Admin (EOC Director)
              </button>
              <button
                type="button"
                onClick={() => handleFillDemo('viewer')}
                className="px-2.5 py-1 bg-bg-surface hover:bg-bg-elevated border border-border-subtle rounded text-[11px] text-text-secondary hover:text-text-primary transition-colors"
              >
                Viewer (Observer)
              </button>
            </div>
            <p className="text-[10px] text-text-muted pt-1">
              Password for all demo accounts: <code className="text-accent-info font-mono">prahari2026!</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
