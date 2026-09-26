import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DeviceHealthPage } from './DeviceHealthPage';

vi.mock('../services/api', () => ({
  fetchSensorHealth: vi.fn().mockResolvedValue([{
    id: 'h1', node_id: 'JALA-01', sensor_id: 'JALA-01:water_level_cm',
    state: 'DEGRADED', trust_score: 62, noise_score: null, drift_score: null,
    missing_data_pct: 0, battery_pct: 90, rssi: -70,
    calibration_state: 'NOT_CONFIGURED', firmware_version: 'TEST',
    provenance: 'SIMULATION', reason_codes: ['REDUCED_TRUST'],
    recorded_at: '2026-09-27T00:00:00Z',
  }]),
}));

vi.mock('../services/websocket', () => ({ wsClient: { subscribe: () => () => undefined } }));

describe('DeviceHealthPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders persisted sensor status, provenance and honest calibration state', async () => {
    render(<DeviceHealthPage />);
    expect(await screen.findByText('JALA-01:water_level_cm')).toBeInTheDocument();
    expect(screen.getByText('DEGRADED')).toBeInTheDocument();
    expect(screen.getByText('NOT_CONFIGURED')).toBeInTheDocument();
    expect(screen.getByText('SIMULATION')).toBeInTheDocument();
    expect(screen.queryByText(/45 days/i)).not.toBeInTheDocument();
  });
});
