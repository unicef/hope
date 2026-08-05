import { describe, expect, it } from 'vitest';
import { buildExecutePayload } from './naPayload';
import { NaTicketDecision } from './naTypes';

describe('buildExecutePayload', () => {
  it('sends the replacement so the server can hand over the role', () => {
    // `individual` is who loses the role (the duplicate) and `newIndividual`
    // is who takes it over; swapping them would withdraw the wrong person.
    const decisions: Record<string, NaTicketDecision> = {
      'ticket-1': {
        marks: { 'ind-2': 'person1_duplicate' },
        duplicateIndividualIds: ['ind-1'],
        distinctIndividualIds: ['ind-2'],
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
      },
    };

    expect(buildExecutePayload(decisions)).toEqual([
      {
        ticketId: 'ticket-1',
        duplicateIndividualIds: ['ind-1'],
        distinctIndividualIds: ['ind-2'],
        roleReassignData: {
          'HEAD-hh-1': {
            role: 'HEAD',
            household: 'hh-1',
            individual: 'ind-1',
            newIndividual: 'ind-3',
          },
        },
      },
    ]);
  });

  it('emits empty roleReassignData for a not-duplicates decision', () => {
    const decisions: Record<string, NaTicketDecision> = {
      'ticket-2': {
        marks: { 'ind-2': 'not_duplicates' },
        duplicateIndividualIds: [],
        distinctIndividualIds: ['ind-1', 'ind-2'],
        reassignments: {},
      },
    };

    expect(buildExecutePayload(decisions)[0]).toEqual({
      ticketId: 'ticket-2',
      duplicateIndividualIds: [],
      distinctIndividualIds: ['ind-1', 'ind-2'],
      roleReassignData: {},
    });
  });

  it('keys HEAD and PRIMARY separately for the same ticket', () => {
    const decisions: Record<string, NaTicketDecision> = {
      'ticket-3': {
        marks: { 'ind-2': 'person2_duplicate' },
        duplicateIndividualIds: ['ind-2'],
        distinctIndividualIds: ['ind-1'],
        reassignments: {
          'HEAD:hh-1': {
            role: 'HEAD',
            household: 'hh-1',
            householdUnicefId: 'HH-0001',
            individual: 'ind-2',
            newIndividual: 'ind-3',
          },
          'PRIMARY:hh-1': {
            role: 'PRIMARY',
            household: 'hh-1',
            householdUnicefId: 'HH-0001',
            individual: 'ind-2',
            newIndividual: 'ind-4',
          },
        },
      },
    };

    const roleReassignData = buildExecutePayload(decisions)[0].roleReassignData;

    expect(Object.keys(roleReassignData).sort()).toEqual([
      'HEAD-hh-1',
      'PRIMARY-hh-1',
    ]);
    expect(roleReassignData['PRIMARY-hh-1'].newIndividual).toBe('ind-4');
  });

  it('keeps both households when the duplicate holds the same role twice', () => {
    // Keying by role name alone would drop one of these and the server would
    // leave a household without a primary collector.
    const decisions: Record<string, NaTicketDecision> = {
      'ticket-5': {
        marks: { 'ind-2': 'person2_duplicate' },
        duplicateIndividualIds: ['ind-2'],
        distinctIndividualIds: ['ind-1'],
        reassignments: {
          'PRIMARY:hh-1': {
            role: 'PRIMARY',
            household: 'hh-1',
            householdUnicefId: 'HH-0001',
            individual: 'ind-2',
            newIndividual: 'ind-3',
          },
          'PRIMARY:hh-2': {
            role: 'PRIMARY',
            household: 'hh-2',
            householdUnicefId: 'HH-0002',
            individual: 'ind-2',
            newIndividual: 'ind-4',
          },
        },
      },
    };

    const roleReassignData = buildExecutePayload(decisions)[0].roleReassignData;

    expect(Object.keys(roleReassignData).sort()).toEqual([
      'PRIMARY-hh-1',
      'PRIMARY-hh-2',
    ]);
    expect(roleReassignData['PRIMARY-hh-1'].household).toBe('hh-1');
    expect(roleReassignData['PRIMARY-hh-2'].household).toBe('hh-2');
  });

  it('omits an unresolved role rather than sending a blank replacement', () => {
    // Execute is blocked in the UI for this state; if it ever gets through, a
    // missing key is safer than newIndividual: undefined.
    const decisions: Record<string, NaTicketDecision> = {
      'ticket-4': {
        marks: { 'ind-2': 'person1_duplicate' },
        duplicateIndividualIds: ['ind-1'],
        distinctIndividualIds: ['ind-2'],
        reassignments: {
          'HEAD:hh-1': {
            role: 'HEAD',
            household: 'hh-1',
            householdUnicefId: 'HH-0001',
            individual: 'ind-1',
          },
        },
      },
    };

    expect(buildExecutePayload(decisions)[0].roleReassignData).toEqual({});
  });
});
