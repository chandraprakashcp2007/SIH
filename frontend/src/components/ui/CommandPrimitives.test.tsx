import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import {
  EmptyState,
  GlassPanel,
  MetricCard,
  SectionHeader,
  SourceBadge,
  StatusBadge,
} from './CommandPrimitives';

describe('command primitives', () => {
  it('keeps section hierarchy and supporting context semantic', () => {
    render(<SectionHeader eyebrow="Evidence fabric" title="Trust assessment" description="Validated observations only" />);
    expect(screen.getByRole('heading', { name: 'Trust assessment', level: 2 })).toBeInTheDocument();
    expect(screen.getByText('Evidence fabric')).toBeInTheDocument();
    expect(screen.getByText('Validated observations only')).toBeInTheDocument();
  });

  it('announces status and source mode as text rather than color alone', () => {
    render(<><StatusBadge status="DEGRADED" /><SourceBadge source="EXTERNAL_DATA" /></>);
    expect(screen.getByText('DEGRADED')).toHaveAttribute('aria-label', 'Status: DEGRADED');
    expect(screen.getByText('EXTERNAL DATA')).toHaveAttribute('aria-label', 'Source: EXTERNAL DATA');
  });

  it('offers a usable recovery action for an unavailable region', () => {
    const retry = vi.fn();
    render(<EmptyState title="Telemetry unavailable" detail="The gateway did not answer." actionLabel="Retry connection" onAction={retry} />);
    screen.getByRole('button', { name: 'Retry connection' }).click();
    expect(retry).toHaveBeenCalledOnce();
  });

  it('renders reusable glass and metric surfaces without losing their labels', () => {
    render(<GlassPanel aria-label="Operational panel"><MetricCard label="Operational nodes" value="4 / 5" detail="Validated now" /></GlassPanel>);
    expect(screen.getByRole('region', { name: 'Operational panel' })).toBeInTheDocument();
    expect(screen.getByText('Operational nodes')).toBeInTheDocument();
    expect(screen.getByText('4 / 5')).toBeInTheDocument();
  });
});
