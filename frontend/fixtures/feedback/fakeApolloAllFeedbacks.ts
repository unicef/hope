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
        first: 10,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allFeedbacks: {
          totalCount: 2,
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjE=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'RmVlZGJhY2tOb2RlOjM3YmJiOTI2LTNkNjUtNDlhNy04YTU0LWRjYjYxMzc5ZWIyMQ==',
                unicefId: 'FED-23-0002',
                issueType: 'NEGATIVE_FEEDBACK',
                householdLookup: null,
                createdAt: '2023-06-15T18:32:24.711951+00:00',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                linkedGrievance: null,
                __typename: 'FeedbackNode',
              },
              __typename: 'FeedbackNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'RmVlZGJhY2tOb2RlOjRmNzdmMmIyLTk4YTMtNGMyMy1hZGM4LTAxMDEwYTczMGY4Nw==',
                unicefId: 'FED-23-0001',
                issueType: 'NEGATIVE_FEEDBACK',
                householdLookup: {
                  id:
                    'SG91c2Vob2xkTm9kZToyMDA3NzQ5OC04MGYwLTQ2MmEtODJlNi04NjZjZWY5MmQwNmE=',
                  unicefId: 'HH-20-0000.0001',
                  __typename: 'HouseholdNode',
                },
                createdAt: '2023-06-15T15:04:39.755594+00:00',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                linkedGrievance: null,
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
