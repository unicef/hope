import { AllTargetPopulationsQuery } from '../../src/__generated__/graphql';

export const fakeAllTargetPopulation = {
  allTargetPopulation: {
    edges: [
      {
        node: {
          id:
            'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZTkzMTU2YWUtOWQ2Ni00MTVkLTk2OWUtMzYzZGJkMjlkNzVl',
          name: 'Example Target Population',
          status: 'OPEN',
          createdAt: '2022-04-13T08:56:10.671921',
          updatedAt: '2022-04-13T08:56:10.671951',
          candidateListTotalHouseholds: 0,
          finalListTotalHouseholds: null,
          program: {
            id:
              'UHJvZ3JhbU5vZGU6OGMyZWVhMDQtNzljMC00NGNjLWI0NDctNTdkYzA3ZjNmMTVh',
            name: 'Add write view around happen make never.',
            __typename: 'ProgramNode',
          },
          createdBy: {
            id: 'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
            firstName: 'Root',
            lastName: 'Rootkowski',
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
} as AllTargetPopulationsQuery;
