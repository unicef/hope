import { AllPaymentRecordsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentRecords = [
  {
    request: {
      query: AllPaymentRecordsDocument,
      variables: {
        cashPlan:
          'Q2FzaFBsYW5Ob2RlOjI1ZTNkODA0LTAzMzEtNDhkOC1iYTk2LWVmZjEzYmU3ZDdiYQ==',
        businessArea: 'afghanistan',
        first: 5,
        orderBy: null,
      },
    },
    result: {
      data: {
        allPaymentRecords: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudFJlY29yZE5vZGU6NWEyZmE4NWYtNTM4YS00M2VjLWEwZTItMzM4ZTBmZDNlODQ1',
                createdAt: '2021-07-22T11:52:58.791297',
                updatedAt: '2021-07-22T11:52:58.791308',
                fullName: 'Mr. Miguel Conner',
                statusDate: '2020-07-25T11:37:23',
                status: 'DISTRIBUTION_SUCCESSFUL',
                caId: '123-21-PR-00006',
                totalPersonsCovered: 2,
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo1YmQ0ODJjMS0zMmYzLTRjZDEtODZlNi0xNTdhMzdmYjBkZWQ=',
                  unicefId: 'HH-21-0000.0025',
                  size: 7,
                  __typename: 'HouseholdNode',
                },
                headOfHousehold: null,
                currency: 'TMT',
                entitlementQuantity: 3683.4,
                deliveredQuantity: 3326.0,
                deliveredQuantityUsd: 1694.0,
                deliveryDate: '2021-01-11T17:05:53',
                parent: {
                  id:
                    'Q2FzaFBsYW5Ob2RlOjViZWQ0OTUyLTMyNmItNDgxNS04MjA5LTBmOGNmYjIyMTc2NA==',
                  program: {
                    id:
                      'UHJvZ3JhbU5vZGU6ZDM4YWI4MTQtOTQyNy00ZmJkLTg4ODctOGUyYzlkMzcxYjg2',
                    name: 'Notice hair fall college enough perhaps.',
                    __typename: 'ProgramNode',
                  },
                  __typename: 'CashPlanNode',
                },
                __typename: 'PaymentRecordNode',
              },
              __typename: 'PaymentRecordNodeEdge',
            },
          ],
          totalCount: 5,
          edgeCount: 5,
          __typename: 'PaymentRecordNodeConnection',
        },
      },
    },
  },
];
