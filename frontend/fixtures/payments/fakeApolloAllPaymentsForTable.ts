import { AllPaymentsForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentsForTable = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOmM2ZWYyMzJjLTgyODEtNGM0Yy05MTdhLTdmMWZkYzhhYTI0Ng==',
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
            endCursor: 'YXJyYXljb25uZWN0aW9uOjI=',
            __typename: 'PageInfo',
          },
          totalCount: 3,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudE5vZGU6Y2VjM2Q0MWQtZDlkYS00ZDE2LThiNTMtMThhMTAxODYyMTA0',
                unicefId: 'RCPT-0060-22-0.000.196',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3YjA1MTRiNC01MWEzLTQ3ZDQtODgwZC1kYWNjZDI3YjhiN2I=',
                  unicefId: 'HH-18-0000.0042',
                  size: 1,
                  admin2: {
                    id:
                      'QXJlYU5vZGU6ZGVjN2MyZWItZDQ4OC00ODRlLWFkNWItNTY3NjVjOTk0YWVk',
                    name: 'Abband',
                    __typename: 'AreaNode',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantityUsd: null,
                currency: 'AFN',
                deliveredQuantity: null,
                deliveredQuantityUsd: null,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6MWZhNzZiOGUtMTNkZi00ODJiLWE4ZGUtYzhkMzYyZmRmYmZm',
                  fullName: 'Daniel Allison',
                  __typename: 'IndividualNode',
                },
                hasPaymentChannel: true,
                financialServiceProvider: null,
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'UGF5bWVudE5vZGU6YWQ5NzU0ZGYtM2YwZC00MmQ2LTlkNGEtN2JmNWVlNGM5Nzcx',
                unicefId: 'RCPT-0060-22-0.000.197',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpkMDM2NjZjNC00MDZkLTQyM2QtOGNlMi01NjBkYmMwMDllODA=',
                  unicefId: 'HH-94-0000.0043',
                  size: 1,
                  admin2: {
                    id:
                      'QXJlYU5vZGU6ZGVjN2MyZWItZDQ4OC00ODRlLWFkNWItNTY3NjVjOTk0YWVk',
                    name: 'Abband',
                    __typename: 'AreaNode',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantityUsd: null,
                currency: 'AFN',
                deliveredQuantity: null,
                deliveredQuantityUsd: null,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6NmVlZmJhMWMtYzQwYi00YjRjLWI0MjItZjNhYzUxMTViNTUx',
                  fullName: 'Tamara Hernandez',
                  __typename: 'IndividualNode',
                },
                hasPaymentChannel: true,
                financialServiceProvider: null,
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'UGF5bWVudE5vZGU6ZmIyYWU5ODYtYzIwYi00NGQzLWE1MWQtMGYzMmQwNWE3MmNk',
                unicefId: 'RCPT-0060-22-0.000.198',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiZTllMmQ1Mi1iNGZiLTQ3YmUtYTE1ZC0yNWRmMTk3NjJhYTQ=',
                  unicefId: 'HH-09-0000.0044',
                  size: 1,
                  admin2: {
                    id:
                      'QXJlYU5vZGU6ZGVjN2MyZWItZDQ4OC00ODRlLWFkNWItNTY3NjVjOTk0YWVk',
                    name: 'Abband',
                    __typename: 'AreaNode',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantityUsd: null,
                currency: 'AFN',
                deliveredQuantity: null,
                deliveredQuantityUsd: null,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6NTFmOGU4NjQtM2ViYy00NzZlLTk5YWQtYWZhYmM1ZTQwMDA5',
                  fullName: 'Kimberly Smith',
                  __typename: 'IndividualNode',
                },
                hasPaymentChannel: true,
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
