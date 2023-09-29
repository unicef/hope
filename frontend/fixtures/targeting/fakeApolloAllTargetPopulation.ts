import { AllTargetPopulationsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllTargetPopulation = [
  {
    request: {
      query: AllTargetPopulationsDocument,
      variables: {
        name: '',
        totalHouseholdsCountMin: 0,
        totalHouseholdsCountMax: null,
        status: '',
        businessArea: 'afghanistan',
        program: [
          'UHJvZ3JhbU5vZGU6YzRkNTY1N2QtMWEyOS00NmUxLTgxOTAtZGY3Zjg1YTBkMmVm',
        ],
        createdAtRange: '{"min":null,"max":null}',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MjQyZmQ4NDQtOTYzOC00MTdhLTkzZWMtYjQzMjY0Y2Y4YmRj',
                name: 'Our ball many investment look like.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-09-29T10:52:33.042363+00:00',
                updatedAt: '2023-09-29T10:52:33.068191+00:00',
                totalHouseholdsCount: 0,
                totalHouseholdsCountWithValidPhoneNo: 0,
                totalIndividualsCount: null,
                __typename: 'TargetPopulationNode',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6M2ZlNWE2OGMtYTI3Mi00Y2UzLWE3YzgtODhkNWIyOTY1YjMy',
                  firstName: 'Mary',
                  lastName: 'Reyes',
                  __typename: 'UserNode',
                },
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              __typename: 'TargetPopulationNodeEdge',
            },
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6YjI0ZDA5ZTUtN2E1Yy00MjgyLWI4ZmItYWY4MDkwMGY5YzRm',
                name: 'Less road structure audience those modern.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-09-29T10:52:30.379605+00:00',
                updatedAt: '2023-09-29T10:52:30.412142+00:00',
                totalHouseholdsCount: 0,
                totalHouseholdsCountWithValidPhoneNo: 0,
                totalIndividualsCount: null,
                __typename: 'TargetPopulationNode',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6ZDA0MjdlNjktN2U1Mi00NmYzLTljNjItMGU1YzJlZWRjNGYz',
                  firstName: 'Elizabeth',
                  lastName: 'Coleman',
                  __typename: 'UserNode',
                },
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              __typename: 'TargetPopulationNodeEdge',
            },
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6YzBiMzE0NjItNmIzMC00OGNiLTljMmMtZDgzM2JkZTJmNGYx',
                name: 'Score visit write ask whole myself.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-09-29T10:52:30.190168+00:00',
                updatedAt: '2023-09-29T10:52:30.220259+00:00',
                totalHouseholdsCount: 0,
                totalHouseholdsCountWithValidPhoneNo: 0,
                totalIndividualsCount: null,
                __typename: 'TargetPopulationNode',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6ODE3OWIyMDAtZjBhZC00OWYyLWJjZDItNTYwZjUxZDZlOGNj',
                  firstName: 'Jennifer',
                  lastName: 'Bailey',
                  __typename: 'UserNode',
                },
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              __typename: 'TargetPopulationNodeEdge',
            },
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMTIz',
                name: 'Test Target Population',
                status: 'ASSIGNED',
                createdAt: '2023-09-29T10:52:29.726956+00:00',
                updatedAt: '2023-09-29T10:52:29.779197+00:00',
                totalHouseholdsCount: 2,
                totalHouseholdsCountWithValidPhoneNo: 0,
                totalIndividualsCount: 8,
                __typename: 'TargetPopulationNode',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  __typename: 'UserNode',
                },
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              __typename: 'TargetPopulationNodeEdge',
            },
          ],
          totalCount: 4,
          edgeCount: 4,
          __typename: 'TargetPopulationNodeConnection',
        },
      },
    },
  },
];
