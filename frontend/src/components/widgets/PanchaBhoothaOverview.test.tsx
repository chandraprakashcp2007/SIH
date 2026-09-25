import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PanchaBhoothaOverview } from './PanchaBhoothaOverview';

const domains = [
  ['JALA-01', 'JALA', 'WATER', 'REAL', 'ESP8266 PROTOTYPE', 'AVAILABLE', '2026-09-25T10:00:00Z'],
  ['AGNI-02', 'AGNI', 'FIRE', 'SIMULATION', 'PLANNED FIELD NODE', 'AVAILABLE', '2026-09-25T10:00:00Z'],
  ['BHUMI-03', 'BHUMI', 'EARTH', 'REPLAY', 'PLANNED FIELD NODE', 'AVAILABLE', '2026-09-25T10:00:00Z'],
  ['VAYU-04', 'VAYU', 'AIR', 'PLANNED', 'PLANNED', 'NOT_IMPLEMENTED', null],
  ['AKASHA-05', 'AKASHA', 'ATMOSPHERE', 'EXTERNAL_DATA', 'PLANNED', 'NOT_IMPLEMENTED', null],
].map(([domain_id, display_name, element, source_mode, hardware_state, risk_engine_state, latest_update]) => ({
  domain_id, display_name, element, source_mode, hardware_state, risk_engine_state, latest_update,
}));

describe('PanchaBhoothaOverview', () => {
  it('renders all five domains and provenance badges', () => {
    render(<PanchaBhoothaOverview domains={domains as any} />);
    for (const name of ['JALA', 'AGNI', 'BHUMI', 'VAYU', 'AKASHA']) {
      expect(screen.getByText(name)).toBeInTheDocument();
    }
    for (const mode of ['REAL', 'SIMULATION', 'REPLAY', 'PLANNED', 'EXTERNAL DATA']) {
      expect(screen.getAllByText(mode).length).toBeGreaterThan(0);
    }
  });

  it('shows no fake readings or update time for planned domains', () => {
    render(<PanchaBhoothaOverview domains={domains as any} />);
    expect(screen.getAllByText('No live physical telemetry').length).toBe(2);
    expect(screen.queryByText(/PM2\.5|wind speed|risk %/i)).not.toBeInTheDocument();
  });
});
