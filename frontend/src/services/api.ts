/**
 * PRAHARI-NET API Client Service
 */

import { fetchOperationalJson } from './cache';

const BASE_URL = '/api';

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('prahari_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function fetchSystemSummary() {
  return fetchOperationalJson<any>('system-summary', `${BASE_URL}/system/summary`, { headers: getHeaders() });
}

export async function fetchNodes() {
  return fetchOperationalJson<any[]>('nodes', `${BASE_URL}/nodes`, { headers: getHeaders() });
}

export async function fetchElements() {
  const res = await fetch(`${BASE_URL}/elements`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch Pancha Bhootha registry');
  return res.json();
}

export async function fetchGeoDomain(domain: string) {
  const res = await fetch(`${BASE_URL}/geo/domains/${encodeURIComponent(domain)}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load ${domain} geo-intelligence (HTTP ${res.status})`);
  return res.json();
}

export async function fetchGeoDatasets() {
  const res = await fetch(`${BASE_URL}/geo/datasets`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load geospatial dataset registry (HTTP ${res.status})`);
  return res.json();
}

export async function fetchSensorHealth(nodeId?: string) {
  const query = nodeId ? `?node_id=${encodeURIComponent(nodeId)}` : '';
  const res = await fetch(`${BASE_URL}/sensor-health${query}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load sensor health (HTTP ${res.status})`);
  return res.json();
}

export async function fetchObservationAggregate(nodeId: string, observedProperty: string, range = '1h') {
  const params = new URLSearchParams({ node_id: nodeId, observed_property: observedProperty, range });
  const res = await fetch(`${BASE_URL}/observations/aggregate?${params}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load observation history (HTTP ${res.status})`);
  return res.json();
}

export async function fetchEvidenceGateEvaluations() {
  const res = await fetch(`${BASE_URL}/evidence-gate/evaluations`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load Evidence Gate evaluations (HTTP ${res.status})`);
  return res.json();
}

export async function fetchCrossHazardIntelligence() {
  const [relationships, compoundRisks, consensus] = await Promise.all([
    fetch(`${BASE_URL}/cascades`, { headers: getHeaders() }),
    fetch(`${BASE_URL}/compound-risk`, { headers: getHeaders() }),
    fetch(`${BASE_URL}/consensus`, { headers: getHeaders() }),
  ]);
  for (const response of [relationships, compoundRisks, consensus]) {
    if (!response.ok) throw new Error(`Failed to load cross-hazard intelligence (HTTP ${response.status})`);
  }
  return {
    relationships: await relationships.json(),
    compoundRisks: await compoundRisks.json(),
    consensus: await consensus.json(),
  };
}

export async function reevaluateCrossHazards() {
  const res = await fetch(`${BASE_URL}/cascades/reevaluate`, { method: 'POST', headers: getHeaders() });
  if (!res.ok) throw new Error(`Cross-hazard reevaluation failed (HTTP ${res.status})`);
  return res.json();
}

export async function fetchJalaDownstreamIntelligence() {
  const [topology, threats] = await Promise.all([
    fetch(`${BASE_URL}/jala/topology`, { headers: getHeaders() }),
    fetch(`${BASE_URL}/jala/downstream-threats`, { headers: getHeaders() }),
  ]);
  if (!topology.ok || !threats.ok) throw new Error('Failed to load JALA downstream intelligence');
  return { topology: await topology.json(), threats: await threats.json() };
}

export async function evaluateJalaDownstreamThreats() {
  const res = await fetch(`${BASE_URL}/jala/downstream-threats/evaluate`, { method: 'POST', headers: getHeaders() });
  if (!res.ok) throw new Error('JALA downstream evaluation failed');
  return res.json();
}
export async function fetchDigitalTwins() { const r=await fetch(`${BASE_URL}/digital-twin`,{headers:getHeaders()}); if(!r.ok) throw new Error('Failed to load digital twins'); return r.json(); }
export async function refreshDigitalTwins() { const r=await fetch(`${BASE_URL}/digital-twin/refresh`,{method:'POST',headers:getHeaders()}); if(!r.ok) throw new Error('Failed to refresh digital twins'); return r.json(); }
export async function evaluateImpact(){const r=await fetch(`${BASE_URL}/impact/evaluate`,{method:'POST',headers:getHeaders()});if(!r.ok)throw new Error('Impact evaluation failed');return r.json()}
export async function evaluateEvacuation(){const r=await fetch(`${BASE_URL}/evacuation/evaluate`,{method:'POST',headers:getHeaders()});if(!r.ok)throw new Error('Evacuation evaluation failed');return r.json()}
export async function fetchSafeZones(){const r=await fetch(`${BASE_URL}/safe-zones`,{headers:getHeaders()});if(!r.ok)throw new Error('Safe-zone registry unavailable');return r.json()}
export async function fetchCAPCentre(){const [s,e,d]=await Promise.all([fetch(`${BASE_URL}/cap/status`,{headers:getHeaders()}),fetch(`${BASE_URL}/cap/exports`,{headers:getHeaders()}),fetch(`${BASE_URL}/cap/deliveries`,{headers:getHeaders()})]);if(!s.ok||!e.ok||!d.ok)throw new Error('CAP centre unavailable');return {status:await s.json(),exports:await e.json(),deliveries:await d.json()}}
export async function exportCAP(alertId:string,languages=['en-IN','hi-IN']){const r=await fetch(`${BASE_URL}/cap/alerts/${encodeURIComponent(alertId)}/export`,{method:'POST',headers:getHeaders(),body:JSON.stringify({languages})});if(!r.ok)throw new Error(`CAP export failed (HTTP ${r.status})`);return r.json()}
export async function fetchContinuity(){const [s,q,t]=await Promise.all([fetch(`${BASE_URL}/continuity/status`,{headers:getHeaders()}),fetch(`${BASE_URL}/continuity/queue`,{headers:getHeaders()}),fetch(`${BASE_URL}/continuity/transports`,{headers:getHeaders()})]);if(!s.ok||!q.ok||!t.ok)throw new Error('Continuity service unavailable');return {status:await s.json(),queue:await q.json(),transports:await t.json()}}
export async function evaluateContinuity(payload:any){const r=await fetch(`${BASE_URL}/continuity/evaluate`,{method:'POST',headers:getHeaders(),body:JSON.stringify(payload)});if(!r.ok)throw new Error('Continuity evaluation failed');return r.json()}

export async function fetchNode(id: string) {
  const res = await fetch(`${BASE_URL}/nodes/${id}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch node ${id}`);
  return res.json();
}

export async function fetchNodeTelemetry(id: string, limit = 60) {
  const res = await fetch(`${BASE_URL}/nodes/${id}/telemetry?limit=${limit}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch telemetry for node ${id}`);
  return res.json();
}

export async function fetchNodeRisk(id: string, limit = 60) {
  const res = await fetch(`${BASE_URL}/nodes/${id}/risk?limit=${limit}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch risk history for node ${id}`);
  return res.json();
}

export async function fetchAlerts(state?: string, severity?: string) {
  let url = `${BASE_URL}/alerts?limit=100`;
  if (state) url += `&state=${state}`;
  if (severity) url += `&severity=${severity}`;
  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

export async function acknowledgeAlert(alertId: string, notes?: string) {
  const user = JSON.parse(localStorage.getItem('prahari_user') || '{}');
  const res = await fetch(`${BASE_URL}/alerts/${alertId}/acknowledge`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ acknowledged_by: user.username || 'operator', notes }),
  });
  if (!res.ok) throw new Error('Failed to acknowledge alert');
  return res.json();
}

