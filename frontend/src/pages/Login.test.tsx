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

describe('prahari premium identity', () => {
  it('renders Panjaputham identity without exposing production demo password', () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    expect(screen.getAllByText('पंजापुतम').length).toBeGreaterThan(0);
    expect(screen.queryByText('prahari2026!')).not.toBeInTheDocument();
    expect(screen.queryByText(/DEV AUTH BYPASS/)).not.toBeInTheDocument();
  });
});
