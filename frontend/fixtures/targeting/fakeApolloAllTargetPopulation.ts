import { AllTargetPopulationsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllTargetPopulation = [
  {
    request: {
      query: AllTargetPopulationsDocument,
      variables: {
        name: '',
        totalHouseholdsCountMin: null,
        totalHouseholdsCountMax: null,
        createdAtRange: '{}',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZTZjZDc0YjgtZjA3Yi00ZTA2LTg2MTAtNWYwMjkwYTA2N2Q0',
                name: 'Key PM attack.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-08-30T08:58:56.158232+00:00',
                updatedAt: '2023-08-30T08:58:56.185496+00:00',
                totalHouseholdsCount: 3,
                totalHouseholdsCountWithValidPhoneNo: 3,
                totalIndividualsCount: 15,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OWNiODk2NTgtMjllMi00ODMzLWFhMzItMTMzNTYwNDcwM2Ri',
                  name: 'Top choose business son read outside give.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6MGUzNDU5NGItZWExNS00ZjQ4LThkNDktZDk1MWNkMzdjMWU4',
                  firstName: 'Brittany',
                  lastName: 'Ramos',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MGJlNzFjZjMtYjYyOC00NGUyLTkyMjUtNzM4Y2IxZmJlNWFk',
                name: 'Argue manage pass part.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-08-30T08:58:56.022529+00:00',
                updatedAt: '2023-08-30T08:58:56.051394+00:00',
                totalHouseholdsCount: 3,
                totalHouseholdsCountWithValidPhoneNo: 3,
                totalIndividualsCount: 15,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OWNiODk2NTgtMjllMi00ODMzLWFhMzItMTMzNTYwNDcwM2Ri',
                  name: 'Top choose business son read outside give.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6MDY1ODdhY2YtN2RjZC00MWMwLWE5OGEtMDYzYzA0Y2FlMDc0',
                  firstName: 'Richard',
                  lastName: 'Bailey',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6NDMxZGM2YWItNWE4Ni00MzI2LWI0OGQtMTA1ODg5NzIyOTBk',
                name: 'Television teach sea letter old.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-08-30T08:58:53.922963+00:00',
                updatedAt: '2023-08-30T08:58:53.950427+00:00',
                totalHouseholdsCount: 2,
                totalHouseholdsCountWithValidPhoneNo: 2,
                totalIndividualsCount: 8,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OWNiODk2NTgtMjllMi00ODMzLWFhMzItMTMzNTYwNDcwM2Ri',
                  name: 'Top choose business son read outside give.',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6YTZlZjM5NWYtYTQwZS00MzUyLWE2NWUtODg0ZWIxZmI0YWI2',
                  firstName: 'Dakota',
                  lastName: 'Rodriguez',
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
                createdAt: '2023-08-30T08:58:53.537158+00:00',
                updatedAt: '2023-08-30T08:58:53.578860+00:00',
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
