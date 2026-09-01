import { describe, expect, it } from 'vitest';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { prepareRestVariables } from './createGrievanceUtils';
import { prepareInitialValues } from './editGrievanceUtils';
import { validate, validateUsingSteps } from './validateGrievance';
import { GrievanceSteps } from '@utils/constants';

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

const individualDataOf = (variables) =>
  variables.extras.issueType.individualDataUpdateIssueTypeExtras.individualData;
const addIndividualDataOf = (variables) =>
  variables.extras.issueType.addIndividualIssueTypeExtras.individualData;

describe('prepareRestVariables - transliterateLatinNames', () => {
  // The backend rejects a name change that carries neither a *_latin twin nor the
  // flag, so the flag has to travel inside individual_data on every submission.
  it('sends the flag inside individualData for an individual data update', () => {
    const variables = prepareRestVariables({
      ...editIndividualBase,
      transliterateLatinNames: true,
      individualDataUpdateFields: [
        { fieldName: 'given_name', fieldValue: 'Ivan' },
      ],
    });

    expect(individualDataOf(variables).transliterateLatinNames).toBe(true);
    expect(individualDataOf(variables).givenName).toBe('Ivan');
  });

  it('sends the flag inside individualData when adding an individual', () => {
    const variables = prepareRestVariables({
      ...addIndividualBase,
      transliterateLatinNames: true,
      individualData: { fullName: 'Иван Иванов' },
    });

    expect(addIndividualDataOf(variables).transliterateLatinNames).toBe(true);
    expect(addIndividualDataOf(variables).fullName).toBe('Иван Иванов');
  });

  it('drops latin names when transliteration is on so they cannot override it', () => {
    // Explicit latin values win over transliteration on the backend, so leaving a
    // stale value behind after ticking the checkbox would silently be applied.
    const variables = prepareRestVariables({
      ...editIndividualBase,
      transliterateLatinNames: true,
      individualDataUpdateFields: [
        { fieldName: 'given_name', fieldValue: 'Ivan' },
        { fieldName: 'given_name_latin', fieldValue: 'Stale' },
      ],
    });

    expect(individualDataOf(variables).givenNameLatin).toBeUndefined();
  });

  it('keeps latin names when transliteration is off', () => {
    const variables = prepareRestVariables({
      ...editIndividualBase,
      transliterateLatinNames: false,
      individualDataUpdateFields: [
        { fieldName: 'given_name', fieldValue: 'Ivan' },
        { fieldName: 'given_name_latin', fieldValue: 'Ivan' },
      ],
    });

    expect(individualDataOf(variables).givenNameLatin).toBe('Ivan');
    expect(individualDataOf(variables).transliterateLatinNames).toBe(false);
  });

  it('drops latin names from the add individual payload when transliteration is on', () => {
    const variables = prepareRestVariables({
      ...addIndividualBase,
      transliterateLatinNames: true,
      individualData: { fullName: 'Иван Иванов', fullNameLatin: 'Stale' },
    });

    expect(addIndividualDataOf(variables).fullNameLatin).toBeUndefined();
  });
});

