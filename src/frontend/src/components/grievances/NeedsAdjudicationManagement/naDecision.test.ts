import { describe, expect, it } from 'vitest';
import { applyMark, clearMark } from './naDecision';
import { NaIndividual } from './naRoleUtils';

const withHeadRole = (id: string, householdId: string): NaIndividual => ({
  id,
  rolesInHouseholds: [
    {
      role: 'HEAD',
      household: {
        id: householdId,
        unicefId: `HH-${householdId}`,
        withdrawn: false,
        activeIndividualsCount: 3,
      },
    },
  ],
});

const person1: NaIndividual = { id: 'golden', fullName: 'Uno Ameno' };
const dup1: NaIndividual = { id: 'dup-1', fullName: 'Ana Ameno' };
const dup2: NaIndividual = { id: 'dup-2', fullName: 'Duo Ameno' };

describe('applyMark', () => {
  it('withdrawing the duplicate keeps the golden record distinct', () => {
    const decision = applyMark(
      undefined,
      { person1, person2: dup1, mark: 'person2_duplicate' },
      [dup1],
    );

    expect(decision.duplicateIndividualIds).toEqual(['dup-1']);
    expect(decision.distinctIndividualIds).toEqual(['golden']);
  });

  it('not-duplicates keeps both individuals out of the duplicate list', () => {
    const decision = applyMark(
      undefined,
      { person1, person2: dup1, mark: 'not_duplicates' },
      [dup1],
    );

    expect(decision.duplicateIndividualIds).toEqual([]);
    expect(decision.distinctIndividualIds).toEqual(['golden', 'dup-1']);
  });

  it('never lists the golden record as both duplicate and distinct', () => {
    // The operator withdraws the golden record against one candidate and calls
    // the pair distinct against another. The backend rejects an individual that
    // appears in both lists, so "duplicate" has to win.
    const first = applyMark(
      undefined,
      { person1, person2: dup1, mark: 'person1_duplicate' },
      [dup1, dup2],
    );
    const decision = applyMark(
      first,
      { person1, person2: dup2, mark: 'not_duplicates' },
      [dup1, dup2],
    );

    expect(decision.duplicateIndividualIds).toEqual(['golden']);
    expect(decision.distinctIndividualIds).toEqual(['dup-1', 'dup-2']);
  });

  it('marks are independent per candidate', () => {
    const first = applyMark(
      undefined,
      { person1, person2: dup1, mark: 'person2_duplicate' },
      [dup1, dup2],
    );
    const decision = applyMark(
      first,
      { person1, person2: dup2, mark: 'not_duplicates' },
      [dup1, dup2],
    );

    expect(decision.marks).toEqual({
      'dup-1': 'person2_duplicate',
      'dup-2': 'not_duplicates',
    });
    expect(decision.duplicateIndividualIds).toEqual(['dup-1']);
    expect(decision.distinctIndividualIds).toEqual(['golden', 'dup-2']);
  });

  it('keeps a replacement the operator already picked when another pair is marked', () => {
    // Re-deriving must not silently discard a reassignment; losing it would let
    // an unresolved decision look finalizable.
    const duplicate = withHeadRole('dup-1', 'hh-1');
    const marked = applyMark(
      undefined,
      { person1, person2: duplicate, mark: 'person2_duplicate' },
      [duplicate, dup2],
    );
    const withPick = {
      ...marked,
      reassignments: {
        'HEAD:hh-1': {
          ...marked.reassignments['HEAD:hh-1'],
          newIndividual: 'ind-9',
          newIndividualName: 'Replacement',
        },
      },
    };

    const decision = applyMark(
      withPick,
      { person1, person2: dup2, mark: 'not_duplicates' },
      [duplicate, dup2],
    );

    expect(decision.reassignments['HEAD:hh-1'].newIndividual).toBe('ind-9');
  });

  it('drops reassignments that are no longer required', () => {
    const duplicate = withHeadRole('dup-1', 'hh-1');
    const marked = applyMark(
      undefined,
      { person1, person2: duplicate, mark: 'person2_duplicate' },
      [duplicate],
    );
    expect(Object.keys(marked.reassignments)).toEqual(['HEAD:hh-1']);

    const decision = applyMark(
      marked,
      { person1, person2: duplicate, mark: 'not_duplicates' },
      [duplicate],
    );

    expect(decision.reassignments).toEqual({});
  });
});

describe('clearMark', () => {
  it('returns null once the last mark is removed so the ticket is unmanaged', () => {
    const decision = applyMark(
      undefined,
      { person1, person2: dup1, mark: 'person2_duplicate' },
      [dup1],
    );

    expect(clearMark(decision, person1, 'dup-1', [dup1])).toBeNull();
  });

  it('keeps the remaining marks and re-derives the id lists', () => {
    const first = applyMark(
      undefined,
      { person1, person2: dup1, mark: 'person2_duplicate' },
      [dup1, dup2],
    );
    const both = applyMark(
      first,
      { person1, person2: dup2, mark: 'person2_duplicate' },
      [dup1, dup2],
    );

    const decision = clearMark(both, person1, 'dup-1', [dup1, dup2]);

    expect(decision?.marks).toEqual({ 'dup-2': 'person2_duplicate' });
    expect(decision?.duplicateIndividualIds).toEqual(['dup-2']);
    expect(decision?.distinctIndividualIds).toEqual(['golden']);
  });
});
