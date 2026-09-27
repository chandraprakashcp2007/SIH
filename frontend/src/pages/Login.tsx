import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAuthMode, login } from '../services/api';
import { ArrowRight, Eye, EyeOff, KeyRound, Radio, ShieldAlert, UserRound } from 'lucide-react';

const DOMAIN_IDS = ['JALA-01', 'AGNI-02', 'BHUMI-03', 'VAYU-04', 'AKASHA-05'] as const;

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
    <main className="relative min-h-screen overflow-hidden bg-[#020812] text-white">
      {/* Desktop cinematic layer: exact user-provided visual reference. */}
      <div className="absolute inset-0 hidden lg:block" aria-hidden="true">
        <img
          src="/prahari-login-cinematic.png"
          alt=""
          className="h-full w-full object-cover object-center"
          draggable={false}
        />
      </div>

      {/* Mobile fallback intentionally avoids exposing the reference image's static demo panel. */}
      <div
        className="absolute inset-0 lg:hidden"
        aria-hidden="true"
        style={{
          background:
            'radial-gradient(circle at 50% 22%, rgba(0,195,255,.18), transparent 32%), radial-gradient(circle at 18% 80%, rgba(42,69,152,.24), transparent 35%), linear-gradient(145deg,#020914 0%,#06172a 58%,#020812 100%)',
        }}
      />

      {/* Keep semantic project/domain identity in the DOM while the desktop visual is image-driven. */}
      <div className="sr-only">
        <h1>पंजापुतम</h1>
        <p>PRAHARI-NET — Predictive Resilient Autonomous Hazard &amp; Risk Intelligence Network</p>
        {DOMAIN_IDS.map((id) => <span key={id}>{id}</span>)}
      </div>

      <section className="relative z-10 flex min-h-screen items-center justify-center p-5 lg:justify-end lg:px-[2.45vw] lg:py-[4vh]">
        <div
          className="
            flex w-full max-w-md flex-col justify-center
            rounded-[22px] border border-[#315f82]
            bg-[#06172a] p-6
            shadow-[0_35px_100px_rgba(0,0,0,.58),inset_0_1px_0_rgba(255,255,255,.03)]
            sm:p-8
            lg:min-h-[74vh] lg:w-[33.4vw] lg:max-w-[550px] lg:min-w-[450px] lg:p-[2.2vw]
          "
        >
          {devBypass && (
            <div
              role="status"
              className="mb-6 border border-[#d4a400] bg-[#101c24] px-4 py-3 text-center text-[11px] font-black uppercase tracking-[0.06em] text-[#ffc400]"
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
              <label
                htmlFor="login-username"
                className="mb-2 block text-[11px] font-bold uppercase tracking-[0.04em] text-[#82a9d3]"
              >
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
                  className="h-12 w-full rounded-[14px] border border-[#355776] bg-[#081421] pl-12 pr-4 text-sm font-semibold text-white outline-none transition placeholder:text-[#5d7186] focus:border-cyan-300/80 focus:ring-2 focus:ring-cyan-300/10"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="login-password"
                className="mb-2 block text-[11px] font-bold uppercase tracking-[0.04em] text-[#82a9d3]"
              >
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
                  className="h-12 w-full rounded-[14px] border border-[#355776] bg-[#081421] pl-12 pr-12 text-sm font-semibold text-white outline-none transition placeholder:text-[#5d7186] focus:border-cyan-300/80 focus:ring-2 focus:ring-cyan-300/10"
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
              className="group flex h-12 w-full items-center justify-center gap-3 rounded-[14px] border border-[#ffd36b] bg-gradient-to-r from-[#e5b951] via-[#f4d177] to-[#deb04c] text-sm font-black text-[#08111b] shadow-[0_8px_28px_rgba(225,175,63,.18)] transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-55"
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
                <button
                  type="button"
                  onClick={() => fillLocalDemo('operator')}
                  className="rounded-full border border-[#355776] bg-[#0a1c2e] px-3 py-1.5 text-[11px] text-[#c7dbef] hover:border-cyan-300/50"
                >
                  Operator (Field Officer)
                </button>
                <button
                  type="button"
                  onClick={() => fillLocalDemo('admin')}
                  className="rounded-full border border-[#355776] bg-[#0a1c2e] px-3 py-1.5 text-[11px] text-[#c7dbef] hover:border-cyan-300/50"
                >
                  Admin (EOC Director)
                </button>
                <button
                  type="button"
                  onClick={() => fillLocalDemo('viewer')}
                  className="rounded-full border border-[#355776] bg-[#0a1c2e] px-3 py-1.5 text-[11px] text-[#c7dbef] hover:border-cyan-300/50"
                >
                  Viewer (Observer)
                </button>
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
