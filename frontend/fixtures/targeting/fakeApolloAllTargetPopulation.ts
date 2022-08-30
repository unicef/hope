import { AllTargetPopulationsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllTargetPopulation = [
  {
    request: {
      query: AllTargetPopulationsDocument,
      variables: {
        name: null,
        numberOfHouseholdsMin: 0,
        numberOfHouseholdsMax: 100,
        status: null,
        businessArea: 'afghanistan',
        first: 10,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allTargetPopulation: {
          edges: [
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6OTlmZGJhYmQtMzc4Ni00MjQ0LWEwNGQtMjIyYTI5MGZmNzRh',
                name: 'frfr',
                status: 'LOCKED',
                createdAt: '2022-02-24T09:48:13.750979',
                updatedAt: '2022-02-24T09:48:17.239308',
                totalHouseholdsCount: 2,
                totalIndividualsCount: 2,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDBkNWI4MmYtMjRlMy00MDE2LWFhN2EtODNlODE0NjM5Mzcx',
                  name: 'Teacher start pick give dinner story return.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6ODA0N2Q5ODctNDQzOC00ZDExLTg0MTctNjJlZGE3MTkyMTI4',
                  firstName: '',
                  lastName: '',
                  __typename: 'UserNode',
                },
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              __typename: 'TargetPopulationNodeEdge',
            },
          ],
          totalCount: 1,
          edgeCount: 1,
          __typename: 'TargetPopulationNodeConnection',
        },
      },
    },
  },
];
