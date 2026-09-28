import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchAuthMode, login } from '../services/api';
import { Login } from './Login';

vi.mock('../services/api', () => ({ fetchAuthMode: vi.fn(), login: vi.fn() }));

describe('cinematic PRAHARI login', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.mocked(fetchAuthMode).mockResolvedValue({ dev_auth_bypass: false } as any);
    vi.mocked(login).mockResolvedValue({ access_token: 'token', user: { username: 'operator', role: 'OPERATOR' } } as any);
  });

  it('renders the exact identity and all five operational node IDs', () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    expect(screen.getAllByText('पंजापुतम्').length).toBeGreaterThan(0);
    for (const id of ['JALA-01', 'AGNI-02', 'BHUMI-03', 'VAYU-04', 'AKASHA-05']) expect(screen.getByText(id)).toBeInTheDocument();
  });

  it('submits labeled credentials through the existing authentication contract', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><Login /></MemoryRouter>);
    await user.type(screen.getByLabelText('Username'), 'operator');
    await user.type(screen.getByLabelText('Password'), 'secure-value');
    await user.click(screen.getByRole('button', { name: 'Access Command Centre' }));
    await waitFor(() => expect(login).toHaveBeenCalledWith('operator', 'secure-value'));
    expect(localStorage.getItem('prahari_token')).toBe('token');
  });

  it('never renders local bypass affordances when the backend disables them', async () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    await waitFor(() => expect(fetchAuthMode).toHaveBeenCalled());
    expect(screen.queryByText(/DEV AUTH BYPASS/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Local jury demo shortcuts/i)).not.toBeInTheDocument();
    expect(screen.queryByText('local-demo')).not.toBeInTheDocument();
  });
});
