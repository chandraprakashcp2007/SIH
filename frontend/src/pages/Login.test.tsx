import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { Login } from './Login';

vi.mock('../services/api', () => ({ fetchAuthMode: vi.fn().mockResolvedValue({ dev_auth_bypass: false }), login: vi.fn() }));

describe('Login', () => {
  it('shows all five domain capability labels', () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    for (const id of ['JALA-01', 'AGNI-02', 'BHUMI-03', 'VAYU-04', 'AKASHA-05']) {
      expect(screen.getByText(id)).toBeInTheDocument();
    }
  });
});
