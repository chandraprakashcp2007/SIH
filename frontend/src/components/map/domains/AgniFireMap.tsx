import React from 'react';
import { NativeHazardMapBase, type DomainLayer, type NativeHazardMapFeature } from './NativeHazardMapBase';

export const AgniFireMap: React.FC<{ feature: NativeHazardMapFeature; layers: DomainLayer[] }> = (props) => (
  <NativeHazardMapBase
    {...props}
    config={{
      domain: 'AGNI', testId: 'agni-fire-map', modeClass: 'agni', mapLabel: 'अग्नि (AGNI) · Fire & Smoke Intelligence',
      accent: '#fb923c', markerText: 'अ', zoom: 8,
      legend: [
        { label: 'Local fire evidence', color: '#fb923c' },
        { label: 'Smoke / gas', color: '#f59e0b' },
        { label: 'Wind context', color: '#a78bfa' },
        { label: 'Critical', color: '#ef4444' },
      ],
      controls: ['Fire Risk', 'Smoke', 'Wind', 'VAYU Link', 'FIRMS status'],
    }}
  />
);
