import { HouseholdChoiceDataQuery } from '../../src/__generated__/graphql';

export const fakeHouseholdChoices = {
  residenceStatusChoices: [
    { name: 'None', value: '', __typename: 'ChoiceObject' },
    {
      name: 'Displaced  |  Internally Displaced People',
      value: 'IDP',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Displaced  |  Refugee / Asylum Seeker',
      value: 'REFUGEE',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Displaced  |  Others of Concern',
      value: 'OTHERS_OF_CONCERN',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Non-displaced  |   Host',
      value: 'HOST',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Non-displaced  |   Non-host',
      value: 'NON_HOST',
      __typename: 'ChoiceObject',
    },
  ],
  relationshipChoices: [
    { name: 'Unknown', value: 'UNKNOWN', __typename: 'ChoiceObject' },
    {
      name: 'Not a Family Member. Can only act as a recipient.',
      value: 'NON_BENEFICIARY',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Head of household (self)',
      value: 'HEAD',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Son / Daughter',
      value: 'SON_DAUGHTER',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Wife / Husband',
      value: 'WIFE_HUSBAND',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Brother / Sister',
      value: 'BROTHER_SISTER',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Mother / Father',
      value: 'MOTHER_FATHER',
      __typename: 'ChoiceObject',
    },
    { name: 'Aunt / Uncle', value: 'AUNT_UNCLE', __typename: 'ChoiceObject' },
    {
      name: 'Grandmother / Grandfather',
      value: 'GRANDMOTHER_GRANDFATHER',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Mother-in-law / Father-in-law',
      value: 'MOTHERINLAW_FATHERINLAW',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Daughter-in-law / Son-in-law',
      value: 'DAUGHTERINLAW_SONINLAW',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Sister-in-law / Brother-in-law',
      value: 'SISTERINLAW_BROTHERINLAW',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Granddaughter / Grandson',
      value: 'GRANDDAUGHER_GRANDSON',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Nephew / Niece',
      value: 'NEPHEW_NIECE',
      __typename: 'ChoiceObject',
    },
    { name: 'Cousin', value: 'COUSIN', __typename: 'ChoiceObject' },
  ],
  roleChoices: [
    { name: 'Primary collector', value: 'PRIMARY', __typename: 'ChoiceObject' },
    {
      name: 'Alternate collector',
      value: 'ALTERNATE',
      __typename: 'ChoiceObject',
    },
    { name: 'None', value: 'NO_ROLE', __typename: 'ChoiceObject' },
  ],
  maritalStatusChoices: [
    { name: 'None', value: '', __typename: 'ChoiceObject' },
    { name: 'Single', value: 'SINGLE', __typename: 'ChoiceObject' },
    { name: 'Married', value: 'MARRIED', __typename: 'ChoiceObject' },
    { name: 'Widowed', value: 'WIDOWED', __typename: 'ChoiceObject' },
    { name: 'Divorced', value: 'DIVORCED', __typename: 'ChoiceObject' },
    { name: 'Separated', value: 'SEPARATED', __typename: 'ChoiceObject' },
  ],
  workStatusChoices: [
    { name: 'Yes', value: '1', __typename: 'ChoiceObject' },
    { name: 'No', value: '0', __typename: 'ChoiceObject' },
    { name: 'Not provided', value: 'NOT_PROVIDED', __typename: 'ChoiceObject' },
  ],
  deduplicationBatchStatusChoices: [
    {
      name: 'Similar in batch',
      value: 'SIMILAR_IN_BATCH',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Duplicate in batch',
      value: 'DUPLICATE_IN_BATCH',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Unique in batch',
      value: 'UNIQUE_IN_BATCH',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Not Processed',
      value: 'NOT_PROCESSED',
      __typename: 'ChoiceObject',
    },
  ],
  deduplicationGoldenRecordStatusChoices: [
    { name: 'Unique', value: 'UNIQUE', __typename: 'ChoiceObject' },
    { name: 'Duplicate', value: 'DUPLICATE', __typename: 'ChoiceObject' },
    {
      name: 'Needs Adjudication',
      value: 'NEEDS_ADJUDICATION',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Not Processed',
      value: 'NOT_PROCESSED',
      __typename: 'ChoiceObject',
    },
  ],
  observedDisabilityChoices: [
    { name: 'None', value: 'NONE', __typename: 'ChoiceObject' },
    {
      name: 'Difficulty seeing (even if wearing glasses)',
      value: 'SEEING',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Difficulty hearing (even if using a hearing aid)',
      value: 'HEARING',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Difficulty walking or climbing steps',
      value: 'WALKING',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Difficulty remembering or concentrating',
      value: 'MEMORY',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Difficulty with self care (washing, dressing)',
      value: 'SELF_CARE',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Difficulty communicating (e.g understanding or being understood)',
      value: 'COMMUNICATING',
      __typename: 'ChoiceObject',
    },
  ],
  severityOfDisabilityChoices: [
    { name: 'None', value: '', __typename: 'ChoiceObject' },
    {
      name: 'Some difficulty',
      value: 'SOME_DIFFICULTY',
      __typename: 'ChoiceObject',
    },
    {
      name: 'A lot of difficulty',
      value: 'LOT_DIFFICULTY',
      __typename: 'ChoiceObject',
    },
    {
      name: 'Cannot do at all',
      value: 'CANNOT_DO',
      __typename: 'ChoiceObject',
    },
  ],
} as HouseholdChoiceDataQuery;
