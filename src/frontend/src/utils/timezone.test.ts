import { describe, it, expect, vi, afterEach } from 'vitest';
import {
  isDateOnly,
  parseInstant,
  formatInstant,
  formatTooltip,
} from './timezone';

describe('isDateOnly', () => {
  it('matches an exact YYYY-MM-DD string', () => {
    expect(isDateOnly('2024-04-11')).toBe(true);
  });

  it('rejects a full ISO timestamp', () => {
    expect(isDateOnly('2024-04-11T10:30:00Z')).toBe(false);
  });
});

describe('parseInstant', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('parses a Z-suffixed instant as-is', () => {
    const date = parseInstant('2024-04-11T10:30:00Z');
    expect(date?.toISOString()).toBe('2024-04-11T10:30:00.000Z');
  });

  it('preserves the instant for a +02:00 offset', () => {
    const date = parseInstant('2024-04-11T12:30:00+02:00');
    expect(date?.toISOString()).toBe('2024-04-11T10:30:00.000Z');
  });

  it('preserves the instant for a -05:00 offset', () => {
    const date = parseInstant('2024-04-11T05:30:00-05:00');
    expect(date?.toISOString()).toBe('2024-04-11T10:30:00.000Z');
  });

  it('treats an offset-less datetime as UTC and warns in dev', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const date = parseInstant('2024-04-11T10:30:00');
    expect(date?.toISOString()).toBe('2024-04-11T10:30:00.000Z');
    expect(warnSpy).toHaveBeenCalled();
  });

  it('returns null for an empty string', () => {
    expect(parseInstant('')).toBeNull();
  });

  it('returns null for an invalid string', () => {
    expect(parseInstant('not-a-date')).toBeNull();
  });
});

describe('formatInstant', () => {
  it('falls back to UTC for an unsupported timezone', () => {
    const date = new Date('2024-04-11T14:05:00Z');
    expect(formatInstant(date, 'Not/AZone', 'date')).toBe(
      formatInstant(date, 'UTC', 'date'),
    );
  });

  it('formats a date in "date" mode matching the app date format', () => {
    const date = new Date('2024-04-11T14:05:00Z');
    expect(formatInstant(date, 'UTC', 'date')).toBe('11 Apr 2024');
  });

  it('formats a date in "dateTime" mode matching the app long date format', () => {
    const date = new Date('2024-04-11T14:05:00Z');
    expect(formatInstant(date, 'UTC', 'dateTime')).toBe('11 Apr 2024 2:05 PM');
  });

  it('an instant crossing local midnight yields the previous calendar day', () => {
    // 2024-04-11T00:30:00Z is 10 Apr 2024, 8:30 PM in America/New_York (UTC-4 in April).
    const date = new Date('2024-04-11T00:30:00Z');
    expect(formatInstant(date, 'America/New_York', 'date')).toBe(
      '10 Apr 2024',
    );
  });

  it('handles DST spring-forward for a zone observing it', () => {
    // 2024-03-10 07:30 UTC is 2024-03-10 03:30 EDT (US spring-forward happened at 2am local).
    const date = new Date('2024-03-10T07:30:00Z');
    expect(formatInstant(date, 'America/New_York', 'dateTime')).toBe(
      '10 Mar 2024 3:30 AM',
    );
  });

  it('handles DST fall-back for a zone observing it', () => {
    // 2024-11-03 06:30 UTC is 2024-11-03 01:30 EST (after US fall-back).
    const date = new Date('2024-11-03T06:30:00Z');
    expect(formatInstant(date, 'America/New_York', 'dateTime')).toBe(
      '3 Nov 2024 1:30 AM',
    );
  });

  it('renders 3-letter month abbreviations matching date-fns MMM', () => {
    const expected = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    expected.forEach((abbr, month) => {
      const d = new Date(Date.UTC(2026, month, 15, 12, 0, 0));
      expect(formatInstant(d, 'UTC', 'date')).toBe(`15 ${abbr} 2026`);
    });
  });
});

describe('formatTooltip', () => {
  it('includes the full date, time, and IANA timezone id', () => {
    const date = new Date('2024-04-11T14:05:00Z');
    expect(formatTooltip(date, 'Europe/Warsaw')).toBe(
      '11 Apr 2024 4:05 PM (Europe/Warsaw)',
    );
  });
});
