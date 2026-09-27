import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAuthMode, login } from '../services/api';
import {
  Activity,
  ArrowRight,
  BarChart3,
  BellRing,
  Eye,
  EyeOff,
  KeyRound,
  Radio,
  Satellite,
  Shield,
  ShieldAlert,
  UserRound,
} from 'lucide-react';

const DOMAINS = [
  ['JALA-01', 'Flood & River Surge', 'Hydrodynamics', 'jala'],
  ['AGNI-02', 'Fire, Smoke & Gas', 'AI Inference', 'agni'],
  ['BHUMI-03', 'Geotechnical Slope', 'Landslide Shear', 'bhumi'],
  ['VAYU-04', 'Air Quality & Gas', 'Intelligence', 'vayu'],
  ['AKASHA-05', 'Atmospheric & Weather', 'Intelligence', 'akasha'],
] as const;

const ALERT_POINTS = [
  { x: 312, y: 118, delay: '0s' },
  { x: 344, y: 224, delay: '-.6s' },
  { x: 388, y: 322, delay: '-1.2s' },
  { x: 328, y: 420, delay: '-1.8s' },
  { x: 356, y: 510, delay: '-2.4s' },
] as const;

const RAIN_CELLS = [
  { cx: 332, cy: 174, rx: 62, ry: 31, rotate: -18, tone: 'cyan' },
  { cx: 355, cy: 244, rx: 74, ry: 38, rotate: 12, tone: 'green' },
  { cx: 377, cy: 316, rx: 80, ry: 42, rotate: -8, tone: 'yellow' },
  { cx: 346, cy: 392, rx: 64, ry: 35, rotate: 18, tone: 'orange' },
] as const;

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [devBypass, setDevBypass] = useState(false);
  const navigate = useNavigate();
  const sceneRef = useRef<HTMLDivElement>(null);

  const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
  const isLocalRuntime =
    hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname === '0.0.0.0';

  const showDevTools = devBypass && isLocalRuntime;

  useEffect(() => {
    fetchAuthMode()
      .then((data) => setDevBypass(Boolean(data.dev_auth_bypass)))
      .catch(() => setDevBypass(false));
  }, []);

  const handlePointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    const scene = sceneRef.current;
    if (!scene) return;

    const rect = scene.getBoundingClientRect();
    const nx = Math.max(-1, Math.min(1, ((event.clientX - rect.left) / rect.width - 0.5) * 2));
    const ny = Math.max(-1, Math.min(1, ((event.clientY - rect.top) / rect.height - 0.5) * 2));

    scene.style.setProperty('--px', `${nx * 12}px`);
    scene.style.setProperty('--py', `${ny * 9}px`);
    scene.style.setProperty('--npx', `${nx * -8}px`);
    scene.style.setProperty('--npy', `${ny * -6}px`);
  };

  const resetPointer = () => {
    const scene = sceneRef.current;
    if (!scene) return;
    scene.style.setProperty('--px', '0px');
    scene.style.setProperty('--py', '0px');
    scene.style.setProperty('--npx', '0px');
    scene.style.setProperty('--npy', '0px');
  };

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
    if (!showDevTools) return;
    setUsername(user);
    setPassword('local-demo');
  };

  return (
    <main className="prahari-native-login min-h-screen overflow-hidden bg-[#020812] text-white">
      <div className="prahari-native-layout min-h-screen">
        <section
          ref={sceneRef}
          onPointerMove={handlePointerMove}
          onPointerLeave={resetPointer}
          className="prahari-native-hero relative hidden min-h-screen overflow-hidden lg:flex lg:flex-col"
        >
          <div className="prahari-native-grid" aria-hidden="true" />
          <div className="prahari-native-stars" aria-hidden="true" />
          <div className="prahari-native-haze prahari-native-haze-a" aria-hidden="true" />
          <div className="prahari-native-haze prahari-native-haze-b" aria-hidden="true" />

          <div className="prahari-native-satellite" aria-hidden="true">
            <Satellite className="h-full w-full" />
          </div>
          <div className="prahari-native-beam" aria-hidden="true" />
          <div className="prahari-native-beam-core" aria-hidden="true" />

          <div className="prahari-native-map-stage" aria-hidden="true">
            <svg
              viewBox="0 0 560 650"
              role="presentation"
              className="prahari-native-india"
              preserveAspectRatio="xMidYMid meet"
            >
              <defs>
                <linearGradient id="indiaFill" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#061a2a" />
                  <stop offset="48%" stopColor="#0a2d43" />
                  <stop offset="100%" stopColor="#04111f" />
                </linearGradient>
                <linearGradient id="indiaStroke" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#43d9ff" />
                  <stop offset="50%" stopColor="#1c8ccc" />
                  <stop offset="100%" stopColor="#54e4ff" />
                </linearGradient>
                <radialGradient id="rainCyan">
                  <stop offset="0%" stopColor="#32e7ff" stopOpacity=".88" />
                  <stop offset="55%" stopColor="#1479ff" stopOpacity=".48" />
                  <stop offset="100%" stopColor="#1479ff" stopOpacity="0" />
                </radialGradient>
                <radialGradient id="rainGreen">
                  <stop offset="0%" stopColor="#7dff5f" stopOpacity=".94" />
                  <stop offset="55%" stopColor="#20c759" stopOpacity=".5" />
                  <stop offset="100%" stopColor="#20c759" stopOpacity="0" />
                </radialGradient>
                <radialGradient id="rainYellow">
                  <stop offset="0%" stopColor="#ffe85c" stopOpacity=".98" />
                  <stop offset="55%" stopColor="#ffad2f" stopOpacity=".58" />
                  <stop offset="100%" stopColor="#ffad2f" stopOpacity="0" />
                </radialGradient>
                <radialGradient id="rainOrange">
                  <stop offset="0%" stopColor="#ff5a32" stopOpacity=".96" />
                  <stop offset="55%" stopColor="#ff6d24" stopOpacity=".54" />
                  <stop offset="100%" stopColor="#ff6d24" stopOpacity="0" />
                </radialGradient>
                <filter id="indiaGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="5" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              <path
                className="prahari-india-shape"
                d="M240 36 L271 51 L291 71 L327 67 L352 84 L388 91 L413 112 L446 121 L455 142 L439 156 L412 158 L398 181 L379 188 L370 216 L355 235 L354 263 L338 287 L344 312 L327 335 L322 363 L308 388 L300 418 L286 445 L275 482 L260 519 L246 563 L226 605 L207 565 L195 520 L181 488 L169 455 L154 424 L145 389 L124 360 L119 331 L102 308 L98 274 L78 254 L82 229 L66 210 L73 187 L58 168 L74 148 L68 125 L88 108 L112 103 L127 83 L154 78 L172 58 L201 55 Z"
                fill="url(#indiaFill)"
                stroke="url(#indiaStroke)"
                strokeWidth="2"
                filter="url(#indiaGlow)"
              />

              <g className="prahari-india-internal">
                <path d="M126 112 C185 145 229 145 294 122" />
                <path d="M101 192 C162 214 225 207 335 177" />
                <path d="M112 281 C171 294 228 285 350 254" />
                <path d="M133 363 C187 357 239 346 322 322" />
                <path d="M161 444 C205 422 245 402 300 375" />
                <path d="M207 89 C205 175 213 249 220 332 C224 411 230 487 229 560" />
                <path d="M283 80 C267 154 262 226 255 297 C248 373 242 438 230 511" />
              </g>

              {RAIN_CELLS.map((cell, index) => (
                <ellipse
                  key={`${cell.cx}-${cell.cy}`}
                  className={`prahari-rain-cell prahari-rain-cell-${index}`}
                  cx={cell.cx}
                  cy={cell.cy}
                  rx={cell.rx}
                  ry={cell.ry}
                  transform={`rotate(${cell.rotate} ${cell.cx} ${cell.cy})`}
                  fill={`url(#rain${cell.tone[0].toUpperCase()}${cell.tone.slice(1)})`}
                />
              ))}

              {ALERT_POINTS.map((point) => (
                <g
                  key={`${point.x}-${point.y}`}
                  className="prahari-svg-alert"
                  transform={`translate(${point.x} ${point.y})`}
                  style={{ animationDelay: point.delay }}
                >
                  <circle r="18" className="prahari-svg-alert-ring" />
                  <circle r="10" className="prahari-svg-alert-core" />
                  <text textAnchor="middle" y="4">!</text>
                </g>
              ))}
            </svg>

            <div className="prahari-native-radar" aria-hidden="true">
              <div className="prahari-native-radar-ring ring-1" />
              <div className="prahari-native-radar-ring ring-2" />
              <div className="prahari-native-radar-ring ring-3" />
              <div className="prahari-native-radar-sweep" />
            </div>

            <div className="prahari-native-cyclone" aria-hidden="true">
              <span className="cyclone-arm cyclone-arm-a" />
              <span className="cyclone-arm cyclone-arm-b" />
              <span className="cyclone-arm cyclone-arm-c" />
              <span className="cyclone-eye" />
            </div>

            <div className="prahari-native-ocean" aria-hidden="true">
              <span className="ocean-line ocean-line-a" />
              <span className="ocean-line ocean-line-b" />
              <span className="ocean-line ocean-line-c" />
            </div>

            <div className="prahari-native-cloud cloud-a" aria-hidden="true" />
            <div className="prahari-native-cloud cloud-b" aria-hidden="true" />
            <div className="prahari-native-cloud cloud-c" aria-hidden="true" />
          </div>

          <div className="prahari-native-brand relative z-20">
            <div className="flex items-center gap-3">
              <div className="prahari-native-logo">
                <img src="/logo.svg" alt="PRAHARI-NET" className="h-12 w-12" />
              </div>
              <div>
                <div className="text-[22px] font-black tracking-[.08em]">PRAHARI-NET</div>
                <div className="text-[10px] font-black tracking-[.12em] text-cyan-300">
                  SENSE • PREDICT • ALERT • PROTECT
                </div>
              </div>
            </div>

            <div className="mt-10 inline-flex items-center rounded-full border border-violet-400/40 bg-violet-500/10 px-4 py-2 text-[10px] font-black tracking-[.08em] text-violet-300">
              SMART INDIA HACKATHON 2026&nbsp; • &nbsp;SIH26178
            </div>

            <h1 className="prahari-devanagari mt-5 text-[clamp(3.6rem,5.4vw,6.7rem)] font-black leading-[.9] tracking-tight text-[#f6c75e] drop-shadow-[0_0_28px_rgba(246,199,94,.18)]">
              पंजापुतम
            </h1>

            <h2 className="mt-5 max-w-[560px] text-[clamp(1.35rem,1.9vw,2.2rem)] font-black leading-[1.12] text-slate-100">
              Predictive Resilient Autonomous Hazard &amp; Risk Intelligence Network
            </h2>

            <p className="mt-4 max-w-[540px] text-[13px] leading-6 text-slate-400">
              Proactive multi-hazard intelligence for sensing, prediction, early warning and resilient local response — designed around evidence, provenance and autonomous edge operation.
            </p>

            <div className="mt-8 grid max-w-[520px] grid-cols-4 gap-5">
              <div className="prahari-native-capability">
                <Activity className="h-6 w-6 text-cyan-300" />
                <span>REAL-TIME<br />MONITORING</span>
              </div>
              <div className="prahari-native-capability">
                <BarChart3 className="h-6 w-6 text-blue-400" />
                <span>AI-POWERED<br />PREDICTIONS</span>
              </div>
              <div className="prahari-native-capability">
                <BellRing className="h-6 w-6 text-orange-400" />
                <span>EARLY<br />ALERTS</span>
              </div>
              <div className="prahari-native-capability">
                <Shield className="h-6 w-6 text-emerald-400" />
                <span>COMMUNITY<br />PROTECTION</span>
              </div>
            </div>
          </div>

          <div className="prahari-native-domains relative z-20 mt-auto">
            {DOMAINS.map(([id, line1, line2, tone]) => (
              <div key={id} className={`prahari-native-domain domain-${tone}`}>
                <div className="domain-id">{id}</div>
                <div>{line1}</div>
                <div>{line2}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="prahari-native-auth-side relative flex min-h-screen items-center justify-center overflow-hidden p-5 sm:p-8 lg:p-[clamp(28px,3vw,54px)]">
          <div className="prahari-mobile-atmosphere lg:hidden" aria-hidden="true" />

          <div className="prahari-native-auth-card relative z-10 w-full max-w-[520px] rounded-[24px] border p-6 sm:p-8 lg:p-[clamp(28px,2.25vw,42px)]">
            <div className="mb-6 lg:hidden">
              <div className="flex items-center gap-3">
                <img src="/logo.svg" alt="PRAHARI-NET" className="h-10 w-10" />
                <div>
                  <div className="text-lg font-black tracking-[.08em]">PRAHARI-NET</div>
                  <div className="text-[9px] font-black tracking-[.1em] text-cyan-300">SENSE • PREDICT • ALERT • PROTECT</div>
                </div>
              </div>
              <div className="prahari-devanagari mt-6 text-4xl font-black text-[#f6c75e]">पंजापुतम</div>
            </div>

            {showDevTools && (
              <div
                role="status"
                className="mb-6 rounded-lg border border-amber-400/45 bg-amber-400/10 px-4 py-3 text-center text-[10px] font-black uppercase tracking-[.07em] text-amber-300"
              >
                DEV AUTH BYPASS — LOCAL DEVELOPMENT ONLY
              </div>
            )}

            <div className="mb-7">
              <div className="mb-2 flex items-center gap-2 text-[10px] font-black uppercase tracking-[.11em] text-cyan-300">
                <Radio className="h-4 w-4" />
                COMMAND &amp; CONTROL ACCESS
              </div>

              <h2 className="text-2xl font-black tracking-tight text-white">
                Operator Authentication
              </h2>

              <p className="mt-2 max-w-md text-[13px] leading-5 text-[#8da8c1]">
                Enter registered credentials to access the PRAHARI environmental command workspace.
              </p>
            </div>

            {error && (
              <div className="mb-5 flex items-start gap-2 rounded-lg border border-red-400/35 bg-red-500/10 p-3 text-xs text-red-200">
                <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label htmlFor="login-username" className="mb-2 block text-[10px] font-bold uppercase tracking-[.09em] text-[#88a3bf]">
                  Username
                </label>
                <div className="relative">
                  <UserRound className="absolute left-4 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-[#6989aa]" />
                  <input
                    id="login-username"
                    type="text"
                    autoComplete="username"
                    required
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder="Registered operator"
                    className="prahari-native-input h-12 w-full rounded-[13px] pl-12 pr-4 text-sm font-semibold text-white outline-none placeholder:text-[#536b82]"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="login-password" className="mb-2 block text-[10px] font-bold uppercase tracking-[.09em] text-[#88a3bf]">
                  Password
                </label>
                <div className="relative">
                  <KeyRound className="absolute left-4 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-[#6989aa]" />
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Password"
                    className="prahari-native-input h-12 w-full rounded-[13px] pl-12 pr-12 text-sm font-semibold text-white outline-none placeholder:text-[#536b82]"
                  />
                  <button
                    type="button"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    onClick={() => setShowPassword((value) => !value)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-2 text-[#d8ad47] transition hover:bg-white/5 hover:text-[#ffe095]"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="prahari-native-submit group flex h-12 w-full items-center justify-center gap-3 rounded-[13px] text-sm font-black text-[#07111d] disabled:cursor-not-allowed disabled:opacity-55"
              >
                <span>{loading ? 'Authenticating secure session…' : 'Access Command Centre'}</span>
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </button>
            </form>

            {showDevTools && (
              <div className="mt-7 border-t border-[#24425d] pt-5">
                <div className="mb-3 text-[10px] font-bold uppercase tracking-[.08em] text-[#7e99b5]">
                  Local jury demo shortcuts
                </div>
                <div className="flex flex-wrap gap-2">
                  {[
                    ['operator', 'Operator'],
                    ['admin', 'Admin'],
                    ['viewer', 'Viewer'],
                  ].map(([user, label]) => (
                    <button
                      key={user}
                      type="button"
                      onClick={() => fillLocalDemo(user)}
                      className="rounded-full border border-[#31516f] bg-[#081827] px-3 py-1.5 text-[10px] font-semibold text-[#bed1e2] transition hover:border-cyan-300/45 hover:text-cyan-200"
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <p className="mt-3 text-[9px] leading-4 text-[#567088]">
                  Development-only shortcuts are never rendered on the public production hostname.
                </p>
              </div>
            )}

            {!showDevTools && (
              <div className="mt-7 flex items-center justify-between border-t border-[#24425d] pt-5 text-[9px] font-bold uppercase tracking-[.1em] text-[#5f7890]">
                <span>SECURE • PROVENANCE-AWARE</span>
                <span>PRAHARI-NET</span>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
};