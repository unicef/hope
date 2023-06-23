import { AllTargetPopulationsDocument } from '../../src/__generated__/graphql';
import { fakeProgram } from '../programs/fakeProgram';

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
        program: ['c4d5657d-1a29-46e1-8190-df7f85a0d2ef'],
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
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6YWM0ZGNiZDktNzRiNy00MzMyLWI0NGEtNmM1MWZmYzlhZDZm',
                  firstName: 'Sabrina',
                  lastName: 'Parker',
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
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6MmY2NzY1NzQtNjJjNS00ZWFlLTk5MjYtOGQ2ODk0NTE2ODMy',
                  firstName: 'Mario',
                  lastName: 'Hayes',
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
                  'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZjVjODkxZDQtYWMyNC00M2MwLWE3N2EtMjIyYWNkODc3OGRl',
                name: 'Read stuff force start model.',
                status: 'READY_FOR_CASH_ASSIST',
                createdAt: '2023-06-21T09:17:01.518063+00:00',
                updatedAt: '2023-06-21T09:17:01.587942+00:00',
                totalHouseholdsCount: 2,
                totalIndividualsCount: 8,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6NmI1OTE1OTktYmNhNy00NDVhLWJmZjItYWU5MTUyMjMxZGFm',
                  name: 'Inside girl analysis report.66688849444',
                  __typename: 'ProgramNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6NmRjYmZiZmEtYjJiOS00Yzc2LWFmYTctMDNjZTlkNGNiMjY4',
                  firstName: 'Fernando',
                  lastName: 'Wells',
                  __typename: 'UserNode',
                },
                __typename: 'TargetPopulationNode',
              },
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              __typename: 'TargetPopulationNodeEdge',
            },
          ],
          totalCount: 3,
          edgeCount: 3,
          __typename: 'TargetPopulationNodeConnection',
        },
      },
    },
  },
];
