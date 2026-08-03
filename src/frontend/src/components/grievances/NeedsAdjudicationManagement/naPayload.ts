import { NaTicketDecision } from './naTypes';

export interface NaRoleReassignEntry {
  role: string;
  household: string;
  individual: string;
  new_individual: string;
}

export interface NaExecuteTicketPayload {
  ticket_id: string;
  duplicate_individual_ids: string[];
  distinct_individual_ids: string[];
  role_reassign_data: Record<string, NaRoleReassignEntry>;
}

/**
 * Flattens session decisions into the bulk execute payload. `role_reassign_data`
 * is keyed by role name and uses snake_case inner fields, matching the shape the
 * backend's reassign service consumes. Hand-typed on purpose — this endpoint is
 * not in restgenerated yet.
 *
 * TODO: confirm the key format with BE. The existing /reassign-role/ action
 * keys collector roles by IndividualRoleInHousehold id rather than by role name;
 * reassign_roles_on_marking_as_duplicate_individual_service iterates values and
 * ignores keys, so role names are safe today, but that is not contractual.
 * TODO: role-name keys collide if one duplicate holds PRIMARY in two households.
 * Session state keys by `role:householdId` and keeps both, so only the
 * serialization loses one — revisit if BE keys by role id instead.
 */
export const buildExecutePayload = (
  decisions: Record<string, NaTicketDecision>,
): NaExecuteTicketPayload[] =>
  Object.entries(decisions).map(([ticketId, decision]) => ({
    ticket_id: ticketId,
    duplicate_individual_ids: decision.duplicateIndividualIds,
    distinct_individual_ids: decision.distinctIndividualIds,
    role_reassign_data: Object.values(decision.reassignments).reduce<
      Record<string, NaRoleReassignEntry>
    >((acc, assignment) => {
      if (!assignment.newIndividual) return acc;
      acc[assignment.role] = {
        role: assignment.role,
        household: assignment.household,
        individual: assignment.individual,
        new_individual: assignment.newIndividual,
      };
      return acc;
    }, {}),
  }));
