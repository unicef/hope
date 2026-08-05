import { NeedsAdjudicationResolution } from '@restgenerated/models/NeedsAdjudicationResolution';
import { NeedsAdjudicationRoleReassignEntry } from '@restgenerated/models/NeedsAdjudicationRoleReassignEntry';
import { NaTicketDecision } from './naTypes';

/**
 * Key for one `roleReassignData` entry. The backend ignores these keys —
 * `_proccesing_role_reassign_data` iterates `role_reassign_data.values()` — so
 * they only need to stay unique within a ticket, hence the household id: a
 * duplicate can hold PRIMARY in more than one household.
 *
 * The body is sent as multipart (`processFormData` in restgenerated/core) and
 * reassembled by DictDrfNestedParser, so the key must avoid the `.` and `[`
 * characters that parser uses for nesting.
 */
const payloadReassignKey = (role: string, householdId: string): string =>
  `${role}-${householdId}`;

/** Flattens session decisions into the bulk needs-adjudication request body. */
export const buildExecutePayload = (
  decisions: Record<string, NaTicketDecision>,
): NeedsAdjudicationResolution[] =>
  Object.entries(decisions).map(([ticketId, decision]) => ({
    ticketId,
    duplicateIndividualIds: decision.duplicateIndividualIds,
    distinctIndividualIds: decision.distinctIndividualIds,
    roleReassignData: Object.values(decision.reassignments).reduce<
      Record<string, NeedsAdjudicationRoleReassignEntry>
    >((acc, assignment) => {
      if (!assignment.newIndividual) return acc;
      acc[payloadReassignKey(assignment.role, assignment.household)] = {
        role: assignment.role,
        household: assignment.household,
        individual: assignment.individual,
        newIndividual: assignment.newIndividual,
      };
      return acc;
    }, {}),
  }));
