import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity, AlertTriangle, BarChart2, Box, ChevronLeft, ChevronRight, CloudDownload,
  CloudRain, Database, Droplets, FileText, Flame, Gauge, GitBranch, History,
  Languages, LayoutDashboard, Map as MapIcon, Mountain, PlaySquare, Radio, Route,
  Server, Settings, Shield, ShieldCheck, Sliders, Sparkles, Terminal, TrendingUp,
  WifiOff, Wind,
} from 'lucide-react';

interface SidebarProps { collapsed: boolean; onToggleCollapse: () => void; }
type NavItem = { to: string; label: string; icon: React.ElementType; domain?: string; highlight?: boolean };
type NavGroup = { label: string; items: NavItem[] };

const groups: NavGroup[] = [
  { label: 'OPERATIONS', items: [
    { to: '/', label: 'Command Centre', icon: LayoutDashboard }, { to: '/map', label: 'Live Map', icon: MapIcon }, { to: '/nodes', label: 'All Nodes', icon: Server },
  ] },
  { label: 'PANCHA BHOOTHA', items: [
    { to: '/live/jala', label: 'जल (JALA)', icon: Droplets, domain: 'jala' },
    { to: '/live/agni', label: 'अग्नि (AGNI)', icon: Flame, domain: 'agni' },
    { to: '/live/bhumi', label: 'भूमि (BHUMI)', icon: Mountain, domain: 'bhumi' },
    { to: '/live/vayu', label: 'वायु (VAYU)', icon: Wind, domain: 'vayu' },
    { to: '/live/akasha', label: 'आकाश (AKASHA)', icon: CloudRain, domain: 'akasha' },
  ] },
  { label: 'INTELLIGENCE', items: [
    { to: '/alerts', label: 'Alerts Centre', icon: AlertTriangle }, { to: '/predictions', label: 'Predictions', icon: TrendingUp },
    { to: '/evidence-gate', label: 'Evidence Gate', icon: ShieldCheck }, { to: '/cascades', label: 'Cross-Hazard Intelligence', icon: GitBranch },
    { to: '/analytics', label: 'Analytics', icon: BarChart2 }, { to: '/digital-twin', label: 'Digital Twin', icon: Box },
    { to: '/impact', label: 'Impact & Evacuation', icon: Route }, { to: '/cap', label: 'CAP Warning Centre', icon: Languages },
    { to: '/continuity', label: 'Offline Continuity', icon: WifiOff }, { to: '/ai', label: 'PRAHARI Copilot', icon: Sparkles },
  ] },
  { label: 'ASSURANCE', items: [
    { to: '/security', label: 'Security Event Centre', icon: Shield }, { to: '/datasets', label: 'Dataset Manager', icon: Database },
    { to: '/events', label: 'Disaster Memory', icon: History }, { to: '/simulator', label: 'Scenario Lab', icon: PlaySquare },
    { to: '/reports', label: 'Reports & Recovery', icon: FileText }, { to: '/readiness', label: 'System Readiness', icon: ShieldCheck },
    { to: '/calibration', label: 'Calibration', icon: Gauge }, { to: '/health', label: 'Device Health', icon: Activity },
    { to: '/logs', label: 'System Logs', icon: Terminal }, { to: '/settings', label: 'Settings', icon: Settings },
    { to: '/network', label: 'Network & RF', icon: Radio }, { to: '/external-data', label: 'External Data', icon: CloudDownload },
  ] },
  { label: 'PRESENTATION', items: [{ to: '/demo', label: 'SIH 2026 Walkthrough', icon: Sliders, highlight: true }] },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => (
  <aside className={`${collapsed ? 'w-[72px]' : 'w-[272px]'} command-sidebar h-full min-h-0 shrink-0 border-r border-border-subtle flex flex-col transition-[width] duration-200 z-20`}>
    <div className="h-[70px] shrink-0 border-b border-border-subtle px-3 flex items-center justify-between bg-bg-secondary/70 backdrop-blur-xl">
      <div className="flex items-center gap-2.5 overflow-hidden"><div className="relative shrink-0"><img src="/logo.svg" alt="PRAHARI Logo" className="w-9 h-9" /><span className="absolute inset-0 rounded-full shadow-[0_0_22px_rgba(142,182,155,.2)]" /></div>
        {!collapsed && <div className="min-w-0"><div className="font-extrabold tracking-[.14em] text-[13px] text-text-primary">PRAHARI-NET</div><div className="text-[8px] tracking-[.22em] text-accent-info font-bold mt-1">SENSE • PREDICT • ALERT • PROTECT</div></div>}
      </div>
      <button type="button" onClick={onToggleCollapse} className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-bg-surface" aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}>{collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}</button>
    </div>
    <nav aria-label="Primary command navigation" className="flex-1 overflow-y-auto py-3 px-2 space-y-3 text-xs">
      {groups.map(group => <div key={group.label}>{collapsed ? <div className="mx-2 mb-2 border-t border-border-subtle" /> : <div className="px-2.5 pb-1.5 text-[9px] uppercase font-bold tracking-[.2em] text-text-muted">{group.label}</div>}
        <div className="space-y-0.5">{group.items.map(item => { const Icon = item.icon; return <NavLink key={item.to} to={item.to} end={item.to === '/'} aria-label={item.label} title={collapsed ? item.label : undefined} className={({ isActive }) => `command-nav-link ${isActive ? 'is-active' : ''} ${item.highlight ? 'is-highlight' : ''} ${collapsed ? 'justify-center px-2' : ''}`} style={item.domain ? { '--domain-accent': `var(--${item.domain})` } as React.CSSProperties : undefined}><Icon className="w-4 h-4 shrink-0" />{!collapsed && <span className="truncate">{item.label}</span>}</NavLink>; })}</div>
      </div>)}
    </nav>
    {!collapsed && <div className="p-3 border-t border-border-subtle text-[9px] text-text-muted flex items-center justify-between bg-bg-secondary/60"><span>SIH 2026 • SIH26178</span><span className="font-mono text-accent-info">SECURE EDGE</span></div>}
  </aside>
);
