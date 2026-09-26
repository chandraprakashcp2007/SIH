import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Sidebar } from './Sidebar';

describe('Sidebar', () => {
  it('links every Pancha Bhootha domain to its dedicated live map', () => {
    render(<MemoryRouter><Sidebar collapsed={false} onToggleCollapse={() => undefined} /></MemoryRouter>);
    expect(screen.getByText('PANCHA BHOOTHAM')).toBeInTheDocument();
    const links = {
      'JALA (Flood)': '/live/jala',
      'AGNI (Fire)': '/live/agni',
      'BHUMI (Landslide)': '/live/bhumi',
      'VAYU (Air)': '/live/vayu',
      'AKASHA (Atmosphere)': '/live/akasha',
    };
    for (const [label, href] of Object.entries(links)) {
      expect(screen.getByRole('link', { name: label })).toHaveAttribute('href', href);
    }
    expect(screen.getByRole('link', { name: 'Evidence Gate' })).toHaveAttribute('href', '/evidence-gate');
  });
});
