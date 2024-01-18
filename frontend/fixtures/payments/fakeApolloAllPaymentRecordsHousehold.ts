import { AllPaymentRecordsAndPaymentsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentRecordsHousehold = [
  {
    request: {
      query: AllPaymentRecordsAndPaymentsDocument,
      variables: {
        household:
          'SG91c2Vob2xkTm9kZTphYTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDE=',
        businessArea: 'afghanistan',
        first: 5,
        orderBy: null,
      },
    },
    result: {
      data: {
        allPaymentRecordsAndPayments: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjI=',
            __typename: 'PageInfoNode',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                objType: 'PaymentRecord',
                id:
                  'UGF5bWVudFJlY29yZE5vZGU6Y2JkMjU1MjctNTIwNS00Mjk5LWFiYmYtYTZjYTgzNzEyYjk1',
                fullName: 'Ashley Reid',
                status: 'TRANSACTION_SUCCESSFUL',
                caId: '123-21-PR-00008',
                currency: 'AZN',
                entitlementQuantity: 303.41,
                deliveredQuantity: 92,
                deliveredQuantityUsd: 264,
                deliveryDate: '2023-03-01 22:21:20+00:00',
                parent: {
                  id:
                    'Q2FzaFBsYW5Ob2RlOjMwMTY0M2ZjLTQwMGItNGY5MS1iZDg1LTFiNTAyZTMxZmMzMg==',
                  programName: 'Test Program',
                  __typename: 'CashPlanAndPaymentPlanNode',
                },
                verification: null,
                __typename: 'PaymentRecordAndPaymentNode',
              },
              __typename: 'PaymentRecordsAndPaymentsEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                objType: 'PaymentRecord',
                id:
                  'UGF5bWVudFJlY29yZE5vZGU6YThhNzdkZTEtNWYxZi00MzBjLWJlOGMtODVhNzkzNjJiMzZm',
                fullName: 'Arthur Fletcher',
                status: 'PARTIALLY_DISTRIBUTED',
                caId: '123-21-PR-00004',
                currency: 'COP',
                entitlementQuantity: 6091.99,
                deliveredQuantity: 3177,
                deliveredQuantityUsd: 5491,
                deliveryDate: '2021-07-31 06:52:41+00:00',
                parent: {
                  id:
                    'Q2FzaFBsYW5Ob2RlOmQzMDI1MDRhLWQzZjMtNGE2MC05Nzg5LTBhNGVjMGI0N2M4Mw==',
                  programName: 'Test Program',
                  __typename: 'CashPlanAndPaymentPlanNode',
                },
                verification: null,
                __typename: 'PaymentRecordAndPaymentNode',
              },
              __typename: 'PaymentRecordsAndPaymentsEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                objType: 'Payment',
                id:
                  'UGF5bWVudE5vZGU6MTAwMDAwMDAtZmVlZC1iZWVmLTAwMDAtMDAwMDBiYWRmMDBk',
                fullName: 'Jan Kowalski',
                status: 'PENDING',
                caId: 'RCPT-0060-24-0.000.001',
                currency: 'USD',
                entitlementQuantity: null,
                deliveredQuantity: null,
                deliveredQuantityUsd: null,
                deliveryDate: null,
                parent: {
                  id:
                    'UGF5bWVudFBsYW5Ob2RlOjAwMDAwMDAwLWZlZWQtYmVlZi0wMDAwLTAwMDAwYmFkZjAwZA==',
                  programName: 'Test Program',
                  __typename: 'CashPlanAndPaymentPlanNode',
                },
                verification: null,
                __typename: 'PaymentRecordAndPaymentNode',
              },
              __typename: 'PaymentRecordsAndPaymentsEdges',
            },
          ],
          totalCount: 3,
          __typename: 'PaginatedPaymentRecordsAndPaymentsNode',
        },
      },
    },
  },
];
