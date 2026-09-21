import React, { useState, useEffect } from 'react';
import { fetchSystemLogs } from '../services/api';
import { Terminal, Search, Filter, ShieldCheck, Clock } from 'lucide-react';

export const SystemLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const loadLogs = async () => {
    try {
      const data = await fetchSystemLogs(categoryFilter === 'ALL' ? undefined : categoryFilter);
      setLogs(data);
    } catch (err) {
      console.error('Error fetching logs:', err);
    }
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 4000);
    return () => clearInterval(interval);
  }, [categoryFilter]);

  const filteredLogs = logs.filter((l) => {
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      return (
        l.message.toLowerCase().includes(q) ||
        l.action.toLowerCase().includes(q) ||
        l.component.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto select-text">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-bg-secondary p-4 rounded-lg border border-border-subtle">
        <div>
          <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
            <Terminal className="w-5 h-5 text-accent-info" />
            <span>Structured System Audit & Diagnostics Logs</span>
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Immutable log stream recording operator interventions, threshold adjustments, and RF lifecycle events.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-2 text-xs">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-text-muted" />
            <input
              type="text"
              placeholder="Search log messages..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-bg-surface border border-border-subtle rounded pl-8 pr-3 py-1.5 text-xs text-text-primary focus:outline-none focus:border-accent-info w-48"
            />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-bg-surface border border-border-subtle rounded px-2.5 py-1.5 text-xs text-text-secondary focus:outline-none"
          >
            <option value="ALL">All Categories</option>
            <option value="ALERT">Alerts</option>
            <option value="SIMULATOR">Simulator</option>
            <option value="AUTH">Authentication</option>
            <option value="SETTINGS">Settings</option>
            <option value="OPERATIONAL">Operational</option>
          </select>
        </div>
      </div>

      {/* Log Console Window */}
      <div className="bg-bg-secondary rounded-lg border border-border-subtle overflow-hidden">
        <div className="p-2.5 bg-bg-surface border-b border-border-subtle flex items-center justify-between text-xs">
          <span className="font-mono text-[11px] text-text-muted">
            Viewing {filteredLogs.length} audit entries • Sensitive credentials masked
          </span>
          <span className="w-2 h-2 rounded-full bg-hazard-normal animate-pulse"></span>
        </div>

        <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
          <table className="w-full text-left font-mono text-[11px]">
            <thead className="bg-bg-surface text-text-muted text-[10px] uppercase tracking-wider border-b border-border-subtle sticky top-0">
              <tr>
                <th className="py-2.5 px-4">Timestamp (IST)</th>
                <th className="py-2.5 px-4">Category</th>
                <th className="py-2.5 px-4">Action</th>
                <th className="py-2.5 px-4">User / Actor</th>
                <th className="py-2.5 px-4">Component</th>
                <th className="py-2.5 px-4">Message Context</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-bg-surface/50">
                  <td className="py-2 px-4 text-text-muted whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-2 px-4">
                    <span className="bg-bg-surface px-1.5 py-0.5 rounded border border-border-subtle text-accent-info text-[10px]">
                      {log.category}
                    </span>
                  </td>
                  <td className="py-2 px-4 font-bold text-text-primary whitespace-nowrap">{log.action}</td>
                  <td className="py-2 px-4 text-text-secondary">{log.user || 'SYSTEM'}</td>
                  <td className="py-2 px-4 text-text-muted">{log.component}</td>
                  <td className="py-2 px-4 text-text-primary leading-relaxed">{log.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
