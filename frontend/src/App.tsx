import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

const load = <T,>(factory: () => Promise<T>, key: keyof T) => lazy(async () => ({ default: (await factory())[key] as React.ComponentType<any> }));
const Layout = load(() => import('./components/layout/Layout'), 'Layout');
const Login = load(() => import('./pages/Login'), 'Login');
const CommandCentre = load(() => import('./pages/CommandCentre'), 'CommandCentre');
const MapPage = load(() => import('./pages/MapPage'), 'MapPage');
const Nodes = load(() => import('./pages/Nodes'), 'Nodes');
const NodeDetail = load(() => import('./pages/NodeDetail'), 'NodeDetail');
const AlertCentre = load(() => import('./pages/AlertCentre'), 'AlertCentre');
const PredictionsPage = load(() => import('./pages/PredictionsPage'), 'PredictionsPage');
const AnalyticsPage = load(() => import('./pages/AnalyticsPage'), 'AnalyticsPage');
const NetworkPage = load(() => import('./pages/NetworkPage'), 'NetworkPage');
const DeviceHealthPage = load(() => import('./pages/DeviceHealthPage'), 'DeviceHealthPage');
const AiIntelligencePage = load(() => import('./pages/AiIntelligencePage'), 'AiIntelligencePage');
const EventHistoryPage = load(() => import('./pages/EventHistoryPage'), 'EventHistoryPage');
const ReportsPage = load(() => import('./pages/ReportsPage'), 'ReportsPage');
const SystemLogsPage = load(() => import('./pages/SystemLogsPage'), 'SystemLogsPage');
const SimulatorPage = load(() => import('./pages/SimulatorPage'), 'SimulatorPage');
const SettingsPage = load(() => import('./pages/SettingsPage'), 'SettingsPage');
const DemoWalkthroughPage = load(() => import('./pages/DemoWalkthroughPage'), 'DemoWalkthroughPage');
const CalibrationPage = load(() => import('./pages/CalibrationPage'), 'CalibrationPage');
const SystemReadinessPage = load(() => import('./pages/SystemReadinessPage'), 'SystemReadinessPage');
const ExternalDataPage = load(() => import('./pages/ExternalDataPage'), 'ExternalDataPage');
const DatasetManagerPage = load(() => import('./pages/DatasetManagerPage'), 'DatasetManagerPage');

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) =>
  localStorage.getItem('prahari_token') ? <>{children}</> : <Navigate to="/login" replace />;

const RouteLoader = () => <div role="status" className="min-h-screen bg-bg-primary p-8 text-sm text-text-muted animate-pulse">Preparing secure command workspace…</div>;

export function App() {
  return <BrowserRouter><Suspense fallback={<RouteLoader />}><Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
      <Route index element={<CommandCentre />} /><Route path="map" element={<MapPage />} />
      <Route path="nodes" element={<Nodes />} /><Route path="nodes/:nodeId" element={<NodeDetail />} />
      <Route path="alerts" element={<AlertCentre />} /><Route path="predictions" element={<PredictionsPage />} />
      <Route path="analytics" element={<AnalyticsPage />} /><Route path="network" element={<NetworkPage />} />
      <Route path="health" element={<DeviceHealthPage />} /><Route path="ai" element={<AiIntelligencePage />} />
      <Route path="events" element={<EventHistoryPage />} /><Route path="reports" element={<ReportsPage />} />
      <Route path="logs" element={<SystemLogsPage />} /><Route path="simulator" element={<SimulatorPage />} />
      <Route path="settings" element={<SettingsPage />} /><Route path="calibration" element={<CalibrationPage />} />
      <Route path="readiness" element={<SystemReadinessPage />} /><Route path="copilot" element={<AiIntelligencePage />} />
      <Route path="external-data" element={<ExternalDataPage />} /><Route path="datasets" element={<DatasetManagerPage />} />
      <Route path="demo" element={<DemoWalkthroughPage />} />
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></Suspense></BrowserRouter>;
}

export default App;
