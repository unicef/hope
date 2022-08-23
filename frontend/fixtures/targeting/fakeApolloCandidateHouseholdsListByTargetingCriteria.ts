import { TargetPopulationHouseholdsDocument } from '../../src/__generated__/graphql';

export const fakeApolloTargetPopulationHouseholds = [
  {
    request: {
      query: TargetPopulationHouseholdsDocument,
      variables: {
        first: 10,
        orderBy: null,
        targetPopulation:
          'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZDYzNWQ0ZDMtNGI1My00MTVkLTkzZWYtNjFlODhjZDg0MWMy',
      },
    },
    result: {
      data: {
        candidateHouseholdsListByTargetingCriteria: {
          edges: [
            {
              node: {
                id:
                  'SG91c2Vob2xkTm9kZTozZjg1YWZjMC0zNTVhLTQ3ODAtYmVkZC0wMTE2ZTU0MmUyOGY=',
                unicefId: 'HH-21-0000.1137',
                headOfHousehold: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6NmQ5ZTgwMDctZTZmNS00YmZjLTk0NDktY2UyMTk4ZTFjZjNk',
                  givenName: 'Johnie',
                  familyName: 'Zielinski',
                  fullName: 'Johnie Zielinski',
                  __typename: 'IndividualNode',
                },
                size: 1,
                adminArea: {
                  id:
                    'QWRtaW5BcmVhTm9kZTpkMGQ1YmNmNS1hZDU1LTQ4YWMtODcyZS1mM2FkZGY0NDdjNDE=',
                  name: 'North Kordofan',
                  __typename: 'AreaNode',
                },
                updatedAt: '2021-12-16T10:16:45.282245',
                address: '',
                selection: null,
                __typename: 'HouseholdNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              __typename: 'HouseholdNodeEdge',
            },
            {
              node: {
                id:
                  'SG91c2Vob2xkTm9kZTpjMGQxMzIyMS0xYTk5LTQ2NDItYjZmNi05OTJjZWEzODAzNTY=',
                unicefId: 'HH-21-0000.1133',
                headOfHousehold: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6ZjM2ZDA3YTYtNzgyZi00OGE3LWJjZGEtOWY4ZDI5ZmE0Yjg1',
                  givenName: 'Jennifer',
                  familyName: 'Foster',
                  fullName: 'Jennifer Foster',
                  __typename: 'IndividualNode',
                },
                size: 1,
                adminArea: {
                  id:
                    'QWRtaW5BcmVhTm9kZTpkMGRkNDRkZC1iNzRiLTQ1MjYtOTAyNC0xOTg2MWI1ZDNkOWQ=',
                  name: 'River Nile',
                  __typename: 'AreaNode',
                },
                updatedAt: '2021-12-16T10:16:45.281644',
                address: '',
                selection: null,
                __typename: 'HouseholdNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              __typename: 'HouseholdNodeEdge',
            },
          ],
          totalCount: 2,
          edgeCount: 2,
          __typename: 'HouseholdNodeConnection',
        },
      },
    },
  },
];
