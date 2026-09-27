import React from 'react';
import { NativeHazardMapBase, type DomainLayer, type NativeHazardMapFeature } from './NativeHazardMapBase';

export const JalaFloodMap: React.FC<{ feature: NativeHazardMapFeature; layers: DomainLayer[] }> = (props) => (
  <NativeHazardMapBase
    {...props}
    config={{
      domain: 'JALA', testId: 'jala-hydrology-map', modeClass: 'jala', mapLabel: 'जल (JALA) · Hydrological Intelligence',
      accent: '#22d3ee', markerText: 'जल', zoom: 8,
      legend: [
        { label: 'Node / gauge evidence', color: '#22d3ee' },
        { label: 'Safe', color: '#22c55e' },
        { label: 'Watch', color: '#eab308' },
        { label: 'Critical', color: '#ef4444' },
      ],
      controls: ['Hydrology', 'Rainfall', 'Gauges', 'Topology', 'Evidence Gate'],
    }}
  />
);
