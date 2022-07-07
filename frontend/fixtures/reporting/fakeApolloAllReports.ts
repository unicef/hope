import { AllReportsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllReports = [
  {
    request: {
      query: AllReportsDocument,
      variables: {
        businessArea: 'afghanistan',
        createdBy: null,
        first: 5,
        orderBy: null,
      },
    },
    result: {
      data: {
        allReports: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          totalCount: 1,
          edgeCount: 1,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UmVwb3J0Tm9kZTo4OTlhNDM0My1jOWEwLTRkM2ItOGIyNi02MzhiMTVlMjM5ZGE=',
                reportType: 1,
                dateFrom: '2019-11-17',
                dateTo: '2022-03-02',
                status: 1,
                createdAt: '2022-02-28T11:43:03.576723',
                updatedAt: '2022-02-28T11:45:03.576723',
                createdBy: {
                  firstName: '',
                  lastName: '',
                  __typename: 'UserNode',
                },
                fileUrl: '',
                numberOfRecords: null,
                __typename: 'ReportNode',
              },
              __typename: 'ReportNodeEdge',
            },
          ],
          __typename: 'ReportNodeConnection',
        },
      },
    },
  },
];
