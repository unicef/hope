import { describe, expect, it } from 'vitest';
import { buildExecutePayload } from './naPayload';
import { NaTicketDecision } from './naTypes';

describe('buildExecutePayload', () => {
  it('sends the replacement so the server can hand over the role', () => {
    // `individual` is who loses the role (the duplicate) and `new_individual`
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
        ticket_id: 'ticket-1',
        duplicate_individual_ids: ['ind-1'],
        distinct_individual_ids: ['ind-2'],
        role_reassign_data: {
          HEAD: {
            role: 'HEAD',
            household: 'hh-1',
            individual: 'ind-1',
            new_individual: 'ind-3',
          },
        },
      },
    ]);
  });

  it('emits empty role_reassign_data for a not-duplicates decision', () => {
    const decisions: Record<string, NaTicketDecision> = {
      'ticket-2': {
        marks: { 'ind-2': 'not_duplicates' },
        duplicateIndividualIds: [],
        distinctIndividualIds: ['ind-1', 'ind-2'],
        reassignments: {},
      },
    };

    expect(buildExecutePayload(decisions)[0]).toEqual({
      ticket_id: 'ticket-2',
      duplicate_individual_ids: [],
      distinct_individual_ids: ['ind-1', 'ind-2'],
      role_reassign_data: {},
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

    const roleReassignData =
      buildExecutePayload(decisions)[0].role_reassign_data;

    expect(Object.keys(roleReassignData).sort()).toEqual(['HEAD', 'PRIMARY']);
    expect(roleReassignData.PRIMARY.new_individual).toBe('ind-4');
  });

  it('omits an unresolved role rather than sending a blank replacement', () => {
    // Execute is blocked in the UI for this state; if it ever gets through, a
    // missing key is safer than new_individual: undefined.
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

    expect(buildExecutePayload(decisions)[0].role_reassign_data).toEqual({});
  });
});
