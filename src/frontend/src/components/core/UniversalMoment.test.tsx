import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { UniversalMoment } from './UniversalMoment';

describe('UniversalMoment', () => {
  it('renders date-only string without timezone shift', () => {
    render(<UniversalMoment>2024-04-11</UniversalMoment>);
    expect(screen.getByText('11 Apr 2024')).toBeTruthy();
  });

  it('renders UTC-midnight ISO timestamp as the ISO calendar date, not shifted to local', () => {
    // "2024-04-11T00:00:00Z" is UTC midnight April 11.
    // In UTC-5 this would previously show "10 Apr 2024". It must show "11 Apr 2024".
    render(<UniversalMoment>2024-04-11T00:00:00Z</UniversalMoment>);
    expect(screen.getByText('11 Apr 2024')).toBeTruthy();
  });

  it('renders UTC-midnight ISO timestamp with milliseconds as the ISO calendar date', () => {
    render(<UniversalMoment>2024-04-11T00:00:00.000Z</UniversalMoment>);
    expect(screen.getByText('11 Apr 2024')).toBeTruthy();
  });

  it('renders null/empty children as a dash', () => {
    render(<UniversalMoment>{null as unknown as string}</UniversalMoment>);
    expect(screen.getByText('-')).toBeTruthy();
  });

  it('withTime renders a time element without throwing', () => {
    const { container } = render(
      <UniversalMoment withTime>2024-04-11T10:30:00Z</UniversalMoment>,
    );
    const timeEl = container.querySelector('time');
    expect(timeEl).toBeTruthy();
    expect(timeEl?.textContent).toContain('Apr 2024');
  });
});
