import React, { useState } from 'react';
import { FileText, Download, Printer, ShieldCheck, AlertTriangle } from 'lucide-react';
import { fetchAlerts } from '../services/api';

export const ReportsPage: React.FC = () => {
  const [selectedAlertId, setSelectedAlertId] = useState<string>('');
  const [reportData, setReportData] = useState<any | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);

  React.useEffect(() => {
    fetchAlerts().then((data) => {
      setAlerts(data);
      if (data.length > 0) {
        loadIncidentReport(data[0].id);
      }
    }).catch(console.error);
  }, []);

  const loadIncidentReport = async (alertId: string) => {
    setSelectedAlertId(alertId);
    try {
      const res = await fetch(`/api/reports/incident/${alertId}`);
      if (res.ok) {
        setReportData(await res.json());
      }
    } catch (e) {
      console.error('Error fetching report:', e);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="p-4 space-y-4 max-w-7xl mx-auto select-text">
      {/* Header */}
      <div className="bg-bg-secondary p-4 rounded-lg border border-border-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-base font-bold text-text-primary flex items-center space-x-2">
            <FileText className="w-5 h-5 text-accent-info" />
            <span>Incident Documentation & CSV Reports Export</span>
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Official emergency situation briefs, raw telemetry archives, and audit records.
          </p>
        </div>

        {/* CSV Export Links */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <a
            href="/api/reports/export/csv?report_type=telemetry"
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-bg-surface hover:bg-bg-elevated border border-border-subtle rounded text-text-primary transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-accent-info" />
            <span>Export Telemetry CSV</span>
          </a>

          <a
            href="/api/reports/export/csv?report_type=alerts"
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-bg-surface hover:bg-bg-elevated border border-border-subtle rounded text-text-primary transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-hazard-warning" />
            <span>Export Alerts CSV</span>
          </a>

          <a
            href="/api/reports/export/csv?report_type=events"
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-bg-surface hover:bg-bg-elevated border border-border-subtle rounded text-text-primary transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-accent-ai" />
            <span>Export Audit Log CSV</span>
          </a>
        </div>
      </div>

      {/* Printable Incident Report Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Left selector */}
        <div className="bg-bg-secondary p-3.5 rounded-lg border border-border-subtle space-y-2">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-2">
            Select Incident
          </h3>
          <div className="space-y-1 max-h-[500px] overflow-y-auto">
            {alerts.map((a) => (
              <button
                key={a.id}
                onClick={() => loadIncidentReport(a.id)}
                className={`w-full text-left p-2 rounded text-xs transition-colors border ${
                  selectedAlertId === a.id
                    ? 'bg-accent-info/15 text-accent-info border-accent-info/50'
                    : 'bg-bg-surface text-text-secondary border-border-subtle hover:text-text-primary'
                }`}
              >
                <div className="font-bold">{a.id}</div>
                <div className="text-[10px] text-text-muted truncate">{a.headline}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Right Printable Document View */}
        <div className="lg:col-span-3 bg-bg-secondary p-6 rounded-lg border border-border-subtle space-y-4">
          <div className="flex justify-between items-center border-b border-border-subtle pb-3">
            <span className="text-xs font-bold text-text-primary uppercase tracking-wider">
              Formal Emergency Situation Brief
            </span>
            <button
              onClick={handlePrint}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-accent-info text-bg-primary font-bold rounded text-xs hover:bg-cyan-300 transition-colors"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Official Incident Report</span>
            </button>
          </div>

          {reportData ? (
            <div className="space-y-4 text-xs font-sans">
              <div className="flex justify-between items-start border-b border-border-subtle pb-4">
                <div>
                  <h2 className="text-sm font-bold text-text-primary">{reportData.organization}</h2>
                  <p className="text-[11px] text-text-muted">{reportData.competition}</p>
                </div>
                <div className="text-right">
                  <div className="font-mono font-bold text-sm text-accent-info">{reportData.incident_id}</div>
                  <div className="text-[10px] text-text-muted">{new Date(reportData.detection_timestamp).toLocaleString()}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-bg-surface p-3 rounded border border-border-subtle">
                <div>
                  <div className="text-[10px] text-text-muted">Hazard Type</div>
                  <div className="font-bold text-text-primary mt-0.5">{reportData.hazard_category}</div>
                </div>
                <div>
                  <div className="text-[10px] text-text-muted">Reporting Node</div>
                  <div className="font-bold text-text-primary mt-0.5">{reportData.reporting_node}</div>
                </div>
                <div>
                  <div className="text-[10px] text-text-muted">Severity Band</div>
                  <div className="font-bold text-hazard-critical mt-0.5">{reportData.severity_level}</div>
                </div>
                <div>
                  <div className="text-[10px] text-text-muted">Risk & Confidence</div>
                  <div className="font-bold text-text-primary mt-0.5">{reportData.risk_assessment_score}% ({reportData.detection_confidence_pct}%)</div>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-text-primary mb-1">Executive Summary & Sensor Causality</h4>
                <div className="bg-bg-surface p-3 rounded border border-border-subtle font-mono text-[11px] text-text-secondary whitespace-pre-line leading-relaxed">
                  {reportData.executive_summary}
                </div>
              </div>

              <div>
                <h4 className="font-bold text-text-primary mb-1">Operational Action Taken</h4>
                <div className="bg-bg-surface p-3 rounded border border-border-subtle text-text-primary">
                  {reportData.operational_action_taken}
                </div>
              </div>

              <div>
                <h4 className="font-bold text-text-primary mb-1">Resolution Audit Trail</h4>
                <div className="bg-bg-surface p-3 rounded border border-border-subtle text-text-secondary font-mono text-[11px]">
                  {reportData.resolution_notes}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-text-muted">Select an incident to view report.</div>
          )}
        </div>
      </div>
    </div>
  );
};
