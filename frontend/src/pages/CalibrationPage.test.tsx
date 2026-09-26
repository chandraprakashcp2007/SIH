import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { CalibrationPage } from './CalibrationPage';

vi.mock('../services/api', () => ({
  fetchCalibration: vi.fn().mockResolvedValue({ nodes: {
    'JALA-01': { water_level_offset_cm: 0 }, 'AGNI-02': { mq2_baseline: 115 },
    'BHUMI-03': { vibration_zero: 0.45 }, 'VAYU-04': { pm2_5_offset: 0 },
    'AKASHA-05': { pressure_offset_hpa: 0 },
  }}),
  saveCalibration: vi.fn(),
}));

describe('CalibrationPage', () => {
  beforeEach(() => localStorage.setItem('prahari_user', JSON.stringify({ role: 'OPERATOR' })));
  it('renders five cards as read-only for an operator', async () => {
    render(<CalibrationPage />);
    expect(await screen.findByText('AKASHA-05')).toBeInTheDocument();
    expect(screen.getByText(/Read-only view/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Save calibration/ })).not.toBeInTheDocument();
    expect(screen.getAllByRole('spinbutton')).toHaveLength(5);
    expect(screen.getAllByRole('spinbutton').every((item) => item.hasAttribute('disabled'))).toBe(true);
  });
});
