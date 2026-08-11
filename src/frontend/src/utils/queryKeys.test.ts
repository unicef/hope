import { describe, it, expect } from 'vitest';
import { restQueryKey } from './queryKeys';

// Stand-ins for RestService methods — only `.name` matters.
function restBusinessAreasProgramsList(): void {}
function restBusinessAreasProgramsRetrieve(): void {}
function hhStatusRetrieve(): void {}

describe('restQueryKey', () => {
  it('normalizes the method name (drops `rest`, lower-cases first char)', () => {
    expect(restQueryKey(restBusinessAreasProgramsList)).toEqual([
      'businessAreasProgramsList',
    ]);
  });

  it('leaves a non-`rest`-prefixed method name untouched', () => {
    expect(restQueryKey(hhStatusRetrieve)).toEqual(['hhStatusRetrieve']);
  });

  it('returns [root] when no params are given (list prefix / invalidation)', () => {
    expect(restQueryKey(restBusinessAreasProgramsRetrieve)).toEqual([
      'businessAreasProgramsRetrieve',
    ]);
  });

  it('returns [root, params] and passes params through by identity', () => {
    const params = { businessAreaSlug: 'afghanistan', limit: 20 };
    const key = restQueryKey(restBusinessAreasProgramsRetrieve, params);
    expect(key).toEqual(['businessAreasProgramsRetrieve', params]);
    // Embedded by identity, not cloned — cache identity relies on this.
    expect(key[1]).toBe(params);
  });

  it('derives distinct roots from distinct methods', () => {
    expect(restQueryKey(restBusinessAreasProgramsList)[0]).not.toBe(
      restQueryKey(restBusinessAreasProgramsRetrieve)[0],
    );
  });
});