describe('validate - latin name rules', () => {
  const runEditValidation = (values) =>
    validate(
      { ...editIndividualBase, ...values },
      null,
      {},
      {},
      { memberLabel: 'Individual', groupLabel: 'Household' },
    );

  it('requires the latin twin of a changed name when transliteration is off', () => {
    const errors = runEditValidation({
      transliterateLatinNames: false,
      individualDataUpdateFields: [
        { fieldName: 'full_name', fieldValue: 'Иван Иванов' },
      ],
    });

    expect(errors.individualDataUpdateFields).toBe(
      'Provide full_name_latin or enable automatic transliteration',
    );
  });

  it('accepts a changed name without its latin twin when transliteration is on', () => {
    const errors = runEditValidation({
      transliterateLatinNames: true,
      individualDataUpdateFields: [
        { fieldName: 'full_name', fieldValue: 'Иван Иванов' },
      ],
    });

    expect(errors.individualDataUpdateFields).toBeUndefined();
  });

  it('accepts a changed name paired with its latin twin', () => {
    const errors = runEditValidation({
      transliterateLatinNames: false,
      individualDataUpdateFields: [
        { fieldName: 'full_name', fieldValue: 'Иван Иванов' },
        { fieldName: 'full_name_latin', fieldValue: "Ivan O'Ivanov-Smith" },
      ],
    });

    expect(errors.individualDataUpdateFields).toBeUndefined();
  });

  it('rejects latin values the backend regex would reject', () => {
    // The model validator runs at close time, long after the ticket was created -
    // catching it here keeps the ticket from being unclosable.
    const errors = runEditValidation({
      transliterateLatinNames: false,
      individualDataUpdateFields: [
        { fieldName: 'full_name', fieldValue: 'Иван Иванов' },
        { fieldName: 'full_name_latin', fieldValue: 'Иван 123' },
      ],
    });

    expect(errors.individualDataUpdateFields).toBe(
      'Only ASCII letters, spaces, hyphens and apostrophes are allowed',
    );
  });

  it('requires each name to have its own latin twin', () => {
    const errors = runEditValidation({
      transliterateLatinNames: false,
      individualDataUpdateFields: [
        { fieldName: 'given_name', fieldValue: 'Иван' },
        { fieldName: 'full_name_latin', fieldValue: 'Ivan Ivanov' },
      ],
    });

    expect(errors.individualDataUpdateFields).toBe(
      'Provide given_name_latin or enable automatic transliteration',
    );
  });
});

describe('prepareInitialValues - transliterateLatinNames', () => {
  const ticketBase = {
    priority: 1,
    urgency: 1,
    programs: [{ id: 'prog-1' }],
    linkedTickets: [],
    category: Number(GRIEVANCE_CATEGORIES.DATA_CHANGE),
    issueType: Number(GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL),
    individual: { id: 'ind-1' },
  };

  it('lifts the stored flag out of individualData instead of listing it as a field row', () => {
    // The backend wraps every individual_data key as {value, approve_status}, so
    // without this the flag would come back as an editable "transliterate latin names" row.
    const initialValues = prepareInitialValues({
      ...ticketBase,
      ticketDetails: {
        individualData: {
          givenName: { value: 'Ivan' },
          transliterateLatinNames: { value: false },
        },
      },
    } as any);

    expect(initialValues.transliterateLatinNames).toBe(false);
    expect(
      initialValues.individualDataUpdateFields.map((row) => row.fieldName),
    ).toEqual(['givenName']);
  });

  it('defaults to enabled when the ticket predates the flag', () => {
    const initialValues = prepareInitialValues({
      ...ticketBase,
      ticketDetails: { individualData: { givenName: { value: 'Ivan' } } },
    } as any);

    expect(initialValues.transliterateLatinNames).toBe(true);
  });
});

describe('validateUsingSteps - latin name rules for add individual', () => {
  const runAddValidation = (values) =>
    validateUsingSteps(
      { ...addIndividualBase, ...values },
      [],
      {},
      {},
      GrievanceSteps.Description,
      () => {},
      { memberLabel: 'Individual', groupLabel: 'Household' },
    );

  it('requires full_name_latin when transliteration is off', () => {
    const errors = runAddValidation({
      transliterateLatinNames: false,
      individualData: { fullName: 'Иван Иванов' },
    });

    expect(errors.individualData).toEqual({
      fullNameLatin: 'Provide full_name_latin or enable automatic transliteration',
    });
  });

  it('does not require latin names when transliteration is on', () => {
    const errors = runAddValidation({
      transliterateLatinNames: true,
      individualData: { fullName: 'Иван Иванов' },
    });

    expect(errors.individualData).toBeUndefined();
  });
});
