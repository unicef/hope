import { ReportChoiceDataQuery } from '../../src/__generated__/graphql';

export const fakeReportChoiceData = {
  reportStatusChoices: [
    { name: 'Processing', value: '1', __typename: 'ChoiceObject' },
    { name: 'Generated', value: '2', __typename: 'ChoiceObject' },
    { name: 'Failed', value: '3', __typename: 'ChoiceObject' },
  ],
  reportTypesChoices: [
    { name: 'Individuals', value: '1', __typename: 'ChoiceObject' },
    { name: 'Households', value: '2', __typename: 'ChoiceObject' },
    {
      name: 'Cash Plan Verification',
      value: '3',
      __typename: 'ChoiceObject',
    },
    { name: 'Payments', value: '4', __typename: 'ChoiceObject' },
    { name: 'Payment verification', value: '5', __typename: 'ChoiceObject' },
    { name: 'Cash Plan', value: '6', __typename: 'ChoiceObject' },
    { name: 'Programme', value: '7', __typename: 'ChoiceObject' },
    { name: 'Individuals & Payment', value: '8', __typename: 'ChoiceObject' },
  ],
} as ReportChoiceDataQuery;
