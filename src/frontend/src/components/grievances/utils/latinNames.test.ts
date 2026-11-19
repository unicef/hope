import { describe, expect, it } from 'vitest';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GrievanceSteps,
} from '@utils/constants';
import { validate, validateUsingSteps } from './validateGrievance';

const beneficiaryGroup = { memberLabel: 'Individual', groupLabel: 'Household' };

const editIndividualBase = {
  category: GRIEVANCE_CATEGORIES.DATA_CHANGE,
  issueType: GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL,
  selectedIndividual: { id: 'ind-1' },
  selectedLinkedTickets: [],
};

const addIndividualBase = {
  category: GRIEVANCE_CATEGORIES.DATA_CHANGE,
  issueType: GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL,
  selectedHousehold: { id: 'hh-1' },
  selectedLinkedTickets: [],
};

const FORMAT_ERROR =
  'Only ASCII letters, spaces, hyphens and apostrophes are allowed';

describe('validate - latin name format', () => {
  const runEditValidation = (values) =>
    validate(
      { ...editIndividualBase, ...values },
      null,
      {},
      {},
      beneficiaryGroup,
    );

  it('rejects latin values the backend regex would reject', () => {
    const errors = runEditValidation({
      individualDataUpdateFields: [
        { fieldName: 'full_name_latin', fieldValue: 'Иван 123' },
      ],
    });

    expect(errors.individualDataUpdateFields).toBe(FORMAT_ERROR);
  });

  it('accepts ASCII latin values and does not require them', () => {
    const errors = runEditValidation({
      individualDataUpdateFields: [
        { fieldName: 'full_name', fieldValue: 'Иван Иванов' },
        { fieldName: 'given_name_latin', fieldValue: "O'Neil-Smith " },
      ],
    });

    expect(errors.individualDataUpdateFields).toBeUndefined();
  });

  it.each([
    ' Anna',
    'Anna ',
    'Anna   Kovalska',
    'Anna\nKovalska',
    'Anna\tKovalska',
    'Anna\u00a0Kovalska',
  ])('accepts unintended spacing in %j', (value) => {
    const errors = runEditValidation({
      individualDataUpdateFields: [
        { fieldName: 'given_name_latin', fieldValue: value },
      ],
    });

    expect(errors.individualDataUpdateFields).toBeUndefined();
  });

  it.each([
    'Anna--Kovalska',
    "Anna'''Kovalska",
    "Anna - ' - Kovalska",
    "Anna O' Brien",
  ])('rejects repeated separators in %j', (value) => {
    const errors = runEditValidation({
      individualDataUpdateFields: [
        { fieldName: 'given_name_latin', fieldValue: value },
      ],
    });

    expect(errors.individualDataUpdateFields).toBe(FORMAT_ERROR);
  });
});

describe('validateUsingSteps - latin name format for add individual', () => {
  const runAddValidation = (individualData) =>
    validateUsingSteps(
      { ...addIndividualBase, individualData },
      [],
      {},
      {},
      GrievanceSteps.Description,
      () => undefined,
      beneficiaryGroup,
    );

  it('flags a malformed latin name under its own input', () => {
    const errors = runAddValidation({
      fullName: 'Иван Иванов',
      fullNameLatin: 'Иван',
    });

    expect(errors.individualData).toEqual({ fullNameLatin: FORMAT_ERROR });
  });

  it('does not require latin names', () => {
    const errors = runAddValidation({ fullName: 'Иван Иванов' });

    expect(errors.individualData).toBeUndefined();
  });
});

describe('validate - phone number, email and count formats', () => {
  const individualFieldsDict = {
    phone_no: { labelEn: 'Phone number', type: 'STRING' },
    phone_no_alternative: {
      labelEn: 'Alternative phone number',
      type: 'STRING',
    },
    email: { labelEn: 'Individual email', type: 'STRING' },
  };
  const householdFieldsDict = {
    size: { labelEn: 'Household size', type: 'INTEGER' },
  };
  const runEditIndividual = (rows) =>
    validate(
      { ...editIndividualBase, individualDataUpdateFields: rows },
      null,
      individualFieldsDict,
      {},
      beneficiaryGroup,
    );
  const runEditHousehold = (rows) =>
    validateUsingSteps(
      {
        category: GRIEVANCE_CATEGORIES.DATA_CHANGE,
        issueType: GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD,
        selectedHousehold: { id: 'hh-1' },
        householdDataUpdateFields: rows,
      },
      null,
      {},
      householdFieldsDict,
      GrievanceSteps.Description,
      () => undefined,
      beneficiaryGroup,
    );

  it.each(['12345', '0791234567', '+999', 'abc', '+48 600'])(
    'rejects phone number %j with the field label',
    (value) => {
      const errors = runEditIndividual([
        { fieldName: 'phone_no', fieldValue: value },
      ]);

      expect(errors.individualDataUpdateFields).toBe(
        'Phone number: Enter a valid phone number with the country code',
      );
    },
  );

  it.each(['+48609456789', '+48 609 456 789', '+1 (631) 784-1118'])(
    'accepts phone number %j',
    (value) => {
      const errors = runEditIndividual([
        { fieldName: 'phone_no_alternative', fieldValue: value },
      ]);

      expect(errors.individualDataUpdateFields).toBeUndefined();
    },
  );

  it.each(['john.example.com', 'john@', '@example.com', 'john@example'])(
    'rejects email %j with the field label',
    (value) => {
      const errors = runEditIndividual([
        { fieldName: 'email', fieldValue: value },
      ]);

      expect(errors.individualDataUpdateFields).toBe(
        'Individual email: Enter a valid email address',
      );
    },
  );

  it('accepts a well formed email', () => {
    const errors = runEditIndividual([
      { fieldName: 'email', fieldValue: 'john@example.com' },
    ]);

    expect(errors.individualDataUpdateFields).toBeUndefined();
  });

  it('rejects a negative household count with the field label', () => {
    const errors = runEditHousehold([{ fieldName: 'size', fieldValue: -1 }]);

    expect(errors.householdDataUpdateFields).toBe(
      'Household size: Value cannot be negative',
    );
  });

  it('accepts a zero household count', () => {
    const errors = runEditHousehold([{ fieldName: 'size', fieldValue: 0 }]);

    expect(errors.householdDataUpdateFields).toBeUndefined();
  });

  it('flags an invalid phone number and email under their own inputs when adding an individual', () => {
    const errors = validateUsingSteps(
      {
        ...addIndividualBase,
        individualData: { phoneNo: '12345', email: 'john.example.com' },
      },
      [],
      {},
      {},
      GrievanceSteps.Description,
      () => undefined,
      beneficiaryGroup,
    );

    expect(errors.individualData).toEqual({
      phoneNo: 'Enter a valid phone number with the country code',
      email: 'Enter a valid email address',
    });
  });
});
