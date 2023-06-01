import { AllAccountabilityCommunicationMessagesDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllCommunicationMessages = [
  {
    request: {
      query: AllAccountabilityCommunicationMessagesDocument,
      variables: {
        createdAtRange: '',
        targetPopulation: '',
        createdBy: '',
        first: 10,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allAccountabilityCommunicationMessages: {
          totalCount: 5,
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'Q29tbXVuaWNhdGlvbk1lc3NhZ2VOb2RlOjExMDZmNThmLTJkZDMtNDQ5OC1hZjNkLTI2YzNhNDc2ZjkwZg==',
                unicefId: 'MSG-23-0005',
                title: 'jij',
                numberOfRecipients: 1,
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                createdAt: '2023-05-31T12:49:15.147652+00:00',
                __typename: 'CommunicationMessageNode',
              },
              __typename: 'CommunicationMessageNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'Q29tbXVuaWNhdGlvbk1lc3NhZ2VOb2RlOjExNzVmMzMwLTM2Y2MtNDM5NC04MjAyLWU4NjY3ZTI5ZTc4MA==',
                unicefId: 'MSG-22-0002',
                title: 'You got credit of USD 200',
                numberOfRecipients: 2,
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-16T08:33:09.955000+00:00',
                __typename: 'CommunicationMessageNode',
              },
              __typename: 'CommunicationMessageNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'Q29tbXVuaWNhdGlvbk1lc3NhZ2VOb2RlOjc1OGJiMjg0LTJjZjAtNGZjYy1hY2YyLTY5NDdlZDhkZGNlNg==',
                unicefId: 'MSG-22-0004',
                title: 'We hold your back!',
                numberOfRecipients: 2,
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-15T15:01:35.261000+00:00',
                __typename: 'CommunicationMessageNode',
              },
              __typename: 'CommunicationMessageNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'Q29tbXVuaWNhdGlvbk1lc3NhZ2VOb2RlOjQxYjllNTE0LWI1NmMtNDY1OS1hYmFhLWE5ZWYwNzVlOThlMQ==',
                unicefId: 'MSG-22-0003',
                title: 'Hello There!',
                numberOfRecipients: 2,
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-15T14:59:51.410000+00:00',
                __typename: 'CommunicationMessageNode',
              },
              __typename: 'CommunicationMessageNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                id:
                  'Q29tbXVuaWNhdGlvbk1lc3NhZ2VOb2RlOjBkMDQ3NDg0LTUzODAtNGJmMi1hOTViLWM4NjVmNWUzYmM4OQ==',
                unicefId: 'MSG-22-0001',
                title: 'Hello World!',
                numberOfRecipients: 2,
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-15T14:59:16.221000+00:00',
                __typename: 'CommunicationMessageNode',
              },
              __typename: 'CommunicationMessageNodeEdge',
            },
          ],
          __typename: 'CommunicationMessageNodeConnection',
        },
      },
    },
  },
];
