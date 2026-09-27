import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Sidebar } from './Sidebar';

describe('Sidebar', () => {
  it('links every Pancha Bhootha domain to its dedicated live map', () => {
    render(<MemoryRouter><Sidebar collapsed={false} onToggleCollapse={() => undefined} /></MemoryRouter>);
    expect(screen.getByText('PANCHA BHOOTHAM')).toBeInTheDocument();
    const links = {
      'जल (JALA) · Flood': '/live/jala',
      'अग्नि (AGNI) · Fire': '/live/agni',
      'भूमि (BHUMI) · Landslide': '/live/bhumi',
      'वायु (VAYU) · Air': '/live/vayu',
      'आकाश (AKASHA) · Atmosphere': '/live/akasha',
    };
    for (const [label, href] of Object.entries(links)) {
      expect(screen.getByRole('link', { name: label })).toHaveAttribute('href', href);
    }
    expect(screen.getByRole('link', { name: 'Evidence Gate' })).toHaveAttribute('href', '/evidence-gate');
    expect(screen.getByRole('link', { name: 'Cross-Hazard Intelligence' })).toHaveAttribute('href', '/cascades');
    expect(screen.getByRole('link', { name: 'Digital Twin' })).toHaveAttribute('href', '/digital-twin');
    expect(screen.getByRole('link', { name: 'Impact & Evacuation' })).toHaveAttribute('href', '/impact');
    expect(screen.getByRole('link', { name: 'CAP Warning Centre' })).toHaveAttribute('href', '/cap');
    expect(screen.getByRole('link', { name: 'Offline Continuity' })).toHaveAttribute('href', '/continuity');
    expect(screen.getByRole('link', { name: 'Security Event Centre' })).toHaveAttribute('href', '/security');
  });
});
