import React from 'react';
import { NativeHazardMapBase, type DomainLayer, type NativeHazardMapFeature } from './NativeHazardMapBase';

export const BhumiLandslideMap: React.FC<{ feature: NativeHazardMapFeature; layers: DomainLayer[] }> = (props) => (
  <NativeHazardMapBase
    {...props}
    config={{
      domain: 'BHUMI', testId: 'bhumi-landslide-map', modeClass: 'bhumi', mapLabel: 'भूमि (BHUMI) · Slope & Landslide Intelligence',
      accent: '#86efac', markerText: 'भू', zoom: 9,
      legend: [
        { label: 'Soil / tilt evidence', color: '#86efac' },
        { label: 'Susceptibility planned', color: '#eab308' },
        { label: 'Rain context', color: '#38bdf8' },
        { label: 'Insufficient', color: '#64748b' },
      ],
      controls: ['Terrain', 'Soil', 'Tilt', 'Vibration', 'AKASHA Link'],
    }}
  />
);
