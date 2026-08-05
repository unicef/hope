import { NaRequiredRole, NaRoleAssignment, NaTicketDecision } from './naTypes';

// Shape of `rolesInHouseholds` on individuals in the NA comparison payload,
// as sent by IndividualForNaComparisonSerializer.get_roles_in_households — the
// PRIMARY/ALTERNATE roles plus a synthetic HEAD entry, since
// IndividualRoleInHousehold does not model HEAD.
// `ticketDetails` is typed as Record<string, any> in restgenerated, so this
// describes the contract rather than deriving from a generated type.
export interface NaRoleInHousehold {
  role: string;
  household: {
    id: string;
    unicefId: string;
    withdrawn?: boolean;
    activeIndividualsCount?: number;
  };
}

export interface NaIndividual {
  id: string;
  fullName?: string;
  rolesInHouseholds?: NaRoleInHousehold[];
}

const REQUIRED_ROLES: NaRequiredRole[] = ['HEAD', 'PRIMARY'];

export const reassignmentKey = (role: string, householdId: string): string =>
  `${role}:${householdId}`;

export const roleLabel = (role: NaRequiredRole): string =>
  role === 'HEAD' ? 'Head of Household' : 'Primary Collector';

/**
 * Roles the operator must hand over before this individual can be withdrawn as
 * a duplicate. Mirrors the backend close-time validation in
 * `reassign_roles_on_marking_as_duplicate_individual_service`: a surviving
 * household may not be left without a head or a primary collector.
 */
export const getRequiredReassignments = (
  duplicate: NaIndividual | null | undefined,
): NaRoleAssignment[] => {
  if (!duplicate?.rolesInHouseholds) return [];

  return (
    duplicate.rolesInHouseholds
      .filter((entry): entry is NaRoleInHousehold & { role: NaRequiredRole } =>
        REQUIRED_ROLES.includes(entry?.role as NaRequiredRole),
      )
      .filter((entry) => Boolean(entry.household?.id))
      // A withdrawn household has nothing left to reassign.
      .filter((entry) => !entry.household.withdrawn)
      // Sole member: withdrawing them withdraws the household automatically.
      .filter((entry) => (entry.household.activeIndividualsCount ?? 0) > 1)
      .map((entry) => ({
        role: entry.role,
        household: entry.household.id,
        householdUnicefId: entry.household.unicefId,
        individual: duplicate.id,
      }))
  );
};

export const keyReassignments = (
  assignments: NaRoleAssignment[],
): Record<string, NaRoleAssignment> =>
  assignments.reduce<Record<string, NaRoleAssignment>>((acc, assignment) => {
    acc[reassignmentKey(assignment.role, assignment.household)] = assignment;
    return acc;
  }, {});

/** A decision can only be executed once every required role has a replacement. */
export const isDecisionResolved = (decision: NaTicketDecision): boolean =>
  Object.values(decision.reassignments).every(
    (assignment) => !!assignment.newIndividual,
  );
