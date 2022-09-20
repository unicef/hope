import { AllCommunicationMessagesDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllCommunicationMessages = [
  {
    request: {
      query: AllCommunicationMessagesDocument,
      variables: {
        createdAtRange: '',
        targetPopulation: '',
        createdBy: '',
        businessArea: 'afghanistan',
        first: 10,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allCommunicationMessages: {
          totalCount: 4,
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjM=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'TWVzc2FnZU5vZGU6NzU4YmIyODQtMmNmMC00ZmNjLWFjZjItNjk0N2VkOGRkY2U2',
                unicefId: 'MSG-22-0004',
                title: 'We hold your back!',
                numberOfRecipients: 2,
                createdBy: {
                  firstName: 'VARUN',
                  lastName: 'GANDE',
                  id:
                    'VXNlck5vZGU6YTg4NGUyMzctNzBiNy00ZDFkLTgzYmYtNGRmY2QyMGM1MmMz',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-15T15:01:35.261000+00:00',
                __typename: 'MessageNode',
              },
              __typename: 'MessageNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'TWVzc2FnZU5vZGU6NDFiOWU1MTQtYjU2Yy00NjU5LWFiYWEtYTllZjA3NWU5OGUx',
                unicefId: 'MSG-22-0003',
                title: 'Hello There!',
                numberOfRecipients: 2,
                createdBy: {
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-15T14:59:51.410000+00:00',
                __typename: 'MessageNode',
              },
              __typename: 'MessageNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'TWVzc2FnZU5vZGU6MTE3NWYzMzAtMzZjYy00Mzk0LTgyMDItZTg2NjdlMjllNzgw',
                unicefId: 'MSG-22-0002',
                title: 'You got credit of USD 200',
                numberOfRecipients: 2,
                createdBy: {
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-16T08:33:09.955000+00:00',
                __typename: 'MessageNode',
              },
              __typename: 'MessageNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'TWVzc2FnZU5vZGU6MGQwNDc0ODQtNTM4MC00YmYyLWE5NWItYzg2NWY1ZTNiYzg5',
                unicefId: 'MSG-22-0001',
                title: 'Hello World!',
                numberOfRecipients: 2,
                createdBy: {
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  __typename: 'UserNode',
                },
                createdAt: '2022-09-15T14:59:16.221000+00:00',
                __typename: 'MessageNode',
              },
              __typename: 'MessageNodeEdge',
            },
          ],
          __typename: 'MessageNodeConnection',
        },
      },
    },
  },
];
