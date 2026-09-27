import React from 'react';
import { NativeHazardMapBase, type DomainLayer, type NativeHazardMapFeature } from './NativeHazardMapBase';

export const AkashaWeatherMap: React.FC<{ feature: NativeHazardMapFeature; layers: DomainLayer[] }> = (props) => (
  <NativeHazardMapBase
    {...props}
    config={{
      domain: 'AKASHA', testId: 'akasha-weather-map', modeClass: 'akasha', mapLabel: 'आकाश (AKASHA) · Atmospheric & Weather Intelligence',
      accent: '#60a5fa', markerText: 'आ', zoom: 8,
      legend: [
        { label: 'Rain / weather evidence', color: '#60a5fa' },
        { label: 'Wind', color: '#22d3ee' },
        { label: 'Cross-hazard link', color: '#a78bfa' },
        { label: 'Critical', color: '#ef4444' },
      ],
      controls: ['Precipitation', 'Wind', 'Pressure', 'Humidity', 'Cross-Hazard'],
    }}
  />
);
