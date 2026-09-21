import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SystemReadinessPage } from './SystemReadinessPage';
import * as api from '../services/api';

vi.mock('../services/api', () => ({ fetchReadiness: vi.fn() }));

describe('SystemReadinessPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders real check results and their semantic state', async () => {
    vi.mocked(api.fetchReadiness).mockResolvedValue({
      overall_status: 'DEGRADED', checked_at: '2026-09-21T10:00:00Z',
      checks: { database: { status: 'READY', detail: 'SQLite query succeeded' }, gateway: { status: 'DEGRADED', detail: 'stale' } },
    });
    render(<SystemReadinessPage />);
    expect(screen.getByText(/Checking backend/i)).toBeInTheDocument();
    expect(await screen.findByText('SQLite query succeeded')).toBeInTheDocument();
    expect(screen.getAllByText('DEGRADED').length).toBeGreaterThan(0);
  });

  it('shows a visible error and retries', async () => {
    vi.mocked(api.fetchReadiness).mockRejectedValueOnce(new Error('Gateway unavailable')).mockResolvedValueOnce({ overall_status: 'READY', checked_at: new Date().toISOString(), checks: {} });
    render(<SystemReadinessPage />);
    expect(await screen.findByRole('alert')).toHaveTextContent('Gateway unavailable');
    await userEvent.click(screen.getByText('Retry checks'));
    await waitFor(() => expect(screen.getAllByText('READY').length).toBeGreaterThan(0));
  });
});
