import { AllDeliveryMechanismsQuery } from '../../src/__generated__/graphql';

export const fakeDeliveryMechanisms = {
  allDeliveryMechanisms: [
    { name: 'None', value: '', __typename: 'ChoiceObject' },
    {
      name: 'Displaced  |  Internally Displaced People',
      value: 'IDP',
      __typename: 'ChoiceObject',
    },
  ],
} as AllDeliveryMechanismsQuery;
