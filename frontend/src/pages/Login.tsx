import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAuthMode, login } from '../services/api';
import {
  ArrowRight,
  CloudLightning,
  Eye,
  EyeOff,
  Key,
  Radio,
  Radar,
  Satellite,
  ShieldAlert,
  User,
} from 'lucide-react';

const PANCHA = [
  ['जल (JALA)', 'JALA-01', 'Flood & river surge intelligence', 'text-cyan-300'],
  ['अग्नि (AGNI)', 'AGNI-02', 'Fire, smoke & thermal intelligence', 'text-orange-300'],
  ['भूमि (BHUMI)', 'BHUMI-03', 'Landslide & geotechnical intelligence', 'text-emerald-300'],
  ['वायु (VAYU)', 'VAYU-04', 'Air, smoke & gas intelligence', 'text-violet-300'],
  ['आकाश (AKASHA)', 'AKASHA-05', 'Atmospheric & weather intelligence', 'text-sky-300'],
] as const;

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [devBypass, setDevBypass] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAuthMode()
      .then((data) => setDevBypass(Boolean(data.dev_auth_bypass)))
      .catch(() => setDevBypass(false));
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
    setPassword('local-demo');
  };

  return (
    <div className="prahari-login min-h-screen w-full overflow-hidden bg-[#020711] text-[#F1F5F9] lg:grid lg:grid-cols-[1.08fr_0.92fr]">
      <section className="prahari-login-scene relative hidden min-h-screen overflow-hidden border-r border-cyan-400/10 lg:flex lg:flex-col lg:justify-between">
        <div className="prahari-login-grid absolute inset-0" aria-hidden="true" />
        <div className="prahari-india-orbit absolute inset-0" aria-hidden="true">
          <div className="prahari-orbit prahari-orbit-one" />
          <div className="prahari-orbit prahari-orbit-two" />
          <div className="prahari-radar-sweep" />
          <div className="prahari-storm-cell prahari-storm-one" />
          <div className="prahari-storm-cell prahari-storm-two" />
          <div className="prahari-signal-point prahari-signal-jala" />
          <div className="prahari-signal-point prahari-signal-agni" />
          <div className="prahari-signal-point prahari-signal-bhumi" />
          <div className="prahari-signal-point prahari-signal-vayu" />
          <div className="prahari-signal-point prahari-signal-akasha" />
        </div>

        <div className="relative z-10 px-10 pt-9 xl:px-14 xl:pt-12">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 rounded-full bg-cyan-300/20 blur-xl" />
              <img src="/logo.svg" alt="PRAHARI Logo" className="relative h-12 w-12" />
            </div>
            <div>
              <div className="text-lg font-black tracking-[0.18em] text-white">PRAHARI-NET</div>
              <div className="text-[10px] font-semibold tracking-[0.24em] text-cyan-300">SENSE • PREDICT • ALERT • PROTECT</div>
            </div>
          </div>

          <div className="mt-10 max-w-3xl xl:mt-14">
            <div className="mb-4 flex flex-wrap items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em]">
              <span className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-cyan-200">Smart India Hackathon 2026</span>
              <span className="rounded-full border border-violet-300/25 bg-violet-300/10 px-3 py-1 text-violet-200">SIH26178</span>
            </div>

            <h1 className="prahari-devanagari text-5xl font-black tracking-tight text-white drop-shadow-[0_0_30px_rgba(34,211,238,0.22)] xl:text-7xl">
              पंजापुतम
            </h1>
            <div className="mt-1 text-sm font-semibold tracking-[0.22em] text-cyan-200/80">PANJAPUTHAM</div>
            <h2 className="mt-6 max-w-2xl text-2xl font-semibold leading-tight text-slate-100 xl:text-3xl">
              Predictive Resilient Autonomous Hazard &amp; Risk Intelligence Network
            </h2>
            <p className="mt-4 max-w-xl text-sm leading-6 text-slate-400">
              A five-domain environmental intelligence fabric for evidence-aware sensing, prediction, alerting and resilient local response.
            </p>

            <div className="mt-7 flex flex-wrap gap-2 text-[10px] font-semibold tracking-wide text-slate-300">
              <span className="flex items-center gap-1.5 rounded-full border border-cyan-300/20 bg-black/20 px-3 py-1.5"><Radar className="h-3.5 w-3.5 text-cyan-300" /> EDGE INTELLIGENCE</span>
              <span className="flex items-center gap-1.5 rounded-full border border-violet-300/20 bg-black/20 px-3 py-1.5"><Satellite className="h-3.5 w-3.5 text-violet-300" /> GEO OPERATIONS</span>
              <span className="flex items-center gap-1.5 rounded-full border border-amber-300/20 bg-black/20 px-3 py-1.5"><CloudLightning className="h-3.5 w-3.5 text-amber-300" /> MULTI-HAZARD</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 grid grid-cols-5 gap-2 px-10 pb-9 xl:px-14 xl:pb-12">
          {PANCHA.map(([label, id, description, tone]) => (
            <div key={id} className="min-w-0 rounded-xl border border-white/10 bg-slate-950/45 p-3 backdrop-blur-xl">
              <div className={`text-[11px] font-black ${tone}`}>{label}</div>
              <div className="mt-0.5 text-[9px] font-mono text-slate-500">{id}</div>
              <div className="mt-2 text-[9px] leading-4 text-slate-400">{description}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="relative flex min-h-screen items-center justify-center overflow-hidden p-5 sm:p-8 lg:p-12">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_65%_20%,rgba(34,211,238,0.10),transparent_28%),radial-gradient(circle_at_25%_80%,rgba(124,58,237,0.10),transparent_30%)]" aria-hidden="true" />
        <div className="prahari-login-card relative z-10 w-full max-w-md rounded-2xl border border-cyan-300/15 bg-[#07111F]/90 p-6 shadow-[0_30px_90px_rgba(0,0,0,0.55),0_0_0_1px_rgba(34,211,238,0.04)] backdrop-blur-2xl sm:p-8">
          <div className="mb-5 lg:hidden">
            <div className="prahari-devanagari text-3xl font-black text-white">पंजापुतम</div>
            <div className="mt-1 text-[9px] font-bold tracking-[0.18em] text-cyan-300">PRAHARI-NET · PANJAPUTHAM</div>
          </div>
          {devBypass && (
            <div role="status" className="mb-5 rounded-lg border border-amber-400/30 bg-amber-400/10 px-3 py-2 text-[10px] font-bold tracking-[0.14em] text-amber-300">
              DEV AUTH BYPASS — LOCAL DEVELOPMENT ONLY
            </div>
          )}

          <div className="mb-6">
            <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-cyan-300">
              <Radio className="h-4 w-4" />
              Secure Command Access
            </div>
            <h2 className="text-xl font-bold text-white">Operator Authentication</h2>
            <p className="mt-1 text-xs leading-5 text-slate-400">Authenticate to enter the PRAHARI environmental command workspace.</p>
          </div>

          {error && (
            <div className="mb-4 flex items-start gap-2 rounded-lg border border-red-400/35 bg-red-500/10 p-3 text-xs text-red-200">
              <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="login-username" className="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">Username</label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
                <input
                  id="login-username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full rounded-lg border border-slate-700/80 bg-slate-950/70 py-2.5 pl-9 pr-3 text-sm text-white outline-none transition focus:border-cyan-300/70 focus:ring-2 focus:ring-cyan-300/10"
                  placeholder="Registered operator"
                />
              </div>
            </div>

            <div>
              <label htmlFor="login-password" className="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">Password</label>
              <div className="relative">
                <Key className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-700/80 bg-slate-950/70 py-2.5 pl-9 pr-10 text-sm text-white outline-none transition focus:border-cyan-300/70 focus:ring-2 focus:ring-cyan-300/10"
                  placeholder="Password"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute right-2 top-2 rounded p-1.5 text-slate-500 transition hover:bg-white/5 hover:text-cyan-200"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="group flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-cyan-300 to-cyan-400 py-2.5 text-xs font-black text-slate-950 shadow-[0_0_25px_rgba(34,211,238,0.18)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating secure session…' : 'Access Command Centre'}</span>
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </button>
          </form>

          {devBypass && (
            <div className="mt-6 border-t border-slate-700/70 pt-4 text-xs">
              <div className="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">Local jury demo shortcuts</div>
              <div className="flex flex-wrap gap-2">
                {['operator', 'admin', 'viewer'].map((user) => (
                  <button key={user} type="button" onClick={() => handleFillDemo(user)} className="rounded-md border border-slate-700 bg-slate-900 px-2.5 py-1 text-[10px] capitalize text-slate-300 transition hover:border-cyan-300/40 hover:text-cyan-200">
                    {user}
                  </button>
                ))}
              </div>
              <p className="mt-2 text-[9px] text-slate-600">Local bypass uses a non-production placeholder credential and is unavailable when production bypass is disabled.</p>
            </div>
          )}

          <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-4 text-[9px] font-semibold tracking-[0.12em] text-slate-600">
            <span>SECURE • PROVENANCE-AWARE</span>
            <span>PRAHARI-NET</span>
          </div>
        </div>
      </section>
    </div>
  );
};
