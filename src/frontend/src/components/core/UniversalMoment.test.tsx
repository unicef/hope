import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { UniversalMoment } from './UniversalMoment';
import { TimezoneProvider } from 'src/timezoneContext';

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

  it('a date-only value is unchanged under a non-UTC provider and has no tooltip', () => {
    render(
      <TimezoneProvider timezone="America/New_York">
        <UniversalMoment>2024-04-11</UniversalMoment>
      </TimezoneProvider>,
    );
    expect(screen.getByText('11 Apr 2024')).toBeTruthy();
    expect(screen.queryByLabelText(/Apr 2024/)).toBeNull();
  });

  it('a timestamp without withTime converts its calendar day for the provider zone', () => {
    // 2024-04-11T00:30:00Z is 10 Apr 2024, 8:30 PM in America/New_York (EDT, UTC-4).
    render(
      <TimezoneProvider timezone="America/New_York">
        <UniversalMoment>2024-04-11T00:30:00Z</UniversalMoment>
      </TimezoneProvider>,
    );
    expect(screen.getByText('10 Apr 2024')).toBeTruthy();
  });

  it('withTime converts date and time for the provider zone', () => {
    render(
      <TimezoneProvider timezone="America/New_York">
        <UniversalMoment withTime>2024-04-11T14:30:00Z</UniversalMoment>
      </TimezoneProvider>,
    );
    expect(screen.getByText('11 Apr 2024 10:30 AM')).toBeTruthy();
  });

  it('the tooltip content includes the IANA timezone id', () => {
    const { container } = render(
      <TimezoneProvider timezone="Europe/Warsaw">
        <UniversalMoment withTime>2024-04-11T14:30:00Z</UniversalMoment>
      </TimezoneProvider>,
    );
    const timeEl = container.querySelector('time');
    const tooltipWrapper = timeEl?.closest('[aria-label]') ?? timeEl?.parentElement;
    // MUI Tooltip forwards aria-label to the wrapped child on hover-capable elements.
    expect(
      timeEl?.getAttribute('aria-label') ??
        tooltipWrapper?.getAttribute('aria-label'),
    ).toContain('Europe/Warsaw');
  });

  it('the dateTime attribute holds the normalized ISO instant for a timestamp', () => {
    const { container } = render(
      <UniversalMoment withTime>2024-04-11T14:30:00Z</UniversalMoment>,
    );
    const timeEl = container.querySelector('time');
    expect(timeEl?.getAttribute('dateTime')).toBe('2024-04-11T14:30:00.000Z');
  });

  it('the dateTime attribute holds the original date string for a date-only value', () => {
    const { container } = render(<UniversalMoment>2024-04-11</UniversalMoment>);
    const timeEl = container.querySelector('time');
    expect(timeEl?.getAttribute('dateTime')).toBe('2024-04-11');
  });

  it('the default context timezone is UTC', () => {
    render(<UniversalMoment withTime>2024-04-11T14:30:00Z</UniversalMoment>);
    expect(screen.getByText('11 Apr 2024 2:30 PM')).toBeTruthy();
  });
});
