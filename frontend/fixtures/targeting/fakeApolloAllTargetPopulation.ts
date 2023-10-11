import { AllTargetPopulationsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllTargetPopulation = [
  {
    request: {
      query: AllTargetPopulationsDocument,
      variables: {
        name: '',
        status: '',
        businessArea: 'afghanistan',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZTY2MDQyNDItYjk5Yi00ZjY3LWFjYTQtMzg3ZDk2YjIyNTky',
                name: 'Image until technology travel.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-09-26T10:58:21.441153+00:00',
                updatedAt: '2023-09-26T10:58:21.464554+00:00',
                totalHouseholdsCount: 2,
                totalHouseholdsCountWithValidPhoneNo: 2,
                totalIndividualsCount: 8,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6ZjcwN2U0ZTItYzYwZC00M2MxLTliMTAtYzI3NDFhZjZkMmFj',
                  name: 'Where analysis hand stand film.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6Zjc1YjE5M2ItYTE3ZC00NTVjLTgxOGItMjNlMTU4NjhkM2Y0',
                  firstName: 'Michael',
                  lastName: 'Jones',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZjUyOWE0N2QtZjc2Ni00NjQ3LWE1NjItZTQ4MjQ2N2ZjZjJh',
                name: 'Actually entire probably road just share fire.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-09-26T10:58:21.314363+00:00',
                updatedAt: '2023-09-26T10:58:21.338575+00:00',
                totalHouseholdsCount: 2,
                totalHouseholdsCountWithValidPhoneNo: 2,
                totalIndividualsCount: 8,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6ZjcwN2U0ZTItYzYwZC00M2MxLTliMTAtYzI3NDFhZjZkMmFj',
                  name: 'Where analysis hand stand film.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6YzExOWQzODItNjg1Mi00OWI4LTllZTktMTk2NmE0NTA3ZTA0',
                  firstName: 'Frances',
                  lastName: 'Ruiz',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6YTRhYTQ4MDctNjBiNy00YTU1LTlmNjUtMjQ3Zjg4ODljMjIw',
                name: 'Lead if southern service no use nothing.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-09-26T10:58:21.176746+00:00',
                updatedAt: '2023-09-26T10:58:21.201679+00:00',
                totalHouseholdsCount: 2,
                totalHouseholdsCountWithValidPhoneNo: 2,
                totalIndividualsCount: 8,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6ZjcwN2U0ZTItYzYwZC00M2MxLTliMTAtYzI3NDFhZjZkMmFj',
                  name: 'Where analysis hand stand film.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6M2MwZWI4YjEtNDBkZi00NmFiLWJjY2ItNGQxNGJmOWFjYmRm',
                  firstName: 'Sharon',
                  lastName: 'Schwartz',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMTIz',
                name: 'Test Target Population',
                status: 'ASSIGNED',
                createdAt: '2023-09-26T10:58:20.825189+00:00',
                updatedAt: '2023-09-26T10:58:20.864599+00:00',
                totalHouseholdsCount: 2,
                totalHouseholdsCountWithValidPhoneNo: 0,
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
