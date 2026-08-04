import { describe, expect, it } from 'vitest';
import { splitFullName } from './naName';

describe('splitFullName', () => {
  // The comparison panel shows Last Name and First Name as separate rows so
  // that two people sharing a family name only highlight the first name.
  it('treats the last token as the family name', () => {
    expect(splitFullName('Uno Ameno')).toEqual({
      givenName: 'Uno',
      familyName: 'Ameno',
    });
    expect(splitFullName('Ana Ameno')).toEqual({
      givenName: 'Ana',
      familyName: 'Ameno',
    });
  });

  it('keeps middle names with the given name', () => {
    expect(splitFullName('Ana Maria Ameno')).toEqual({
      givenName: 'Ana Maria',
      familyName: 'Ameno',
    });
  });

  it('treats a single token as a family name', () => {
    expect(splitFullName('Ameno')).toEqual({
      givenName: '',
      familyName: 'Ameno',
    });
  });

  it('tolerates missing and padded values', () => {
    expect(splitFullName(null)).toEqual({ givenName: '', familyName: '' });
    expect(splitFullName('   ')).toEqual({ givenName: '', familyName: '' });
    expect(splitFullName('  Uno   Ameno  ')).toEqual({
      givenName: 'Uno',
      familyName: 'Ameno',
    });
  });
});
