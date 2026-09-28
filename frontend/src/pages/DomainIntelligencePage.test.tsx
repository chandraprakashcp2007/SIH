import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { fetchGeoDomain } from '../services/api';
import { DomainIntelligencePage } from './DomainIntelligencePage';

vi.mock('../services/api', () => ({ fetchGeoDomain: vi.fn() }));
vi.mock('../components/map/domains/JalaFloodMap', () => ({ JalaFloodMap: () => <div aria-label="Interactive domain map" /> }));
vi.mock('../components/map/domains/AgniFireMap', () => ({ AgniFireMap: () => <div aria-label="Interactive domain map" /> }));
vi.mock('../components/map/domains/BhumiLandslideMap', () => ({ BhumiLandslideMap: () => <div aria-label="Interactive domain map" /> }));
vi.mock('../components/map/domains/VayuAirMap', () => ({ VayuAirMap: () => <div aria-label="Interactive domain map" /> }));
vi.mock('../components/map/domains/AkashaWeatherMap', () => ({ AkashaWeatherMap: () => <div aria-label="Interactive domain map" /> }));

const domainPayload = (domain: string, nodeId: string, layerId = `${domain}_PRIMARY`) => ({
  generated_at: '2026-09-28T10:00:00Z',
  features: [{ geometry: { coordinates: [77, 22] }, properties: { node_id: nodeId, provenance: 'SIMULATION', risk_band: 'NO_DATA', metrics: {}, freshness_seconds: null } }],
  layers: [{ id: layerId, status: 'NOT_CONFIGURED', provenance: 'PLANNED' }],
});

describe('domain intelligence experience', () => {
  it('shows exact JALA identity, source provenance, and prediction abstention when evidence is absent', async () => {
    vi.mocked(fetchGeoDomain).mockResolvedValue(domainPayload('JALA', 'JALA-01') as any);
    render(<DomainIntelligencePage domain="JALA" />);
    expect(await screen.findByRole('heading', { name: /जल \(JALA\).*Flood & River Surge Intelligence/ })).toBeInTheDocument();
    expect(screen.getByText('JALA-01')).toBeInTheDocument();
    expect(screen.getAllByText('SIMULATION').length).toBeGreaterThan(0);
    expect(screen.getByText('Prediction unavailable in this response')).toBeInTheDocument();
    expect(screen.getByText(/Open Predictions for evidence-gated forecast/i)).toBeInTheDocument();
  });

  it('states that unavailable AKASHA imagery is not configured', async () => {
    vi.mocked(fetchGeoDomain).mockResolvedValue(domainPayload('AKASHA', 'AKASHA-05', 'radar_satellite') as any);
    render(<DomainIntelligencePage domain="AKASHA" />);
    expect(await screen.findByText('AKASHA-05')).toBeInTheDocument();
    expect(screen.getByText('WEATHER WARNING / RADAR-SATELLITE LAYERS — NOT CONFIGURED')).toBeInTheDocument();
  });

  it('does not infer provider configuration from an unrelated unavailable layer', async () => {
    vi.mocked(fetchGeoDomain).mockResolvedValue(domainPayload('AKASHA', 'AKASHA-05', 'rainfall') as any);
    render(<DomainIntelligencePage domain="AKASHA" />);
    expect(await screen.findByText('AKASHA-05')).toBeInTheDocument();
    expect(screen.queryByText('WEATHER WARNING / RADAR-SATELLITE LAYERS — NOT CONFIGURED')).not.toBeInTheDocument();
  });
});
