import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { fetchCrossHazardIntelligence, reevaluateCrossHazards } from '../services/api';
import { CrossHazardPage } from './CrossHazardPage';

vi.mock('../services/api', () => ({
  fetchCrossHazardIntelligence: vi.fn(),
  reevaluateCrossHazards: vi.fn(),
}));

describe('CrossHazardPage', () => {
  it('prevents reevaluation until the initial snapshot has loaded', async () => {
    let resolveInitial!: (value: any) => void;
    vi.mocked(fetchCrossHazardIntelligence).mockReturnValue(new Promise(resolve => { resolveInitial = resolve; }) as any);
    vi.mocked(reevaluateCrossHazards).mockResolvedValue({ relationships: [], compound_risks: [], consensus: [] } as any);

    render(<CrossHazardPage />);
    const button = screen.getByRole('button', { name: 'Reevaluate' });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(reevaluateCrossHazards).not.toHaveBeenCalled();

    resolveInitial({ relationships: [], compoundRisks: [], consensus: [] });
    await waitFor(() => expect(button).toBeEnabled());
  });
});
