import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Sidebar } from './Sidebar';

describe('Sidebar', () => {
  it('shows the Pancha Bhootham section and every node route', () => {
    render(<MemoryRouter><Sidebar collapsed={false} onToggleCollapse={() => undefined} /></MemoryRouter>);
    expect(screen.getByText('PANCHA BHOOTHAM')).toBeInTheDocument();
    for (const label of ['JALA (Flood)', 'AGNI (Fire)', 'BHUMI (Landslide)', 'VAYU (Air)', 'AKASHA (Atmosphere)']) {
      expect(screen.getByRole('link', { name: label })).toBeInTheDocument();
    }
  });
});
