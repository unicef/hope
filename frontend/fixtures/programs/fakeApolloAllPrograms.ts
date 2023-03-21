import { AllProgramsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPrograms = [
  {
    request: {
      query: AllProgramsDocument,
      variables: {
        businessArea: 'afghanistan',
        search: '',
        status: '',
        sector: [],
        numberOfHouseholds: '{"min":"","max":""}',
        budget: '{"min":"","max":""}',
        first: 5,
        orderBy: null,
      },
    },
    result: {
      data: {
        allPrograms: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          totalCount: 9,
          edgeCount: 5,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UHJvZ3JhbU5vZGU6ZDM4YWI4MTQtOTQyNy00ZmJkLTg4ODctOGUyYzlkMzcxYjg2',
                name: 'Notice hair fall college enough perhaps.',
                startDate: '2020-01-20',
                endDate: '2020-08-19',
                status: 'ACTIVE',
                caId: '123-21-PRG-00001',
                description:
                  'Purpose she occur lose new wish day per little because east like bill.',
                budget: '691946197.49',
                frequencyOfPayments: 'ONE_OFF',
                populationGoal: 507376,
                sector: 'EDUCATION',
                totalNumberOfHouseholds: 12,
                individualDataNeeded: true,
                __typename: 'ProgramNode',
              },
              __typename: 'ProgramNodeEdge',
            },
          ],
          __typename: 'ProgramNodeConnection',
        },
      },
    },
  },
];
