import { AllHouseholdsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllHouseholds = [
  {
    request: {
      query: AllHouseholdsDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 10,
        orderBy: '-unicef_id',
      },
    },
    result: {
      data: {
        allHouseholds: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjE=',
            __typename: 'PageInfo',
          },
          totalCount: 2,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'SG91c2Vob2xkTm9kZTo4MmI2MTA3ZC1hYzg5LTQ2NTctYmVjYi1lOTY4ODdjNTU0ZWQ=',
                status: 'ACTIVE',
                unicefId: 'HH-20-0000.0001',
                hasDuplicates: false,
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                headOfHousehold: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6MzIyYzFhYjAtNjQ3NS00NThhLWEyNTQtMWEyY2QzMjY5NDM2',
                  fullName: 'Agata Kowalska',
                  __typename: 'IndividualNode',
                },
                size: 4,
                admin2: {
                  id:
                    'QWRtaW5BcmVhTm9kZTo2ZDRmZmJhNi0xN2Q3LTRhYjctYWJkYS1kODg2OWM3NjQxODc=',
                  name: 'Achin',
                  __typename: 'AreaNode',
                },
                residenceStatus: 'REFUGEE',
                totalCashReceived: null,
                currency: '',
                lastRegistrationDate: '2020-08-22T00:00:00',
                program: null,
                __typename: 'HouseholdNode',
              },
              __typename: 'HouseholdNodeEdge',
            },
          ],
          __typename: 'HouseholdNodeConnection',
        },
      },
    },
  },
];
