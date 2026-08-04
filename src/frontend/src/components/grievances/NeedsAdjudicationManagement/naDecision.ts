import {
  getRequiredReassignments,
  NaIndividual,
  reassignmentKey,
} from './naRoleUtils';
import { NaMark, NaRoleAssignment, NaTicketDecision } from './naTypes';

/**
 * A needs-adjudication ticket compares one golden record (person 1) against one
 * or more possible duplicates (person 2). Each pair is marked independently, so
 * the executable id lists have to be derived from all marks at once:
 *
 *  - person 1 is a duplicate as soon as ANY pair is marked `person1_duplicate`;
 *  - a possible duplicate is a duplicate only if ITS OWN pair says so;
 *  - everyone else carrying a mark is distinct.
 *
 * Duplicate wins over distinct: marking person 1 as the duplicate in one pair
 * and distinct in another is a legitimate operator sequence, but the backend
 * cannot receive the same individual in both lists.
 */

interface ApplyMarkArgs {
  person1: NaIndividual | null | undefined;
  person2: NaIndividual | null | undefined;
  mark: NaMark;
}

const EMPTY_DECISION: NaTicketDecision = {
  marks: {},
  duplicateIndividualIds: [],
  distinctIndividualIds: [],
  reassignments: {},
};

/**
 * Rebuilds the id lists and the required reassignments from `marks`.
 * Replacements the operator already picked are carried over for every
 * reassignment that is still required; keys that no longer apply are dropped.
 */
const derive = (
  marks: Record<string, NaMark>,
  person1: NaIndividual | null | undefined,
  duplicatesById: Record<string, NaIndividual>,
  previousReassignments: Record<string, NaRoleAssignment>,
): NaTicketDecision => {
  const markValues = Object.values(marks);
  const person1IsDuplicate = markValues.includes('person1_duplicate');

  const duplicateIndividuals: NaIndividual[] = [];
  if (person1IsDuplicate && person1) duplicateIndividuals.push(person1);
  Object.entries(marks).forEach(([duplicateId, mark]) => {
    if (mark === 'person2_duplicate' && duplicatesById[duplicateId]) {
      duplicateIndividuals.push(duplicatesById[duplicateId]);
    }
  });

  const duplicateIds = duplicateIndividuals.map((individual) => individual.id);
  const duplicateIdSet = new Set(duplicateIds);

  const involvedIds = [
    ...(person1?.id && markValues.length > 0 ? [person1.id] : []),
    ...Object.keys(marks),
  ];
  const distinctIds = Array.from(new Set(involvedIds)).filter(
    (id) => !duplicateIdSet.has(id),
  );

  const reassignments = duplicateIndividuals
    .flatMap((individual) => getRequiredReassignments(individual))
    .reduce<Record<string, NaRoleAssignment>>((acc, assignment) => {
      const key = reassignmentKey(assignment.role, assignment.household);
      const previous = previousReassignments[key];
      acc[key] =
        previous?.individual === assignment.individual
          ? { ...assignment, ...previous }
          : assignment;
      return acc;
    }, {});

  return {
    marks,
    duplicateIndividualIds: duplicateIds,
    distinctIndividualIds: distinctIds,
    reassignments,
  };
};

/** Records the operator's mark for one golden-record/duplicate pair. */
export const applyMark = (
  decision: NaTicketDecision | undefined,
  { person1, person2, mark }: ApplyMarkArgs,
  allDuplicates: NaIndividual[],
): NaTicketDecision => {
  if (!person2?.id) return decision ?? EMPTY_DECISION;

  const marks = { ...(decision?.marks ?? {}), [person2.id]: mark };
  const duplicatesById = allDuplicates.reduce<Record<string, NaIndividual>>(
    (acc, individual) => {
      if (individual?.id) acc[individual.id] = individual;
      return acc;
    },
    {},
  );

  return derive(marks, person1, duplicatesById, decision?.reassignments ?? {});
};

/**
 * Drops the mark for one pair. Returns null when nothing is marked any more, so
 * the caller can remove the ticket from the session decisions entirely.
 */
export const clearMark = (
  decision: NaTicketDecision | undefined,
  person1: NaIndividual | null | undefined,
  person2Id: string | undefined,
  allDuplicates: NaIndividual[],
): NaTicketDecision | null => {
  if (!decision || !person2Id) return decision ?? null;

  const marks = { ...decision.marks };
  delete marks[person2Id];
  if (Object.keys(marks).length === 0) return null;

  const duplicatesById = allDuplicates.reduce<Record<string, NaIndividual>>(
    (acc, individual) => {
      if (individual?.id) acc[individual.id] = individual;
      return acc;
    },
    {},
  );

  return derive(marks, person1, duplicatesById, decision.reassignments);
};
