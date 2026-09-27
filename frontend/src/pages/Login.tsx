import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAuthMode, login } from '../services/api';
import {
  ArrowRight,
  Eye,
  EyeOff,
  KeyRound,
  Radio,
  Satellite,
  ShieldAlert,
  UserRound,
} from 'lucide-react';

const DOMAINS = [
  ['JALA-01', 'Flood & River Surge Hydrodynamics', 'cyan'],
  ['AGNI-02', 'Fire, Smoke & Gas AI Inference', 'orange'],
  ['BHUMI-03', 'Geotechnical Slope & Landslide Shear', 'green'],
  ['VAYU-04', 'Air Quality & Gas Intelligence', 'yellow'],
  ['AKASHA-05', 'Atmospheric & Weather Intelligence', 'violet'],
] as const;

const ALERTS = [
  { left: '57%', top: '19%', delay: '0s' },
  { left: '59%', top: '35%', delay: '-.7s' },
  { left: '73%', top: '44%', delay: '-1.4s' },
  { left: '62%', top: '59%', delay: '-2.1s' },
  { left: '65%', top: '72%', delay: '-2.8s' },
] as const;

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [devBypass, setDevBypass] = useState(false);
  const [pointer, setPointer] = useState({ x: 0, y: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    fetchAuthMode()
      .then((data) => setDevBypass(Boolean(data.dev_auth_bypass)))
      .catch(() => setDevBypass(false));
  }, []);

  const parallax = useMemo(
    () => ({
      far: `translate3d(${pointer.x * -4}px, ${pointer.y * -3}px, 0) scale(1.025)`,
      mid: `translate3d(${pointer.x * 8}px, ${pointer.y * 5}px, 0)`,
      near: `translate3d(${pointer.x * 14}px, ${pointer.y * 9}px, 0)`,
    }),
    [pointer],
  );

  const onPointerMove = (event: React.PointerEvent<HTMLElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    setPointer({ x, y });
  };

  const onPointerLeave = () => setPointer({ x: 0, y: 0 });

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await login(username, password);
      localStorage.setItem('prahari_token', data.access_token);
      localStorage.setItem('prahari_user', JSON.stringify(data.user));
      navigate('/');
    } catch (err: any) {
      setError(err?.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillLocalDemo = (user: string) => {
    setUsername(user);
    setPassword('local-demo');
  };

  return (
    <main
      className="prahari-cinema-login relative min-h-screen overflow-hidden bg-[#020812] text-white"
      onPointerMove={onPointerMove}
      onPointerLeave={onPointerLeave}
    >
      <section className="prahari-cinema-stage absolute inset-y-0 left-0 hidden overflow-hidden lg:block">
        <div
          className="prahari-cinema-base absolute inset-y-0 left-0"
          style={{ transform: parallax.far }}
          aria-hidden="true"
        >
          <img src="/prahari-login-cinematic.png" alt="" draggable={false} />
        </div>

        <div className="prahari-cinema-night absolute inset-0" aria-hidden="true" />
        <div className="prahari-cinema-grid absolute inset-0" aria-hidden="true" />
        <div className="prahari-cinema-scanlines absolute inset-0" aria-hidden="true" />

        <div className="prahari-cloud prahari-cloud-a" style={{ transform: parallax.mid }} aria-hidden="true" />
        <div className="prahari-cloud prahari-cloud-b" style={{ transform: parallax.mid }} aria-hidden="true" />
        <div className="prahari-cloud prahari-cloud-c" style={{ transform: parallax.near }} aria-hidden="true" />

        <div className="prahari-ocean-zone" style={{ transform: parallax.mid }} aria-hidden="true">
          <div className="prahari-ocean-shimmer" />
          <div className="prahari-ocean-wave prahari-ocean-wave-one" />
          <div className="prahari-ocean-wave prahari-ocean-wave-two" />
        </div>

        <div className="prahari-cyclone" style={{ transform: parallax.near }} aria-hidden="true">
          <div className="prahari-cyclone-arm prahari-cyclone-arm-one" />
          <div className="prahari-cyclone-arm prahari-cyclone-arm-two" />
          <div className="prahari-cyclone-eye" />
        </div>

        <div className="prahari-satellite-wrap" style={{ transform: parallax.near }} aria-hidden="true">
          <Satellite className="prahari-satellite-icon" />
          <div className="prahari-satellite-halo" />
        </div>
        <div className="prahari-satellite-beam" aria-hidden="true" />
        <div className="prahari-satellite-beam-core" aria-hidden="true" />

        <div className="prahari-radar-disc" style={{ transform: parallax.mid }} aria-hidden="true">
          <div className="prahari-radar-ring prahari-radar-ring-one" />
          <div className="prahari-radar-ring prahari-radar-ring-two" />
          <div className="prahari-radar-ring prahari-radar-ring-three" />
          <div className="prahari-radar-sector" />
        </div>

        {ALERTS.map((alert, index) => (
          <div
            key={`${alert.left}-${alert.top}`}
            className="prahari-alert-beacon"
            style={{
              left: alert.left,
              top: alert.top,
              animationDelay: alert.delay,
              transform: parallax.near,
            }}
            aria-hidden="true"
          >
            <div className="prahari-alert-core">!</div>
            <span className="prahari-alert-ring prahari-alert-ring-a" />
            <span className="prahari-alert-ring prahari-alert-ring-b" />
          </div>
        ))}

        <div className="prahari-energy-arc prahari-energy-arc-one" aria-hidden="true" />
        <div className="prahari-energy-arc prahari-energy-arc-two" aria-hidden="true" />
        <div className="prahari-energy-arc prahari-energy-arc-three" aria-hidden="true" />

        <div className="prahari-scene-depth absolute inset-0" aria-hidden="true" />
      </section>

      <section className="prahari-cinema-mobile absolute inset-0 lg:hidden" aria-hidden="true">
        <div className="prahari-mobile-radar" />
        <div className="prahari-mobile-cloud" />
      </section>

      <div className="sr-only">
        <h1>पंजापुतम</h1>
        <p>PRAHARI-NET — Predictive Resilient Autonomous Hazard &amp; Risk Intelligence Network</p>
        {DOMAINS.map(([id]) => <span key={id}>{id}</span>)}
      </div>

      <section className="relative z-30 flex min-h-screen items-center justify-center p-5 lg:justify-end lg:px-[3.1vw] lg:py-[4vh]">
        <div className="prahari-auth-card flex w-full max-w-md flex-col justify-center rounded-[22px] border p-6 sm:p-8 lg:min-h-[72vh] lg:w-[31.5vw] lg:max-w-[535px] lg:min-w-[440px] lg:p-[2.15vw]">
          {devBypass && (
            <div
              role="status"
              className="mb-6 border border-[#d4a400] bg-[#101c24]/95 px-4 py-3 text-center text-[11px] font-black uppercase tracking-[0.06em] text-[#ffc400]"
            >
              DEV AUTH BYPASS — LOCAL DEVELOPMENT ONLY
            </div>
          )}

          <header className="mb-7">
            <div className="mb-2 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.08em] text-cyan-300">
              <Radio className="h-4 w-4" />
              COMMAND &amp; CONTROL ACCESS
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white">
              Operator Authentication
            </h2>
            <p className="mt-2 max-w-md text-[13px] leading-5 text-[#8ba9c7]">
              Enter registered credentials to unlock local emergency command dispatch.
            </p>
          </header>

          {error && (
            <div className="mb-5 flex items-start gap-2 rounded-lg border border-red-400/40 bg-red-500/10 p-3 text-xs text-red-200">
              <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label htmlFor="login-username" className="mb-2 block text-[11px] font-bold uppercase tracking-[0.04em] text-[#82a9d3]">
                Username
              </label>
              <div className="relative">
                <UserRound className="absolute left-4 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-[#6c93bc]" />
                <input
                  id="login-username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="Registered operator"
                  className="prahari-auth-input h-12 w-full rounded-[14px] pl-12 pr-4 text-sm font-semibold text-white outline-none placeholder:text-[#5d7186]"
                />
              </div>
            </div>

            <div>
              <label htmlFor="login-password" className="mb-2 block text-[11px] font-bold uppercase tracking-[0.04em] text-[#82a9d3]">
                Password
              </label>
              <div className="relative">
                <KeyRound className="absolute left-4 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-[#6c93bc]" />
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Password"
                  className="prahari-auth-input h-12 w-full rounded-[14px] pl-12 pr-12 text-sm font-semibold text-white outline-none placeholder:text-[#5d7186]"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-2 text-[#d9ad3e] transition hover:bg-white/5 hover:text-[#ffd76d]"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="prahari-access-button group flex h-12 w-full items-center justify-center gap-3 rounded-[14px] text-sm font-black text-[#08111b] disabled:cursor-not-allowed disabled:opacity-55"
            >
              <span>{loading ? 'Authenticating secure session…' : 'Access Command Centre'}</span>
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </button>
          </form>

          {devBypass && (
            <div className="mt-7 border-t border-[#28445d] pt-5">
              <div className="mb-3 text-[11px] font-bold uppercase tracking-[0.04em] text-[#829db8]">
                Fast jury demo credentials
              </div>
              <div className="flex flex-wrap gap-2">
                {[
                  ['operator', 'Operator (Field Officer)'],
                  ['admin', 'Admin (EOC Director)'],
                  ['viewer', 'Viewer (Observer)'],
                ].map(([user, label]) => (
                  <button
                    key={user}
                    type="button"
                    onClick={() => fillLocalDemo(user)}
                    className="rounded-full border border-[#355776] bg-[#0a1c2e] px-3 py-1.5 text-[11px] text-[#c7dbef] transition hover:border-cyan-300/50 hover:bg-cyan-300/5"
                  >
                    {label}
                  </button>
                ))}
              </div>
              <p className="mt-3 text-[10px] leading-4 text-[#607991]">
                Local-development shortcuts are available only while development bypass is enabled.
              </p>
            </div>
          )}

          {!devBypass && (
            <div className="mt-7 border-t border-[#28445d] pt-5 text-[10px] uppercase tracking-[0.08em] text-[#66839d]">
              Secure production authentication • provenance-aware access
            </div>
          )}
        </div>
      </section>
    </main>
  );
};