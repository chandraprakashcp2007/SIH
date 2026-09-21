import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { CopilotDrawer } from '../copilot/CopilotDrawer';
import { fetchSystemSummary } from '../../services/api';
import { wsClient } from '../../services/websocket';
import { WifiOff } from 'lucide-react';
import { Menu } from 'lucide-react';

export const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    setMobileNavOpen(false);
  }, [location.pathname]);

  const loadSummary = async () => {
    try {
      const data = await fetchSystemSummary();
      setSummary(data);
    } catch (e) {
      console.warn('Could not refresh summary:', e);
    }
  };

  useEffect(() => {
    loadSummary();
    const interval = setInterval(loadSummary, 5000);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Subscribe to WebSocket status changes
    const unsubTelemetry = wsClient.subscribe('telemetry.updated', loadSummary);
    const unsubAlert = wsClient.subscribe('alert.created', loadSummary);
    const unsubSim = wsClient.subscribe('simulation.updated', loadSummary);

    return () => {
      clearInterval(interval);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      unsubTelemetry();
      unsubAlert();
      unsubSim();
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('prahari_token');
    localStorage.removeItem('prahari_user');
    navigate('/login');
  };

  return (
    <div className="flex h-screen w-screen bg-bg-primary text-text-primary overflow-hidden">
      {/* Left Sidebar */}
      {mobileNavOpen && <button aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} className="fixed inset-0 bg-black/60 z-40 md:hidden" />}
      <div className={`${mobileNavOpen ? 'block' : 'hidden'} fixed inset-y-0 left-0 z-50 md:static md:block`}>
        <Sidebar collapsed={collapsed} onToggleCollapse={() => setCollapsed(!collapsed)} />
      </div>

      {/* Main Column */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <button aria-label="Open navigation" onClick={() => setMobileNavOpen(true)} className="md:hidden absolute top-3 left-3 z-40 p-2 bg-bg-surface border border-border-subtle"><Menu className="w-4 h-4" /></button>
        {/* Top Navbar */}
        <Navbar summary={summary} onLogout={handleLogout} />

        {/* Offline Banner (if physical WAN connection drops) */}
        {!isOnline && (
          <div className="bg-amber-900/40 border-b border-amber-600/50 px-4 py-1.5 flex items-center justify-between text-xs text-amber-300 z-30">
            <div className="flex items-center space-x-2">
              <WifiOff className="w-4 h-4" />
              <span>
                <strong>EXTERNAL INTERNET DISCONNECTED:</strong> PRAHARI-NET is operating in autonomous <strong>LOCAL EDGE</strong> mode over local LoRa RF & LAN.
              </span>
            </div>
            <span className="text-[10px] bg-amber-600/30 px-2 py-0.5 rounded font-mono">EDGE SOVEREIGN</span>
          </div>
        )}
        {summary?._dataState?.source === 'CACHED' && (
          <div role="status" className="bg-slate-800 border-b border-slate-600 px-4 py-1.5 text-xs text-slate-200">
            CACHED OPERATIONAL DATA — last confirmed {summary._dataState.ageSeconds}s ago. Values are not live.
          </div>
        )}

        {/* Dynamic Workspace Container */}
        <main className="flex-1 overflow-y-auto min-h-0 bg-bg-primary">
          <Outlet context={{ summary, onRefreshSummary: loadSummary }} />
        </main>
      </div>

      {/* Persistent Floating Copilot */}
      <CopilotDrawer />
    </div>
  );
};
