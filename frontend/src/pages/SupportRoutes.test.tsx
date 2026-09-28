import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { fetchSecurityCentre } from '../services/api';
import { SecurityCentrePage } from './SecurityCentrePage';

vi.mock('../services/api', () => ({ fetchSecurityCentre: vi.fn() }));

describe('assurance and support presentation', () => {
  it('shows security truth states without exposing device secrets', async () => {
    vi.mocked(fetchSecurityCentre).mockResolvedValue({ status: { signed_telemetry: 'NOT_CONFIGURED', replay_protection: 'OPERATIONAL' }, chain: { valid: true }, events: [] } as any);
    render(<SecurityCentrePage />);
    expect((await screen.findAllByText('NOT CONFIGURED')).length).toBeGreaterThan(0);
    expect(screen.getAllByText('OPERATIONAL').length).toBeGreaterThan(0);
    expect(screen.getAllByText('VALID').length).toBeGreaterThan(0);
    expect(screen.getByText(/Device secrets.*never returned/i)).toBeInTheDocument();
    expect(screen.queryByText(/password|secret=/i)).not.toBeInTheDocument();
  });

  it('does not claim a clear audit queue when the request fails', async () => {
    vi.mocked(fetchSecurityCentre).mockRejectedValue(new Error('network unavailable'));
    render(<SecurityCentrePage />);
    expect(await screen.findByText('Security events unavailable')).toBeInTheDocument();
    expect(screen.queryByText('CLEAR AUDIT QUEUE')).not.toBeInTheDocument();
  });
});
