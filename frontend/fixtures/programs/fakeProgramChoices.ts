import { ProgrammeChoiceDataQuery } from '../../src/__generated__/graphql';

export const fakeProgramChoices = {
  programFrequencyOfPaymentsChoices: [
    { name: 'Regular', value: 'REGULAR', __typename: 'ChoiceObject' },
    { name: 'One-off', value: 'ONE_OFF', __typename: 'ChoiceObject' },
  ],
  programScopeChoices: [
    { name: 'For partners', value: 'FOR_PARTNERS', __typename: 'ChoiceObject' },
    { name: 'Unicef', value: 'UNICEF', __typename: 'ChoiceObject' },
  ],
  programSectorChoices: [
    {
      name: 'Child Protection',
      value: 'CHILD_PROTECTION',
      __typename: 'ChoiceObject',
    },
    { name: 'Education', value: 'EDUCATION', __typename: 'ChoiceObject' },
    { name: 'Health', value: 'HEALTH', __typename: 'ChoiceObject' },
    {
      name: 'Multi Purpose',
      value: 'MULTI_PURPOSE',
      __typename: 'ChoiceObject',
    },
    { name: 'Nutrition', value: 'NUTRITION', __typename: 'ChoiceObject' },
    {
      name: 'Social Policy',
      value: 'SOCIAL_POLICY',
      __typename: 'ChoiceObject',
    },
    { name: 'WASH', value: 'WASH', __typename: 'ChoiceObject' },
  ],
  programStatusChoices: [
    { name: 'Draft', value: 'DRAFT', __typename: 'ChoiceObject' },
    { name: 'Active', value: 'ACTIVE', __typename: 'ChoiceObject' },
    { name: 'Finished', value: 'FINISHED', __typename: 'ChoiceObject' },
  ],
  dataCollectionTypeChoices: [
    { name: 'Full', value: 'full', __typename: 'ChoiceObject' },
    { name: 'Partial', value: 'partial', __typename: 'ChoiceObject' }
  ]
} as ProgrammeChoiceDataQuery;
