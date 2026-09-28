import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

describe('command shell', () => {
  it('groups navigation and links every Pancha Bhootha domain with exact identity', () => {
    render(<MemoryRouter><Sidebar collapsed={false} onToggleCollapse={() => undefined} /></MemoryRouter>);
    expect(screen.getByText('PANCHA BHOOTHA')).toBeInTheDocument();
    const links = { 'जल (JALA)': '/live/jala', 'अग्नि (AGNI)': '/live/agni', 'भूमि (BHUMI)': '/live/bhumi', 'वायु (VAYU)': '/live/vayu', 'आकाश (AKASHA)': '/live/akasha' };
    for (const [label, href] of Object.entries(links)) expect(screen.getByRole('link', { name: label })).toHaveAttribute('href', href);
    expect(screen.getByRole('navigation', { name: 'Primary command navigation' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Evidence Gate' })).toHaveAttribute('href', '/evidence-gate');
    expect(screen.getByRole('link', { name: 'Cross-Hazard Intelligence' })).toHaveAttribute('href', '/cascades');
    expect(screen.getByRole('link', { name: 'Digital Twin' })).toHaveAttribute('href', '/digital-twin');
    expect(screen.getByRole('link', { name: 'Impact & Evacuation' })).toHaveAttribute('href', '/impact');
    expect(screen.getByRole('link', { name: 'CAP Warning Centre' })).toHaveAttribute('href', '/cap');
    expect(screen.getByRole('link', { name: 'Offline Continuity' })).toHaveAttribute('href', '/continuity');
    expect(screen.getByRole('link', { name: 'Security Event Centre' })).toHaveAttribute('href', '/security');
  });

  it('identifies the active workspace and exposes an accessible logout action', () => {
    const logout = vi.fn();
    render(<MemoryRouter initialEntries={['/alerts']}><Navbar summary={{ network_mode: 'LOCAL_EDGE' }} onLogout={logout} /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: 'Alerts Centre' })).toBeInTheDocument();
    screen.getByRole('button', { name: 'Sign out of Command Centre' }).click();
    expect(logout).toHaveBeenCalledOnce();
  });
});
