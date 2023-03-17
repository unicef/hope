import { AllTargetPopulationsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllTargetPopulation = [
  {
    request: {
      query: AllTargetPopulationsDocument,
      variables: {
        name: '',
        numberOfHouseholdsMin: null,
        numberOfHouseholdsMax: null,
        status: '',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MzVkYTkwMTMtY2IyMy00ZTQ0LWFlYzEtNmUyMDllNjg2MjA2',
                name: 'feeeee',
                status: 'ASSIGNED',
                createdAt: '2023-03-09T15:14:00.326946+00:00',
                updatedAt: '2023-03-09T15:14:39.506326+00:00',
                totalHouseholdsCount: 4,
                totalIndividualsCount: 17,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OWE5NjI0NjktNzU3NC00Y2M0LWFjYzUtYjU1Y2QxNWJmNzFm',
                  name: 'If appear agreement discuss hair international.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6ZWVjMjJlZjgtNzRiZC00MmE5LTlkZTEtNzljNzg1MDRkMzll',
                  firstName: '',
                  lastName: '',
                  __typename: 'UserNode',
                },
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              __typename: 'TargetPopulationNodeEdge',
            },
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6NmYwMGM3N2ItYmE1ZS00NTQyLWE3YTctOTJkNGY2MTk5NTcz',
                name: 'Manage whole study crime so receive.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-03-08T13:02:06.449223+00:00',
                updatedAt: '2023-03-08T13:02:06.486382+00:00',
                totalHouseholdsCount: 3,
                totalIndividualsCount: 14,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OWE5NjI0NjktNzU3NC00Y2M0LWFjYzUtYjU1Y2QxNWJmNzFm',
                  name: 'If appear agreement discuss hair international.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDEzM2QyMDAtZDczYS00YTBiLTg5NGQtN2E3NDgyY2JiZjAy',
                  firstName: 'Ashley',
                  lastName: 'Smith',
                  __typename: 'UserNode',
                },
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              __typename: 'TargetPopulationNodeEdge',
            },
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MzYzNDk5YTYtMTRlOC00MmZlLWE5MGYtNmVkYTI0MjIwMDk1',
                name: 'Role eat seem road cup worker modern.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-03-08T13:02:06.230343+00:00',
                updatedAt: '2023-03-08T13:02:06.270910+00:00',
                totalHouseholdsCount: 3,
                totalIndividualsCount: 14,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OWE5NjI0NjktNzU3NC00Y2M0LWFjYzUtYjU1Y2QxNWJmNzFm',
                  name: 'If appear agreement discuss hair international.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6ZDY5NWYyNjAtZTkyOS00MzM1LWE2ZTAtMWJhOTAyMjRkMmRm',
                  firstName: 'Sophia',
                  lastName: 'Goodwin',
                  __typename: 'UserNode',
                },
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              __typename: 'TargetPopulationNodeEdge',
            },
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6YmNlOWZhM2QtODBjOC00YmM0LWIzZjItODIzMTM3NWY0ODVh',
                name: 'Ok with turn difficult policy.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-03-08T13:02:04.267826+00:00',
                updatedAt: '2023-03-08T13:02:04.306629+00:00',
                totalHouseholdsCount: 2,
                totalIndividualsCount: 8,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OWE5NjI0NjktNzU3NC00Y2M0LWFjYzUtYjU1Y2QxNWJmNzFm',
                  name: 'If appear agreement discuss hair international.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6OThkZDQ1ZGItYWZiMC00MWNlLTg1YTktZjkyNGI5MzgwODM1',
                  firstName: 'James',
                  lastName: 'Aguilar',
                  __typename: 'UserNode',
                },
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              __typename: 'TargetPopulationNodeEdge',
            },
            {
              node: {
                id:
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMTIz',
                name: 'Test Target Population',
                status: 'ASSIGNED',
                createdAt: '2023-03-08T13:02:03.689113+00:00',
                updatedAt: '2023-03-08T13:02:03.735184+00:00',
                totalHouseholdsCount: 2,
                totalIndividualsCount: 8,
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
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              __typename: 'TargetPopulationNodeEdge',
            },
          ],
          totalCount: 5,
          edgeCount: 5,
          __typename: 'TargetPopulationNodeConnection',
        },
      },
    },
  },
];
