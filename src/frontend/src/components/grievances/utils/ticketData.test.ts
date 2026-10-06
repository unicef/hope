import { describe, expect, it } from 'vitest';
import {
  countTicketChanges,
  getTicketFieldChange,
  getTicketFlexFields,
  isApprovedTicketFieldChange,
  normalizeTicketFieldChange,
} from './ticketData';

// household_data is in deepCamelize's notCamelizedKeys, so it keeps its
// snake_case keys; individual_data is camelized apart from flex field names.
const householdTicketDetails = {
  householdData: {
    size: { value: 5, previous_value: 4, approve_status: true },
    consent_sign: {
      value: '/new.jpg',
      previous_value: '/old.jpg',
      approve_status: false,
    },
    roles: [
      { individual_id: 'ind-1', value: 'PRIMARY', approve_status: false },
    ],
    flex_fields: {
      hh_total_eligible_ind_h_f: {
        value: 2,
        previous_value: 1,
        approve_status: false,
      },
    },
  },
};

const individualTicketDetails = {
  individualData: {
    givenName: { value: 'Jan', previousValue: 'Janek', approveStatus: true },
    consentSign: {
      value: '/new.jpg',
      previousValue: '/old.jpg',
      approveStatus: false,
    },
    flexFields: {
      photo_i_f: {
        value: '/flex-new.jpg',
        previousValue: '/flex-old.jpg',
        approveStatus: false,
      },
    },
  },
};

describe('getTicketFlexFields', () => {
  it('reads flex_fields on the household side', () => {
    expect(
      Object.keys(getTicketFlexFields(householdTicketDetails)),
    ).toStrictEqual(['hh_total_eligible_ind_h_f']);
  });

  it('reads flexFields on the individual side', () => {
    expect(
      Object.keys(getTicketFlexFields(individualTicketDetails, true)),
    ).toStrictEqual(['photo_i_f']);
  });

  it('returns an empty object for a ticket without flex fields', () => {
    expect(getTicketFlexFields(undefined)).toStrictEqual({});
  });
});

describe('getTicketFieldChange', () => {
  it.each([
    ['household core field', householdTicketDetails, 'size', false, 5],
    [
      'household flex field',
      householdTicketDetails,
      'hh_total_eligible_ind_h_f',
      false,
      2,
    ],
    [
      'individual core field under its camelized name',
      individualTicketDetails,
      'consent_sign',
      true,
      '/new.jpg',
    ],
    [
      'individual flex field under its original name',
      individualTicketDetails,
      'photo_i_f',
      true,
      '/flex-new.jpg',
    ],
  ])(
    'finds the %s',
    (_label, ticketDetails, fieldName, isIndividual, value) => {
      expect(
        getTicketFieldChange(ticketDetails, fieldName, isIndividual)?.value,
      ).toBe(value);
    },
  );

  it('returns nothing for a field the ticket does not change', () => {
    expect(
      getTicketFieldChange(householdTicketDetails, 'missing_h_f'),
    ).toBeUndefined();
  });
});

describe('normalizeTicketFieldChange', () => {
  it('reads both spellings of the same change', () => {
    expect(
      normalizeTicketFieldChange(householdTicketDetails.householdData.size),
    ).toStrictEqual({ value: 5, previousValue: 4, approveStatus: true });
    expect(
      normalizeTicketFieldChange(
        individualTicketDetails.individualData.givenName,
        true,
      ),
    ).toStrictEqual({
      value: 'Jan',
      previousValue: 'Janek',
      approveStatus: true,
    });
  });
});

describe('isApprovedTicketFieldChange', () => {
  it.each([
    [{ approve_status: true }, true],
    [{ approveStatus: true }, true],
    [{ approve_status: false }, false],
    [{ approveStatus: false }, false],
    [{ value: 'no status at all' }, false],
    [null, false],
    ['a plain value', false],
  ])('reads %s as %s', (value, expected) => {
    expect(isApprovedTicketFieldChange(value)).toBe(expected);
  });
});

describe('countTicketChanges', () => {
  it('counts household core fields, flex fields and roles', () => {
    expect(countTicketChanges(householdTicketDetails)).toStrictEqual({
      approved: 1,
      notApproved: 3,
    });
  });

  it('counts individual changes, which are camelized', () => {
    expect(countTicketChanges(individualTicketDetails)).toStrictEqual({
      approved: 1,
      notApproved: 2,
    });
  });

  it('counts nothing for a ticket without requested changes', () => {
    expect(countTicketChanges(undefined)).toStrictEqual({
      approved: 0,
      notApproved: 0,
    });
  });
});
