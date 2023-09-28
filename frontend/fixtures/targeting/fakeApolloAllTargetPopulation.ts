import { AllTargetPopulationsDocument } from '../../src/__generated__/graphql';
import { fakeProgram } from '../programs/fakeProgram';

export const fakeApolloAllTargetPopulation = [
  {
    request: {
      query: AllTargetPopulationsDocument,
      variables: {
        name: '',
        status: '',
        program: [fakeProgram.id],
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
<<<<<<< HEAD
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6YTY3MGJmNTQtOGJiOS00MzU5LTkwMjEtYjZhNmJmYTM2ZGU2',
                name: 'Growth get try financial country south.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-06-21T09:17:05.197737+00:00',
                updatedAt: '2023-06-21T09:17:05.273250+00:00',
                totalHouseholdsCount: 3,
                totalIndividualsCount: 13,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6NmI1OTE1OTktYmNhNy00NDVhLWJmZjItYWU5MTUyMjMxZGFm',
                  name: 'Inside girl analysis report.66688849444',
=======
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
>>>>>>> develop
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
<<<<<<< HEAD
                    'VXNlck5vZGU6YWM0ZGNiZDktNzRiNy00MzMyLWI0NGEtNmM1MWZmYzlhZDZm',
                  firstName: 'Sabrina',
                  lastName: 'Parker',
=======
                    'VXNlck5vZGU6Zjc1YjE5M2ItYTE3ZC00NTVjLTgxOGItMjNlMTU4NjhkM2Y0',
                  firstName: 'Michael',
                  lastName: 'Jones',
>>>>>>> develop
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
<<<<<<< HEAD
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MGI1NDljMjMtYTMxNC00ZDY0LWIxZDktOGVmMDliYWE1OWFj',
                name: 'Stop per point address bit lose set.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-06-21T09:17:04.608777+00:00',
                updatedAt: '2023-06-21T09:17:04.715117+00:00',
                totalHouseholdsCount: 3,
                totalIndividualsCount: 13,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6NmI1OTE1OTktYmNhNy00NDVhLWJmZjItYWU5MTUyMjMxZGFm',
                  name: 'Inside girl analysis report.66688849444',
=======
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
>>>>>>> develop
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
<<<<<<< HEAD
                    'VXNlck5vZGU6MmY2NzY1NzQtNjJjNS00ZWFlLTk5MjYtOGQ2ODk0NTE2ODMy',
                  firstName: 'Mario',
                  lastName: 'Hayes',
=======
                    'VXNlck5vZGU6YzExOWQzODItNjg1Mi00OWI4LTllZTktMTk2NmE0NTA3ZTA0',
                  firstName: 'Frances',
                  lastName: 'Ruiz',
>>>>>>> develop
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
<<<<<<< HEAD
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZjVjODkxZDQtYWMyNC00M2MwLWE3N2EtMjIyYWNkODc3OGRl',
                name: 'Read stuff force start model.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-06-21T09:17:01.518063+00:00',
                updatedAt: '2023-06-21T09:17:01.587942+00:00',
=======
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6YTRhYTQ4MDctNjBiNy00YTU1LTlmNjUtMjQ3Zjg4ODljMjIw',
                name: 'Lead if southern service no use nothing.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-09-26T10:58:21.176746+00:00',
                updatedAt: '2023-09-26T10:58:21.201679+00:00',
>>>>>>> develop
                totalHouseholdsCount: 2,
                totalIndividualsCount: 8,
                program: {
                  id:
<<<<<<< HEAD
                    'UHJvZ3JhbU5vZGU6NmI1OTE1OTktYmNhNy00NDVhLWJmZjItYWU5MTUyMjMxZGFm',
                  name: 'Inside girl analysis report.66688849444',
=======
                    'UHJvZ3JhbU5vZGU6ZjcwN2U0ZTItYzYwZC00M2MxLTliMTAtYzI3NDFhZjZkMmFj',
                  name: 'Where analysis hand stand film.',
>>>>>>> develop
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
<<<<<<< HEAD
                    'VXNlck5vZGU6NmRjYmZiZmEtYjJiOS00Yzc2LWFmYTctMDNjZTlkNGNiMjY4',
                  firstName: 'Fernando',
                  lastName: 'Wells',
=======
                    'VXNlck5vZGU6M2MwZWI4YjEtNDBkZi00NmFiLWJjY2ItNGQxNGJmOWFjYmRm',
                  firstName: 'Sharon',
                  lastName: 'Schwartz',
>>>>>>> develop
                  __typename: 'UserNode',
                },
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              __typename: 'TargetPopulationNodeEdge',
            },
<<<<<<< HEAD
=======
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
>>>>>>> develop
          ],
          totalCount: 3,
          edgeCount: 3,
          __typename: 'TargetPopulationNodeConnection',
        },
      },
    },
  },
];
