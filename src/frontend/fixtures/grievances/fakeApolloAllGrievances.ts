import { AllGrievanceTicketDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllGrievances = [
  {
    request: {
      query: AllGrievanceTicketDocument,
      variables: {
        household: 'HH-20-0000.0001',
        businessArea: 'afghanistan',
      },
    },
    result: {
      data: {
        allGrievanceTicket: {
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
                  'R3JpZXZhbmNlVGlja2V0Tm9kZTplYzBkNDEwZi1kMTE1LTQ2OGYtYWI5Ni0wOGQ5NzM4ODUyYjA=',
                status: 2,
                assignedTo: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  __typename: 'UserNode',
                },
                category: 5,
                issueType: null,
                createdAt: '2022-06-30T09:25:42.661116',
                userModified: '2022-06-30T09:25:42.658121',
                admin: null,
                household: {
                  unicefId: 'HH-20-0000.0001',
                  id:
                    'SG91c2Vob2xkTm9kZTowOWI4YWE2ZC1hOTViLTQ5NWEtYTM0ZS1kMGM0YmQyNWE4Njc=',
                  __typename: 'HouseholdNode',
                },
                unicefId: 'GRV-000005',
                existingTickets: [],
                relatedTickets: [],
                __typename: 'GrievanceTicketNode',
              },
              __typename: 'GrievanceTicketNodeEdge',
            },
          ],
          __typename: 'GrievanceTicketNodeConnection',
        },
      },
    },
  },
];
