import React, { useEffect, useState } from 'react';
import { Bell, Cpu, LogOut, Radio, User as UserIcon, Volume2, VolumeX } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { audioAlertManager } from '../../services/audioAlerts';
import { SourceBadge, StatusBadge } from '../ui/CommandPrimitives';

interface NavbarProps { summary: any; onLogout: () => void; }
const routeTitles: Record<string, [string, string]> = {
  '/': ['Command Centre', 'Multi-hazard operations'], '/map': ['Live Map', 'Geospatial intelligence'], '/nodes': ['All Nodes', 'Sensor fabric'],
  '/alerts': ['Alerts Centre', 'Incident triage'], '/predictions': ['Predictions', 'Evidence-aware outlook'], '/evidence-gate': ['Evidence Gate', 'Trust and corroboration'],
  '/cascades': ['Cross-Hazard', 'Linked environmental risk'], '/analytics': ['Analytics', 'Operational intelligence'], '/reports': ['Reports & Recovery', 'Persisted evidence'],
  '/digital-twin': ['Digital Twin', 'State and uncertainty'], '/impact': ['Impact & Evacuation', 'Decision support'], '/cap': ['CAP Centre', 'Public warning'],
  '/continuity': ['Continuity', 'Offline resilience'], '/security': ['Security', 'Trust and assurance'], '/datasets': ['Dataset Manager', 'Evidence sources'],
  '/events': ['Disaster Memory', 'Tamper-evident history'], '/simulator': ['Scenario Lab', 'Simulation isolation'], '/readiness': ['System Readiness', 'Operational posture'],
  '/calibration': ['Calibration', 'Sensor assurance'], '/health': ['Device Health', 'Fleet diagnostics'], '/logs': ['System Logs', 'Audit timeline'], '/settings': ['Settings', 'Command configuration'],
};

export const Navbar: React.FC<NavbarProps> = ({ summary, onLogout }) => {
  const [timeStr, setTimeStr] = useState('');
  const [audioEnabled, setAudioEnabled] = useState(audioAlertManager.getEnabled());
  const [user, setUser] = useState<any>({});
  const { pathname } = useLocation();
  const domain = pathname.match(/^\/live\/(jala|agni|bhumi|vayu|akasha)/)?.[1]?.toUpperCase();
  const [title, subtitle] = domain ? [`${domain} Intelligence`, 'Pancha Bhootha live operations'] : (routeTitles[pathname] || ['PRAHARI Workspace', 'Environmental intelligence']);
  useEffect(() => { const update = () => setTimeStr(new Date().toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit' })); update(); const id = setInterval(update, 1000); try { setUser(JSON.parse(localStorage.getItem('prahari_user') || '{}')); } catch { setUser({}); } return () => clearInterval(id); }, []);
  const activeAlerts = summary?.active_alerts_count ?? 0; const criticalAlerts = summary?.critical_alerts_count ?? 0; const networkMode = summary?.network_mode || 'UNVERIFIED';
  const networkStatus = summary?._dataState?.source === 'CACHED' ? 'CACHED' : summary?.gateway_status === 'CONNECTED' ? 'OPERATIONAL' : summary?.gateway_status === 'STALE' || summary?.gateway_status === 'OFFLINE' ? 'DEGRADED' : 'UNVERIFIED';
  const toggleAudio = () => { const next = !audioEnabled; audioAlertManager.setEnabled(next); setAudioEnabled(next); };
  return <header className="command-navbar h-[70px] border-b border-border-subtle px-3 md:px-4 flex items-center justify-between gap-3 z-30 shrink-0 select-none">
    <div className="min-w-0 pl-11 md:pl-0"><div className="command-eyebrow hidden sm:block">{subtitle}</div><h1 className="truncate text-sm md:text-base font-bold text-text-primary tracking-tight">{title}</h1></div>
    <div className="hidden xl:flex items-center gap-2"><SourceBadge source={summary?.gateway_mode === 'REAL' ? 'REAL' : summary?.gateway_mode === 'SIMULATOR' ? 'SIMULATION' : 'UNVERIFIED'} /><StatusBadge status={networkStatus} /><span className="command-header-chip"><Cpu />{summary?.nodes_online ?? 0}/{summary?.nodes_total ?? 0} NODES</span></div>
    <div className="ml-auto flex items-center gap-1.5 md:gap-2"><span className="command-header-chip hidden sm:inline-flex"><Radio />{networkMode === 'LOCAL_EDGE' ? 'LOCAL EDGE' : networkMode}</span><span className="command-header-chip hidden lg:inline-flex font-mono">{timeStr || '00:00'} IST</span>
      <button type="button" onClick={toggleAudio} className={`command-icon-button ${audioEnabled ? 'is-active' : ''}`} aria-label={audioEnabled ? 'Disable auditory alarms' : 'Enable auditory alarms'}>{audioEnabled ? <Volume2 /> : <VolumeX />}</button>
      <span className={`command-alert-chip ${criticalAlerts ? 'is-critical' : ''}`} aria-label={`${activeAlerts} active alerts`}><Bell /><b>{activeAlerts}</b><span className="hidden sm:inline">ACTIVE</span></span>
      <div className="hidden lg:flex items-center gap-2 pl-2 border-l border-border-subtle"><span className="command-avatar"><UserIcon /></span><span className="text-[10px] leading-tight"><b className="block text-text-primary">{user.username || 'operator'}</b><span className="text-text-muted uppercase">{user.role || 'OPERATOR'}</span></span></div>
      <button type="button" onClick={onLogout} className="command-icon-button hover:!text-hazard-critical" aria-label="Sign out of Command Centre"><LogOut /></button>
    </div>
  </header>;
};
