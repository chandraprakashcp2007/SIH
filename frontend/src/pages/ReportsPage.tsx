import React, { useState } from 'react';
import { AlertTriangle, Download, FileText, Loader2, Printer } from 'lucide-react';
import { downloadReportCsv, fetchAlerts, fetchIncidentReport } from '../services/api';

type ReportState = 'IDLE' | 'LOADING' | 'READY' | 'NOT_FOUND' | 'ERROR';

export const ReportsPage: React.FC = () => {
  const [selectedAlertId, setSelectedAlertId] = useState<string>('');
  const [reportData, setReportData] = useState<any | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [reportState, setReportState] = useState<ReportState>('IDLE');
  const [message, setMessage] = useState('Select an incident to view its persisted situation brief.');
  const [exporting, setExporting] = useState<string>('');

  React.useEffect(() => {
    let active = true;
    fetchAlerts()
      .then((data) => {
        if (!active) return;
        setAlerts(data);
        if (data.length > 0) void loadIncidentReport(data[0].id);
      })
      .catch((error) => {
        if (!active) return;
        setMessage(error?.message || 'Unable to load incident list.');
        setReportState('ERROR');
      });
    return () => { active = false; };
  }, []);

  const loadIncidentReport = async (alertId: string) => {
    setSelectedAlertId(alertId);
    setReportData(null);
    setReportState('LOADING');
    setMessage('Loading persisted incident report…');
    try {
      const report = await fetchIncidentReport(alertId);
      setReportData(report);
      setReportState('READY');
      setMessage('');
    } catch (error: any) {
      if (error?.status === 404) {
        setReportState('NOT_FOUND');
        setMessage('REPORT NOT YET GENERATED / INSUFFICIENT PERSISTED EVIDENCE');
      } else {
        setReportState('ERROR');
        setMessage(error?.message || 'Unable to load persisted incident report.');
      }
    }
  };

  const handleDownload = async (reportType: 'telemetry' | 'alerts' | 'events') => {
    setExporting(reportType);
    try {
      const { blob, filename } = await downloadReportCsv(reportType);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1500);
    } catch (error: any) {
      setMessage(error?.message || `Unable to export ${reportType} CSV.`);
      setReportState('ERROR');
    } finally {
      setExporting('');
    }
  };

  return (
    <div className="mx-auto max-w-7xl space-y-4 p-4 select-text">
      <div className="rounded-xl border border-border-subtle bg-bg-secondary p-4 text-xs">
        <h2 className="font-bold">Recovery Intelligence</h2>
        <p className="mt-1 text-text-muted">Incident reports cite persisted evidence. Unverified evidence remains PENDING_HUMAN_VERIFICATION, and PRAHARI never issues an automatic all-clear.</p>
      </div>

      <div className="flex flex-col justify-between gap-3 rounded-xl border border-border-subtle bg-bg-secondary p-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="flex items-center gap-2 text-base font-bold text-text-primary"><FileText className="h-5 w-5 text-accent-info" />Incident Documentation & CSV Export</h1>
          <p className="mt-0.5 text-xs text-text-muted">Authenticated situation briefs, telemetry archives and audit records.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {([
            ['telemetry', 'Export Telemetry CSV'],
            ['alerts', 'Export Alerts CSV'],
            ['events', 'Export Audit CSV'],
          ] as const).map(([type, label]) => (
            <button key={type} type="button" onClick={() => handleDownload(type)} disabled={Boolean(exporting)} className="flex items-center gap-1.5 rounded border border-border-subtle bg-bg-surface px-3 py-1.5 text-text-primary transition hover:bg-bg-elevated disabled:opacity-50">
              {exporting === type ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5 text-accent-info" />}
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div className="space-y-2 rounded-xl border border-border-subtle bg-bg-secondary p-3.5">
          <h3 className="mb-2 text-xs font-bold uppercase tracking-wider text-text-primary">Select Incident</h3>
          <div className="max-h-[520px] space-y-1 overflow-y-auto">
            {alerts.length === 0 && <div className="rounded border border-dashed border-border-subtle p-4 text-center text-[10px] text-text-muted">NO PERSISTED INCIDENTS AVAILABLE</div>}
            {alerts.map((alert) => (
              <button key={alert.id} onClick={() => loadIncidentReport(alert.id)} className={`w-full rounded border p-2 text-left text-xs transition ${selectedAlertId === alert.id ? 'border-accent-info/50 bg-accent-info/15 text-accent-info' : 'border-border-subtle bg-bg-surface text-text-secondary hover:text-text-primary'}`}>
                <div className="font-bold">{alert.id}</div>
                <div className="truncate text-[10px] text-text-muted">{alert.headline}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-4 rounded-xl border border-border-subtle bg-bg-secondary p-6 lg:col-span-3">
          <div className="flex items-center justify-between border-b border-border-subtle pb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary">Formal Emergency Situation Brief</span>
            <button type="button" onClick={() => window.print()} disabled={reportState !== 'READY'} className="flex items-center gap-1.5 rounded bg-accent-info px-3 py-1.5 text-xs font-bold text-bg-primary transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-40"><Printer className="h-3.5 w-3.5" />Print Incident Report</button>
          </div>

          {reportState === 'LOADING' && <div role="status" className="flex min-h-72 items-center justify-center gap-2 text-sm text-text-muted"><Loader2 className="h-4 w-4 animate-spin" />Loading persisted evidence…</div>}

          {(reportState === 'IDLE' || reportState === 'NOT_FOUND' || reportState === 'ERROR') && (
            <div className={`flex min-h-72 flex-col items-center justify-center rounded-xl border border-dashed p-8 text-center ${reportState === 'ERROR' ? 'border-red-400/25 bg-red-400/5 text-red-200' : 'border-border-subtle text-text-muted'}`}>
              {reportState === 'ERROR' ? <AlertTriangle className="mb-3 h-6 w-6" /> : <FileText className="mb-3 h-6 w-6" />}
              <div className="max-w-lg text-sm font-semibold">{message}</div>
              {reportState === 'NOT_FOUND' && <div className="mt-2 text-[10px] font-mono text-text-muted">No report claim is fabricated when persisted evidence is absent.</div>}
            </div>
          )}

          {reportState === 'READY' && reportData && (
            <div className="space-y-4 text-xs font-sans">
              <div className="flex items-start justify-between border-b border-border-subtle pb-4">
                <div><h2 className="text-sm font-bold text-text-primary">{reportData.organization}</h2><p className="text-[11px] text-text-muted">{reportData.competition}</p></div>
                <div className="text-right"><div className="font-mono text-sm font-bold text-accent-info">{reportData.incident_id}</div><div className="text-[10px] text-text-muted">{new Date(reportData.detection_timestamp).toLocaleString()}</div></div>
              </div>

              <div className="grid grid-cols-2 gap-3 rounded border border-border-subtle bg-bg-surface p-3 sm:grid-cols-4">
                <div><div className="text-[10px] text-text-muted">Hazard Type</div><div className="mt-0.5 font-bold text-text-primary">{reportData.hazard_category}</div></div>
                <div><div className="text-[10px] text-text-muted">Reporting Node</div><div className="mt-0.5 font-bold text-text-primary">{reportData.reporting_node}</div></div>
                <div><div className="text-[10px] text-text-muted">Severity Band</div><div className="mt-0.5 font-bold text-hazard-critical">{reportData.severity_level}</div></div>
                <div><div className="text-[10px] text-text-muted">Risk & Confidence</div><div className="mt-0.5 font-bold text-text-primary">{reportData.risk_assessment_score}% ({reportData.detection_confidence_pct}%)</div></div>
              </div>

              <div><h4 className="mb-1 font-bold text-text-primary">Executive Summary & Sensor Causality</h4><div className="whitespace-pre-line rounded border border-border-subtle bg-bg-surface p-3 font-mono text-[11px] leading-relaxed text-text-secondary">{reportData.executive_summary}</div></div>
              <div><h4 className="mb-1 font-bold text-text-primary">Operational Action Taken</h4><div className="rounded border border-border-subtle bg-bg-surface p-3 text-text-primary">{reportData.operational_action_taken}</div></div>
              <div><h4 className="mb-1 font-bold text-text-primary">Resolution Audit Trail</h4><div className="rounded border border-border-subtle bg-bg-surface p-3 font-mono text-[11px] text-text-secondary">{reportData.resolution_notes}</div></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
