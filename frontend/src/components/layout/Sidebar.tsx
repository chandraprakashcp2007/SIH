import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Map as MapIcon,
  Server,
  AlertTriangle,
  TrendingUp,
  BarChart2,
  Radio,
  Activity,
  BrainCircuit,
  History,
  FileText,
  Sliders,
  PlaySquare,
  Droplets,
  Flame,
  Mountain,
  Wind,
  CloudRain,
  ChevronLeft,
  ChevronRight,
  Terminal,
  Gauge,
  ShieldCheck,
  Database,
  CloudDownload
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => {
  const navItems = [
    { section: 'OPERATIONS' },
    { to: '/', label: 'Command Centre', icon: LayoutDashboard },
    { to: '/map', label: 'Live Map', icon: MapIcon },
    { to: '/nodes', label: 'All Nodes', icon: Server },
    { section: 'PANCHA BHOOTHAM' },
    { to: '/nodes/JALA-01', label: 'JALA (Flood)', icon: Droplets, indent: true },
    { to: '/nodes/AGNI-02', label: 'AGNI (Fire)', icon: Flame, indent: true },
    { to: '/nodes/BHUMI-03', label: 'BHUMI (Landslide)', icon: Mountain, indent: true },
    { to: '/nodes/VAYU-04', label: 'VAYU (Air)', icon: Wind, indent: true },
    { to: '/nodes/AKASHA-05', label: 'AKASHA (Atmosphere)', icon: CloudRain, indent: true },
    { to: '/alerts', label: 'Alert Centre', icon: AlertTriangle },

    { section: 'INTELLIGENCE' },
    { to: '/predictions', label: 'Predictions', icon: TrendingUp },
    { to: '/analytics', label: 'Analytics', icon: BarChart2 },
    { to: '/ai', label: 'AI Intelligence', icon: BrainCircuit },
    { to: '/external-data', label: 'External Data', icon: CloudDownload },
    { to: '/datasets', label: 'Dataset Manager', icon: Database },

    { section: 'INFRASTRUCTURE' },
    { to: '/network', label: 'Network & RF', icon: Radio },
    { to: '/health', label: 'Device Health', icon: Activity },
    { to: '/simulator', label: 'Simulator', icon: PlaySquare },
    { to: '/calibration', label: 'Calibration', icon: Gauge },
    { to: '/readiness', label: 'System Readiness', icon: ShieldCheck },

    { section: 'GOVERNANCE' },
    { to: '/events', label: 'Event History', icon: History },
    { to: '/reports', label: 'Reports & Export', icon: FileText },
    { to: '/logs', label: 'System Logs', icon: Terminal },
    { to: '/settings', label: 'Settings', icon: Sliders },

    { section: 'HACKATHON DEMO' },
    { to: '/demo', label: 'SIH 2026 Walkthrough', icon: PlaySquare, highlight: true },
  ];

  return (
    <aside
      className={`h-full min-h-0 bg-bg-secondary border-r border-border-subtle flex flex-col transition-all duration-200 z-20 select-none ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-14 border-b border-border-subtle px-3 flex items-center justify-between">
        <div className="flex items-center space-x-2.5 overflow-hidden">
          <img src="/logo.svg" alt="PRAHARI Logo" className="w-8 h-8 shrink-0" />
          {!collapsed && (
            <div className="truncate">
              <div className="font-bold tracking-wider text-sm text-text-primary flex items-center space-x-1">
                <span>PRAHARI-NET</span>
              </div>
              <div className="text-[9px] tracking-widest text-accent-info font-medium">
                SENSE • PREDICT • ALERT
              </div>
            </div>
          )}
        </div>
        <button
          onClick={onToggleCollapse}
          className="p-1 rounded text-text-muted hover:text-text-primary hover:bg-bg-surface"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5 text-xs font-medium">
        {navItems.map((item, idx) => {
          if (item.section) {
            if (collapsed) return <div key={idx} className="my-2 border-t border-border-subtle" />;
            return (
              <div key={idx} className="px-2 pt-3 pb-1 text-[10px] uppercase font-semibold tracking-wider text-text-muted">
                {item.section}
              </div>
            );
          }

          const Icon = item.icon!;
          return (
            <NavLink
              key={item.to}
              to={item.to!}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center px-2.5 py-2 rounded transition-colors group relative ${
                  item.indent && !collapsed ? 'pl-6' : ''
                } ${
                  item.highlight
                    ? 'bg-accent-ai/10 text-accent-ai border border-accent-ai/30 hover:bg-accent-ai/20'
                    : isActive
                    ? 'bg-bg-surface text-accent-info font-semibold border-l-2 border-accent-info'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-surface/50'
                }`
              }
              title={collapsed ? item.label : undefined}
            >
              <Icon className={`w-4 h-4 shrink-0 ${collapsed ? 'mx-auto' : 'mr-2.5'}`} />
              {!collapsed && <span className="truncate">{item.label}</span>}
              {item.highlight && !collapsed && (
                <span className="ml-auto text-[9px] bg-accent-ai text-white px-1.5 py-0.2 rounded font-bold">
                  LIVE
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      {!collapsed && (
        <div className="p-3 border-t border-border-subtle text-[11px] text-text-muted flex items-center justify-between">
          <span>SIH 2026 • SIH26178</span>
          <span className="text-accent-info font-mono">v1.0.0</span>
        </div>
      )}
    </aside>
  );
};
