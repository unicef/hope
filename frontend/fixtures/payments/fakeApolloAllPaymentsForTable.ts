import { AllPaymentsForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentsForTable = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOjI1ZTNkODA0LTAzMzEtNDhkOC1iYTk2LWVmZjEzYmU3ZDdiYQ==',
        first: 5,
        orderBy: null,
      },
    },
    result: {
      data: {
        allPayments: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: "YXJyYXljb25uZWN0aW9uOjA=",
            endCursor: "YXJyYXljb25uZWN0aW9uOjQ=",
            __typename: "PageInfo"
          },
          edges: [
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjA=",
              node: {
                id: "UGF5bWVudE5vZGU6ZDkwY2JjNTktNGI5Yy00NDQwLWJiOWMtZjI4YWNiOWNkMWEz",
                household: {
                  id: "SG91c2Vob2xkTm9kZTowOWI4YWE2ZC1hOTViLTQ5NWEtYTM0ZS1kMGM0YmQyNWE4Njc=",
                  unicefId: "HH-20-0000.0001",
                  size: 4,
                  admin2: {
                    id: "QXJlYU5vZGU6NzYxZjhkODQtOTljZi00MWExLTk1MmYtMTQ5ZWFhNjJkZDJh",
                    name: "Achin",
                    __typename: "AreaNode"
                  },
                  __typename: "HouseholdNode"
                },
                entitlementQuantityUsd: 4054,
                __typename: "PaymentNode"
              },
              __typename: "PaymentNodeEdge"
            },
          ],
          totalCount: 15,
          edgeCount: 5,
          __typename: "PaymentNodeConnection"
        }
      }
    },
  },
];
