import { AllHouseholdsForPopulationTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllHouseholdsForPopulationTable = [
  {
    request: {
      query: AllHouseholdsForPopulationTableDocument,
      variables: {
        businessArea: 'afghanistan',
        familySize: '{"min":"","max":""}',
        search: '',
        adminArea: '',
        residenceStatus: '',
        first: 10,
        orderBy: 'unicef_id',
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
                  'SG91c2Vob2xkTm9kZTowOWI4YWE2ZC1hOTViLTQ5NWEtYTM0ZS1kMGM0YmQyNWE4Njc=',
                status: 'ACTIVE',
                unicefId: 'HH-20-0000.0001',
                hasDuplicates: false,
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                headOfHousehold: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6N2JhZjlhMGItODQ4My00MDA0LTg2NzAtMGU4YTUwZjI1YTMw',
                  fullName: 'Agata Kowalska',
                  __typename: 'IndividualNode',
                },
                size: 4,
                admin2: {
                  id:
                    'QXJlYU5vZGU6NzYxZjhkODQtOTljZi00MWExLTk1MmYtMTQ5ZWFhNjJkZDJh',
                  name: 'Achin',
                  __typename: 'AreaNode',
                },
                residenceStatus: 'REFUGEE',
                totalCashReceived: null,
                currency: '',
                lastRegistrationDate: '2020-08-22T00:00:00',
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
