import { AllPaymentsForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentsForTable = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOmU3NjE4MzA4LTgyYmQtNDAxYi1iNjkzLTAyZGRlZGU3MmY2NQ==',
        first: 10,
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
            endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          totalCount: 1,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudE5vZGU6NWU0ZjRiNDEtMjFkMS00ZDFiLWEzMzEtZjkyZTBlOGZmMjU4',
                unicefId: 'RCPT-0060-23-0.000.010',
                status: 'PENDING',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTozMGIwMjQ2YS05YzA5LTQzMTktYWI5MS1lYjU3MTE1NTljM2M=',
                  unicefId: 'HH-23-0000.0012',
                  size: 5,
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                entitlementQuantity: 2123,
                entitlementQuantityUsd: 2123,
                currency: 'USD',
                deliveredQuantity: null,
                deliveredQuantityUsd: null,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6OGVmYTVjZmUtNzkxOC00MDU0LTk3YWMtMWQ0YzYzMDhjYjM1',
                  fullName: 'John Latoya Smith',
                  __typename: 'IndividualNode',
                },
                financialServiceProvider: null,
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
