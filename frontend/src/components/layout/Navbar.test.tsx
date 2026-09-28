import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { Navbar } from './Navbar';

vi.mock('../../services/audioAlerts', () => ({
  audioAlertManager: { getEnabled: () => false, setEnabled: vi.fn() },
}));

describe('Navbar truth states', () => {
  it('never presents cached gateway state as operational', () => {
    render(<MemoryRouter><Navbar summary={{ gateway_status: 'CONNECTED', gateway_mode: 'REAL', network_mode: 'ONLINE', nodes_online: 5, nodes_total: 5, _dataState: { source: 'CACHED' } }} onLogout={vi.fn()} /></MemoryRouter>);
    expect(screen.getByLabelText('Status: CACHED')).toBeInTheDocument();
    expect(screen.queryByLabelText('Status: OPERATIONAL')).not.toBeInTheDocument();
  });
});
