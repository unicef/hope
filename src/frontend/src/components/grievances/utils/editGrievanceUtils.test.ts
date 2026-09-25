import type { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { describe, expect, it } from 'vitest';
import { prepareInitialValues } from './editGrievanceUtils';

// householdData keeps its snake_case keys, see utils/ticketData
const makeHouseholdTicket = (
  householdData: Record<string, unknown>,
): GrievanceTicketDetail =>
  ({
    category: GRIEVANCE_CATEGORIES.DATA_CHANGE,
    issueType: GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD,
    programs: [],
    linkedTickets: [],
    household: { id: 'hh-1' },
    ticketDetails: { householdData },
  }) as unknown as GrievanceTicketDetail;

describe('prepareInitialValues for a household data change ticket', () => {
  it('offers core fields and flex fields for editing', () => {
    const ticket = makeHouseholdTicket({
      size: { value: 5, previous_value: 4, approve_status: false },
      flex_fields: {
        hh_total_eligible_ind_h_f: {
          value: 2,
          previous_value: 1,
          approve_status: false,
        },
      },
    });

    expect(
      prepareInitialValues(ticket).householdDataUpdateFields,
    ).toStrictEqual([
      { fieldName: 'size', fieldValue: 5 },
      { fieldName: 'hh_total_eligible_ind_h_f', fieldValue: 2 },
    ]);
  });

  it('leaves out flex_fields and roles, which are not single fields', () => {
    const ticket = makeHouseholdTicket({
      size: { value: 5, previous_value: 4, approve_status: false },
      roles: [
        { individual_id: 'ind-1', value: 'PRIMARY', approve_status: false },
      ],
      flex_fields: {},
    });

    expect(
      prepareInitialValues(ticket).householdDataUpdateFields,
    ).toStrictEqual([{ fieldName: 'size', fieldValue: 5 }]);
  });

  it('offers nothing for a ticket without household data', () => {
    const ticket = makeHouseholdTicket(undefined);

    expect(
      prepareInitialValues(ticket).householdDataUpdateFields,
    ).toStrictEqual([]);
  });
});
