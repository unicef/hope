import {
  ProgramNode,
  ProgramPartnerAccess,
} from '../../src/__generated__/graphql';

export const fakeProgram = {
  id: 'UHJvZ3JhbU5vZGU6YzRkNTY1N2QtMWEyOS00NmUxLTgxOTAtZGY3Zjg1YTBkMmVm',
  name: 'Surface campaign practice actually about about will what.',
  startDate: '2020-02-25',
  endDate: '2020-10-18',
  status: 'FINISHED',
  description: 'Yeah worry might newspaper drive her many.',
  budget: '507922706.44',
  frequencyOfPayments: 'REGULAR',
  cashPlus: false,
  populationGoal: 341883,
  scope: 'UNICEF',
  sector: 'CHILD_PROTECTION',
  totalNumberOfHouseholds: 2,
  administrativeAreasOfImplementation: 'Crime book.',
  version: 1644233612796091,
  partnerAccess: ProgramPartnerAccess.SelectedPartnersAccess,
  partners: [
    {
      areas: [],
      areaAccess: 'BUSINESS_AREA',
      id: '1',
    },
  ],
  dataCollectingType: {
    code: '0',
    description: 'Partial individuals collected',
  },
  __typename: 'ProgramNode',
} as ProgramNode;
