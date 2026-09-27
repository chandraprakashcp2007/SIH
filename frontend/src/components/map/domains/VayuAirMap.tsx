import React from 'react';
import { NativeHazardMapBase, type DomainLayer, type NativeHazardMapFeature } from './NativeHazardMapBase';

export const VayuAirMap: React.FC<{ feature: NativeHazardMapFeature; layers: DomainLayer[] }> = (props) => (
  <NativeHazardMapBase
    {...props}
    config={{
      domain: 'VAYU', testId: 'vayu-air-map', modeClass: 'vayu', mapLabel: 'वायु (VAYU) · Air, Smoke & Gas Intelligence',
      accent: '#c084fc', markerText: 'वा', zoom: 9,
      legend: [
        { label: 'Gas / smoke evidence', color: '#c084fc' },
        { label: 'Air model context', color: '#22d3ee' },
        { label: 'AGNI relationship', color: '#fb923c' },
        { label: 'Insufficient', color: '#64748b' },
      ],
      controls: ['Air Model', 'Gas', 'Smoke', 'Wind', 'AGNI Link'],
    }}
  />
);
