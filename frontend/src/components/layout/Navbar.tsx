import React, { useState, useEffect } from 'react';
import { Radio, Bell, Volume2, VolumeX, ShieldAlert, Cpu, User as UserIcon, LogOut } from 'lucide-react';
import { audioAlertManager } from '../../services/audioAlerts';
import { wsClient } from '../../services/websocket';

interface NavbarProps {
  summary: any;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ summary, onLogout }) => {
  const [timeStr, setTimeStr] = useState<string>('');
  const [audioEnabled, setAudioEnabled] = useState<boolean>(audioAlertManager.getEnabled());
  const [user, setUser] = useState<any>({});

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);

    const storedUser = localStorage.getItem('prahari_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {}
    }

    return () => clearInterval(interval);
  }, []);

  const toggleAudio = () => {
    const nextState = !audioEnabled;
    audioAlertManager.setEnabled(nextState);
    setAudioEnabled(nextState);
  };

  const activeAlerts = summary?.active_alerts_count ?? 0;
  const criticalAlerts = summary?.critical_alerts_count ?? 0;
  const networkMode = summary?.network_mode || 'LOCAL_EDGE';

  const gatewayLabel =
    summary?.gateway_mode === 'REAL'
      ? 'USB Serial Hardware'
      : summary?.gateway_mode === 'SIMULATOR'
        ? 'Windows Python / Simulator'
        : (summary?.gateway_mode || 'Gateway Unknown');

  return (
    <header className="h-14 bg-bg-secondary border-b border-border-subtle px-4 flex items-center justify-between z-30 shrink-0 select-none">
      {/* Left: System Mode & Local Time */}
      <div className="flex items-center space-x-3 text-xs">
        <div className="flex items-center space-x-1.5 bg-bg-surface px-2.5 py-1 rounded border border-border-subtle">
          <span className="w-2 h-2 rounded-full bg-hazard-normal animate-pulse"></span>
          <span className="font-mono text-text-secondary">{timeStr || '00:00:00'} IST</span>
        </div>

        {/* Network Status Badge */}
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded font-medium border ${
            networkMode === 'ONLINE'
              ? 'bg-hazard-normal/10 border-hazard-normal/30 text-hazard-normal'
              : networkMode === 'LOCAL_EDGE'
              ? 'bg-accent-info/10 border-accent-info/30 text-accent-info'
              : 'bg-hazard-critical/10 border-hazard-critical/30 text-hazard-critical'
          }`}
          title={networkMode === 'LOCAL_EDGE' ? 'Autonomous local operation independent of external internet' : 'Connected to network'}
        >
          <Radio className="w-3.5 h-3.5" />
          <span className="tracking-wider">{networkMode === 'LOCAL_EDGE' ? 'LOCAL EDGE' : networkMode}</span>
        </div>

        {/* Gateway indicator */}
        <div className="hidden sm:flex items-center space-x-1.5 bg-bg-surface px-2.5 py-1 rounded border border-border-subtle text-text-secondary">
          <Cpu className="w-3.5 h-3.5 text-accent-info" />
          <span>Gateway: <strong className="text-text-primary">{gatewayLabel}</strong></span>
        </div>

        {/* Nodes online */}
        <div className="hidden md:flex items-center space-x-1.5 bg-bg-surface px-2.5 py-1 rounded border border-border-subtle text-text-secondary">
          <span className="w-2 h-2 rounded-full bg-hazard-normal"></span>
          <span><strong className="text-text-primary">{summary?.nodes_online ?? 0}</strong> / {summary?.nodes_total ?? 0} Operational Nodes</span>
        </div>
      </div>

      {/* Right: Audio Control, Active Alerts, User & Logout */}
      <div className="flex items-center space-x-2.5">
        {/* Audio Siren Toggle */}
        <button
          onClick={toggleAudio}
          className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs transition-colors border ${
            audioEnabled
              ? 'bg-accent-info/15 text-accent-info border-accent-info/40'
              : 'bg-bg-surface text-text-muted border-border-subtle hover:text-text-secondary'
          }`}
          title={audioEnabled ? 'Auditory alarm enabled (Click to mute)' : 'Auditory alarm disabled (Click to enable)'}
        >
          {audioEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
          <span className="hidden sm:inline">{audioEnabled ? 'SIREN ARMED' : 'MUTED'}</span>
        </button>

        {/* Active Alerts Pill */}
        <div
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-semibold border ${
            criticalAlerts > 0
              ? 'bg-hazard-critical/20 text-hazard-critical border-hazard-critical pulse-critical'
              : activeAlerts > 0
              ? 'bg-hazard-warning/20 text-hazard-warning border-hazard-warning'
              : 'bg-bg-surface text-text-secondary border-border-subtle'
          }`}
        >
          <Bell className="w-3.5 h-3.5" />
          <span>{activeAlerts} ACTIVE {activeAlerts === 1 ? 'ALERT' : 'ALERTS'}</span>
        </div>

        {/* User Role Badge */}
        <div className="hidden lg:flex items-center space-x-1.5 bg-bg-surface px-2 py-1 rounded border border-border-subtle text-xs">
          <UserIcon className="w-3.5 h-3.5 text-accent-info" />
          <span className="font-medium text-text-primary">{user.username || 'operator'}</span>
          <span className="text-[10px] bg-accent-ai/20 text-accent-ai px-1.5 py-0.5 rounded font-mono uppercase">
            {user.role || 'OPERATOR'}
          </span>
        </div>

        {/* Logout */}
        <button
          onClick={onLogout}
          className="p-1.5 rounded text-text-muted hover:text-hazard-critical hover:bg-bg-surface transition-colors"
          title="Sign out of Command Centre"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
