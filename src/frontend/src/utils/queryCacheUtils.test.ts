import { describe, it, expect } from 'vitest';
import { isStaticReferenceQuery } from './queryCacheUtils';

describe('isStaticReferenceQuery', () => {
  // Reference data must stay exempt so the blanket post-mutation invalidation does not
  // needlessly refetch it and discard its long staleTime.
  it('returns true for known static reference roots', () => {
    expect(isStaticReferenceQuery(['profile', 'afghanistan', 'prog'])).toBe(true);
    expect(isStaticReferenceQuery(['businessArea', 'afghanistan'])).toBe(true);
    expect(isStaticReferenceQuery(['allAreasTree', 'afghanistan'])).toBe(true);
    expect(isStaticReferenceQuery(['beneficiaryGroups'])).toBe(true);
  });

  it('returns true for any choices endpoint key', () => {
    expect(isStaticReferenceQuery(['programChoices', 'afghanistan'])).toBe(true);
    expect(isStaticReferenceQuery(['householdChoices', 'afghanistan'])).toBe(true);
    expect(isStaticReferenceQuery(['choicesPaymentPlanStatusList'])).toBe(true);
    expect(
      isStaticReferenceQuery(['businessAreasGrievanceTicketsChoices', 'afg']),
    ).toBe(true);
    // Dropped from the STATIC_QUERY_KEY_ROOTS set but still matched by the choices heuristic.
    expect(isStaticReferenceQuery(['restChoicesCountriesList'])).toBe(true);
    // A derived (normalized) choices retrieve root is exempt too.
    expect(
      isStaticReferenceQuery([
        'businessAreasGrievanceTicketsChoicesRetrieve',
        { businessAreaSlug: 'afg' },
      ]),
    ).toBe(true);
  });

  // Mutable data MUST NOT be exempt — these are exactly the readers that go stale after a
  // create/edit/status-change and need to refetch.
  it('returns false for mutable data readers that must refetch after a write', () => {
    expect(isStaticReferenceQuery(['program', 'afghanistan', 'prog-1'])).toBe(false);
    expect(
      isStaticReferenceQuery(['businessAreasProgramsList', {}, 'afghanistan']),
    ).toBe(false);
    expect(
      isStaticReferenceQuery(['paymentPlan', 'afghanistan', 'pp-1', 'prog-1']),
    ).toBe(false);
    expect(
      isStaticReferenceQuery(['businessAreaProgram', 'afghanistan', 'prog-1']),
    ).toBe(false);
    // Derived (normalized) mutable-data roots must not be exempt.
    expect(
      isStaticReferenceQuery(['businessAreasProgramsList', { limit: 20 }]),
    ).toBe(false);
    expect(
      isStaticReferenceQuery([
        'businessAreasProgramsRetrieve',
        { businessAreaSlug: 'afg', code: 'p1' },
      ]),
    ).toBe(false);
  });

  // The exact-match guard must not treat `businessArea`-prefixed data keys as static.
  it('does not treat businessArea-prefixed data keys as static via prefix', () => {
    expect(
      isStaticReferenceQuery(['businessAreasProgramsTargetPopulationsList', {}]),
    ).toBe(false);
  });

  it('returns false when the first key element is not a string', () => {
    expect(isStaticReferenceQuery([{ limit: 100 }, 'afghanistan'])).toBe(false);
    expect(isStaticReferenceQuery([])).toBe(false);
  });
});
