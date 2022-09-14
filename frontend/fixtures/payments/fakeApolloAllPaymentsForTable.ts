import { AllPaymentsForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentsForTable = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOjFmN2U5NmRkLTJmNDAtNDllNC04NzUyLTRjMzRjMGNiOGVjZQ==',
        first: 5,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allPayments: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            __typename: 'PageInfo',
          },
          totalCount: 2,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudE5vZGU6ZDUyYjMxZjktZTk5ZS00YjEyLTgwNjUtZTQ0MGExOTYzZTll',
                unicefId: 'RCPT-0060-22-0.000.001',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZToyMDA3NzQ5OC04MGYwLTQ2MmEtODJlNi04NjZjZWY5MmQwNmE=',
                  unicefId: 'HH-20-0000.0001',
                  size: 4,
                  admin2: {
                    id:
                      'QXJlYU5vZGU6Y2JmYzhmZTMtZDg5Ny00ODg0LTk5NGItN2YxZjQ0ZTE0ZDEx',
                    name: 'Achin',
                    __typename: 'AreaNode',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantityUsd: 78,
                currency: 'WST',
                deliveredQuantity: 631,
                deliveredQuantityUsd: 242,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6ZTc3NTM5NDEtYjU1Ny00NzhmLTgxYjMtOWRiN2QxOGZjNjIz',
                  fullName: 'Agata Kowalska',
                  __typename: 'IndividualNode',
                },
                hasPaymentChannel: true,
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'UGF5bWVudE5vZGU6MzgzMmQyNmUtY2NjNS00MGQ2LTlkMDItOTFjMDA4NDEzOTY4',
                unicefId: 'RCPT-0060-22-0.000.002',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTozZGIyNzI5ZS03MjU5LTRiMTMtODNiMi0zMDkwZDg0N2U1Y2M=',
                  unicefId: 'HH-20-0000.0002',
                  size: 4,
                  admin2: {
                    id:
                      'QXJlYU5vZGU6ZGVjN2MyZWItZDQ4OC00ODRlLWFkNWItNTY3NjVjOTk0YWVk',
                    name: 'Abband',
                    __typename: 'AreaNode',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantityUsd: 2693,
                currency: 'HTG',
                deliveredQuantity: 3703,
                deliveredQuantityUsd: 3515,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6YmM1YTViMjAtNzRhNC00ZDQ4LWFiNjMtOTlhMGM5MTM4NTBk',
                  fullName: 'Jan Romaniak',
                  __typename: 'IndividualNode',
                },
                hasPaymentChannel: true,
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
          ],
          __typename: 'PaymentNodeConnection',
        },
      },
    },
  },
];
