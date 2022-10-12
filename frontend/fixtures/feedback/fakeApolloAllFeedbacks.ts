import { AllFeedbacksDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllFeedbacks = [
  {
    request: {
      query: AllFeedbacksDocument,
      variables: {
        feedbackId: '',
        issueType: '',
        createdBy: '',
        createdAtRange: '',
        businessAreaSlug: 'afghanistan',
        first: 10,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allFeedbacks: {
          totalCount: 1,
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'RmVlZGJhY2tOb2RlOmNhNzNkZjEyLTNiZTctNDM4Yy04OWUyLWMzYTAyZDIzZDcxMQ==',
                unicefId: 'MSG-22-0001',
                issueType: 'A_2',
                householdLookup: {
                  id:
                    'SG91c2Vob2xkTm9kZTozZGIyNzI5ZS03MjU5LTRiMTMtODNiMi0zMDkwZDg0N2U1Y2M=',
                  unicefId: 'HH-20-0000.0002',
                  __typename: 'HouseholdNode',
                },
                createdAt: '2022-09-29T07:39:01.955613+00:00',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                linkedGrievance: {
                  id:
                    'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzE4NDgwOC1hMTg3LTQ0YmUtYmVjYi1lYmFjZjA2MGNlMGQ=',
                  unicefId: 'GRV-0000002',
                  __typename: 'GrievanceTicketNode',
                },
                __typename: 'FeedbackNode',
              },
              __typename: 'FeedbackNodeEdge',
            },
          ],
          __typename: 'FeedbackNodeConnection',
        },
      },
    },
  },
];
