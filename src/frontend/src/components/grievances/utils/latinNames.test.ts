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
