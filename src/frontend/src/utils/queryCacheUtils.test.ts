import { describe, it, expect } from 'vitest';
import { isStaticReferenceQuery } from './queryCacheUtils';

describe('isStaticReferenceQuery', () => {
  // Exempt so the blanket post-mutation invalidation does not discard their long staleTime.
  it('returns true for known static reference roots', () => {
    expect(
      isStaticReferenceQuery([
        'businessAreasUsersProfileRetrieve',
        { businessAreaSlug: 'afghanistan', programCode: 'prog' },
      ]),
    ).toBe(true);
    expect(
      isStaticReferenceQuery([
        'businessAreasRetrieve',
        { businessAreaSlug: 'afghanistan' },
      ]),
    ).toBe(true);
    expect(
      isStaticReferenceQuery([
        'businessAreasGeoAreasList',
        { businessAreaSlug: 'afghanistan', level: 2 },
      ]),
    ).toBe(true);
    expect(isStaticReferenceQuery(['beneficiaryGroupsList'])).toBe(true);
  });

  it('returns false for the retired hand-written roots', () => {
    expect(isStaticReferenceQuery(['profile', 'afghanistan'])).toBe(false);
    expect(isStaticReferenceQuery(['businessArea', 'afghanistan'])).toBe(false);
    expect(isStaticReferenceQuery(['allAreasTree', 'afghanistan'])).toBe(false);
    expect(isStaticReferenceQuery(['beneficiaryGroups'])).toBe(false);
  });

  it('returns true for any choices endpoint key', () => {
    expect(isStaticReferenceQuery(['programChoices', 'afghanistan'])).toBe(
      true,
    );
    expect(isStaticReferenceQuery(['householdChoices', 'afghanistan'])).toBe(
      true,
    );
    expect(isStaticReferenceQuery(['choicesPaymentPlanStatusList'])).toBe(true);
    expect(
      isStaticReferenceQuery([
        'businessAreasDataCollectingTypesChoicesList',
        'afg',
      ]),
    ).toBe(true);
    // Matched by the heuristic, not the explicit set.
    expect(isStaticReferenceQuery(['restChoicesCountriesList'])).toBe(true);
    expect(isStaticReferenceQuery(['choicesGrievanceTicketsRetrieve'])).toBe(
      true,
    );
  });

  it('returns false for mutable data readers that must refetch after a write', () => {
    expect(isStaticReferenceQuery(['program', 'afghanistan', 'prog-1'])).toBe(
      false,
    );
    expect(
      isStaticReferenceQuery(['businessAreasProgramsList', {}, 'afghanistan']),
    ).toBe(false);
    expect(
      isStaticReferenceQuery(['paymentPlan', 'afghanistan', 'pp-1', 'prog-1']),
    ).toBe(false);
    expect(
      isStaticReferenceQuery(['businessAreaProgram', 'afghanistan', 'prog-1']),
    ).toBe(false);
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

  it('does not treat businessArea-prefixed data keys as static via prefix', () => {
    expect(
      isStaticReferenceQuery([
        'businessAreasProgramsTargetPopulationsList',
        {},
      ]),
    ).toBe(false);
  });

  it('returns false when the first key element is not a string', () => {
    expect(isStaticReferenceQuery([{ limit: 100 }, 'afghanistan'])).toBe(false);
    expect(isStaticReferenceQuery([])).toBe(false);
  });
});
