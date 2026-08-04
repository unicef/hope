import { describe, expect, it } from 'vitest';
import {
  getRequiredReassignments,
  isDecisionResolved,
  keyReassignments,
} from './naRoleUtils';
import { NaTicketDecision } from './naTypes';

const household = (overrides = {}) => ({
  id: 'hh-1',
  unicefId: 'HH-0001',
  withdrawn: false,
  activeIndividualsCount: 3,
  ...overrides,
});

const duplicate = (roles) => ({
  id: 'ind-1',
  fullName: 'Jan Kowalski',
  rolesInHouseholds: roles,
});

describe('getRequiredReassignments', () => {
  it('requires reassignment when the duplicate heads a surviving household', () => {
    // Without a new head the household is left headless — the backend rejects
    // the close, so the operator must be asked before executing.
    const result = getRequiredReassignments(
      duplicate([{ role: 'HEAD', household: household() }]),
    );

    expect(result).toEqual([
      {
        role: 'HEAD',
        household: 'hh-1',
        householdUnicefId: 'HH-0001',
        individual: 'ind-1',
      },
    ]);
  });

  it('requires reassignment for the primary collector', () => {
    // A household without a primary collector has nobody to receive payments.
    const result = getRequiredReassignments(
      duplicate([{ role: 'PRIMARY', household: household() }]),
    );

    expect(result).toHaveLength(1);
    expect(result[0].role).toBe('PRIMARY');
  });

  it('does not require reassignment for the alternate collector', () => {
    // Losing the alternate leaves the household payable, so it must not block.
    expect(
      getRequiredReassignments(
        duplicate([{ role: 'ALTERNATE', household: household() }]),
      ),
    ).toEqual([]);
  });

  it('skips a household where the duplicate is the sole member', () => {
    // The household is withdrawn along with its only member — there is nobody
    // to reassign to and nothing left needing a head.
    expect(
      getRequiredReassignments(
        duplicate([
          { role: 'HEAD', household: household({ activeIndividualsCount: 1 }) },
        ]),
      ),
    ).toEqual([]);
  });

  it('skips an already withdrawn household', () => {
    expect(
      getRequiredReassignments(
        duplicate([
          { role: 'HEAD', household: household({ withdrawn: true }) },
        ]),
      ),
    ).toEqual([]);
  });

  it('returns nothing when the payload carries no roles', () => {
    expect(getRequiredReassignments({ id: 'ind-1' })).toEqual([]);
    expect(getRequiredReassignments(null)).toEqual([]);
  });

  it('keeps one entry per household when a role is held twice', () => {
    const result = keyReassignments(
      getRequiredReassignments(
        duplicate([
          { role: 'PRIMARY', household: household() },
          {
            role: 'PRIMARY',
            household: household({ id: 'hh-2', unicefId: 'HH-0002' }),
          },
        ]),
      ),
    );

    expect(Object.keys(result)).toEqual(['PRIMARY:hh-1', 'PRIMARY:hh-2']);
  });
});

describe('isDecisionResolved', () => {
  const base: NaTicketDecision = {
    marks: { 'ind-2': 'person1_duplicate' },
    duplicateIndividualIds: ['ind-1'],
    distinctIndividualIds: ['ind-2'],
    reassignments: {},
  };

  it('blocks while a required role has no replacement', () => {
    expect(
      isDecisionResolved({
        ...base,
        reassignments: {
          'HEAD:hh-1': {
            role: 'HEAD',
            household: 'hh-1',
            householdUnicefId: 'HH-0001',
            individual: 'ind-1',
          },
        },
      }),
    ).toBe(false);
  });

  it('passes once every required role has a replacement', () => {
    expect(
      isDecisionResolved({
        ...base,
        reassignments: {
          'HEAD:hh-1': {
            role: 'HEAD',
            household: 'hh-1',
            householdUnicefId: 'HH-0001',
            individual: 'ind-1',
            newIndividual: 'ind-3',
            newIndividualName: 'Anna Nowak',
          },
        },
      }),
    ).toBe(true);
  });

  it('passes for a not-duplicates decision, which never reassigns', () => {
    expect(
      isDecisionResolved({
        marks: { 'ind-2': 'not_duplicates' },
        duplicateIndividualIds: [],
        distinctIndividualIds: ['ind-1', 'ind-2'],
        reassignments: {},
      }),
    ).toBe(true);
  });
});
