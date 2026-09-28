import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { fetchEvidenceGateEvaluations } from '../services/api';
import { EvidenceGatePage } from './EvidenceGatePage';

vi.mock('../services/api', () => ({ fetchEvidenceGateEvaluations: vi.fn() }));

describe('intelligence route presentation', () => {
  it('explains the evidence decision pipeline and abstains when no evaluation exists', async () => {
    vi.mocked(fetchEvidenceGateEvaluations).mockResolvedValue([] as any);
    render(<EvidenceGatePage />);
    expect(await screen.findByText(/NO EVALUATIONS/)).toBeInTheDocument();
    for (const stage of ['RAW EVIDENCE', 'VALIDATION', 'TRUST', 'CORROBORATION', 'RISK DECISION']) expect(screen.getByText(stage)).toBeInTheDocument();
    expect(screen.getByText(/predictions remain COLLECTING/i)).toBeInTheDocument();
  });
});
