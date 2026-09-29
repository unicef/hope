import { describe, expect, it } from 'vitest';
import { formatCurrencyCode, formatCurrencyWithSymbol } from './utils';

describe('formatCurrencyCode', () => {
  it('returns null without a currency', () => {
    expect(formatCurrencyCode(null, 'SYP01')).toBeNull();
  });

  it('shows the bare code when there is no distinct vision code', () => {
    expect(formatCurrencyCode('SYP')).toBe('SYP');
    expect(formatCurrencyCode('SYP', 'SYP')).toBe('SYP');
  });

  it('appends the vision code of a redenominated currency', () => {
    expect(formatCurrencyCode('SYP', 'SYP01')).toBe('SYP (SYP01)');
  });
});

describe('formatCurrencyWithSymbol', () => {
  it('labels two denominations sharing one ISO code differently', () => {
    const deprecated = formatCurrencyWithSymbol(100, 'SYP', 'SYP');

    expect(formatCurrencyWithSymbol(100, 'SYP', 'SYP01')).toBe(
      `${deprecated} (SYP01)`,
    );
  });

  it('appends the vision code to a non-ISO currency as well', () => {
    expect(formatCurrencyWithSymbol(100, 'USDC', 'USDC01')).toMatch(
      / USDC \(USDC01\)$/,
    );
  });
});
