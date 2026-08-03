// Session-local adjudication mark for a ticket in the NA management screen.
export type NaMark =
  | 'person1_duplicate'
  | 'person2_duplicate'
  | 'not_duplicates';

// Roles that leave a household broken if their holder is withdrawn without a
// replacement: the household would have no head / nobody to receive payments.
export type NaRequiredRole = 'HEAD' | 'PRIMARY';

export interface NaRoleAssignment {
  role: NaRequiredRole;
  // Household the role belongs to.
  household: string;
  householdUnicefId: string;
  // The duplicate who loses the role.
  individual: string;
  // The replacement. Undefined until the operator picks one.
  newIndividual?: string;
  newIndividualName?: string;
}

export interface NaTicketDecision {
  mark: NaMark;
  duplicateIndividualIds: string[];
  distinctIndividualIds: string[];
  // Keyed by `${role}:${householdId}` so a duplicate holding the same role in
  // two households keeps both entries.
  reassignments: Record<string, NaRoleAssignment>;
}