export async function resolveAlert(alertId: string, resolutionNotes: string) {
  const user = JSON.parse(localStorage.getItem('prahari_user') || '{}');
  const res = await fetch(`${BASE_URL}/alerts/${alertId}/resolve`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ resolved_by: user.username || 'operator', resolution_notes: resolutionNotes }),
  });
  if (!res.ok) throw new Error('Failed to resolve alert');
  return res.json();
}

export async function fetchPredictions() {
  const res = await fetch(`${BASE_URL}/predictions`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch predictions');
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${BASE_URL}/analytics/overview`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}

export async function fetchNetworkStatus() {
  return fetchOperationalJson<any>('network', `${BASE_URL}/network/status`, { headers: getHeaders() });
}

export async function fetchNetworkPackets(limit = 40) {
  const res = await fetch(`${BASE_URL}/network/packets?limit=${limit}`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch network packets');
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${BASE_URL}/simulator/scenarios`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch simulation scenarios');
  return res.json();
}

export async function triggerScenario(scenarioName: string) {
  const res = await fetch(`${BASE_URL}/simulator/scenario/${scenarioName}`, {
    method: 'POST',
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to trigger scenario ${scenarioName}`);
  return res.json();
}

export async function resetSimulator() {
  const res = await fetch(`${BASE_URL}/simulator/reset`, {
    method: 'POST',
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error('Failed to reset simulator');
  return res.json();
}

export async function sendCopilotChat(message: string) {
  const res = await fetch(`${BASE_URL}/copilot/chat`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error('Failed to communicate with Copilot');
  return res.json();
}

export async function fetchCopilotSessions() {
  const res = await fetch(`${BASE_URL}/copilot/sessions`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to load Copilot sessions');
  return res.json();
}

export async function createCopilotSession(title = 'Operational Inquiry') {
  const res = await fetch(`${BASE_URL}/copilot/sessions`, { method: 'POST', headers: getHeaders(), body: JSON.stringify({ title }) });
  if (!res.ok) throw new Error('Failed to create Copilot session');
  return res.json();
}

export async function fetchCopilotMessages(sessionId: string) {
  const res = await fetch(`${BASE_URL}/copilot/sessions/${sessionId}/messages`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to load conversation');
  return res.json();
}

export async function deleteCopilotSession(sessionId: string) {
  const res = await fetch(`${BASE_URL}/copilot/sessions/${sessionId}`, { method: 'DELETE', headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to clear conversation');
}

export async function streamCopilotChat(
  query: string,
  sessionId: string | null,
  signal: AbortSignal,
  onEvent: (event: string, data: any) => void,
) {
  const params = new URLSearchParams({ query });
  if (sessionId) params.set('session_id', sessionId);
  const res = await fetch(`${BASE_URL}/copilot/stream?${params}`, { headers: getHeaders(), signal });
  if (!res.ok || !res.body) throw new Error('Copilot stream unavailable');
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split('\n\n');
    buffer = frames.pop() || '';
    for (const frame of frames) {
      const event = frame.match(/^event:\s*(.+)$/m)?.[1];
      const raw = frame.match(/^data:\s*(.+)$/m)?.[1];
      if (event && raw) onEvent(event, JSON.parse(raw));
    }
  }
}

export async function fetchSystemLogs(category?: string) {
  let url = `${BASE_URL}/logs?limit=100`;
  if (category) url += `&category=${category}`;
  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch system logs');
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${BASE_URL}/settings`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function saveSettings(settings: any) {
  const res = await fetch(`${BASE_URL}/settings`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ settings }),
  });
  if (!res.ok) throw new Error('Failed to save settings');
  return res.json();
}

export async function login(username: string, password: string) {
  let res: Response;

  try {
    res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw new Error(
      'Authentication service is unavailable. Make sure the PRAHARI backend is running.'
    );
  }

  const raw = await res.text();

  let data: any = null;

  if (raw.trim()) {
    try {
      data = JSON.parse(raw);
    } catch {
      if (!res.ok) {
        throw new Error(`Authentication failed (HTTP ${res.status}).`);
      }

      throw new Error(
        'Authentication service returned an invalid response. Please restart the backend.'
      );
    }
  }

  if (!res.ok) {
    const detail =
      data?.detail ||
      data?.message ||
      `Login failed (HTTP ${res.status}).`;

    throw new Error(detail);
  }

  if (!data || !data.access_token) {
    throw new Error(
      'Authentication succeeded but no access token was returned.'
    );
  }

  return data;
}

export async function fetchAuthMode() {
  let res: Response;

  try {
    res = await fetch(`${BASE_URL}/auth/mode`);
  } catch {
    return {
      dev_auth_bypass: false,
      mode: 'OFFLINE',
      backend_available: false,
    };
  }

  const raw = await res.text();

  if (!raw.trim()) {
    return {
      dev_auth_bypass: false,
      mode: res.ok ? 'UNKNOWN' : 'OFFLINE',
      backend_available: res.ok,
    };
  }

  try {
    const data = JSON.parse(raw);

    return {
      ...data,
      backend_available: true,
    };
  } catch {
    return {
      dev_auth_bypass: false,
      mode: 'UNKNOWN',
      backend_available: false,
    };
  }
}

export async function fetchReadiness() {
  return fetchOperationalJson<any>('readiness', `${BASE_URL}/readiness`, { headers: getHeaders() });
}

export async function fetchCalibration() {
  const res = await fetch(`${BASE_URL}/calibration`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load calibration (HTTP ${res.status}): ${(await res.text()) || res.statusText}`);
  return res.json();
}

export async function saveCalibration(nodeId: string, values: Record<string, number>) {
  const res = await fetch(`${BASE_URL}/calibration`, {
    method: 'PUT', headers: getHeaders(), body: JSON.stringify({ node_id: nodeId, values }),
  });
  if (!res.ok) throw new Error(`Failed to save calibration (HTTP ${res.status}): ${(await res.text()) || res.statusText}`);
  return res.json();
}

export async function fetchExternalProviderStatus() {
  const res = await fetch(`${BASE_URL}/external/status`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load external providers (HTTP ${res.status})`);
  return res.json();
}

export async function fetchExternalObservations() {
  const res = await fetch(`${BASE_URL}/external/observations?limit=50`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to load external observations (HTTP ${res.status})`);
  return res.json();
}


