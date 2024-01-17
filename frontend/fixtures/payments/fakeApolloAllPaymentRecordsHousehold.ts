import { AllPaymentRecordsAndPaymentsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentRecordsHousehold = [
  {
    request: {
      query: AllPaymentRecordsAndPaymentsDocument,
      variables: {
        household:
          'SG91c2Vob2xkTm9kZTo3NjExNzM2Ny0yYWFiLTRmNTEtODUwOC1mMzBmODliYWUzYzE=',
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
                  'UGF5bWVudFJlY29yZE5vZGU6OTljYTYxY2EtMzRmNS00OGFjLWIzMzItZTA4YzY4ZWU0NGNj',
                fullName: 'Alyssa Davis',
                status: 'TRANSACTION_ERRONEOUS',
                caId: '123-21-PR-00009',
                currency: 'GNF',
                entitlementQuantity: 8581.3,
                deliveredQuantity: 4659,
                deliveredQuantityUsd: 2963,
                deliveryDate: '2022-01-07 14:15:18+00:00',
                parent: {
                  id:
                    'Q2FzaFBsYW5Ob2RlOmY1MTQyYzZiLWZjNzAtNGEzMC1hNjRlLTAyNzhkZTI5ZDMwMA==',
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
                  'UGF5bWVudFJlY29yZE5vZGU6NGRmMjhlZWEtMjhjMC00Mzk2LTk2Y2MtZDMzOGU4Yzk0ZDE5',
                fullName: 'Jesse Reynolds',
                status: 'TRANSACTION_SUCCESSFUL',
                caId: '123-21-PR-00002',
                currency: 'AED',
                entitlementQuantity: 3562.5,
                deliveredQuantity: 2833,
                deliveredQuantityUsd: 2418,
                deliveryDate: '2023-07-10 19:16:41+00:00',
                parent: {
                  id:
                    'Q2FzaFBsYW5Ob2RlOmY2MzkxZDVhLTgyZmMtNGMyYi04ZTM0LWRmZDQ2NmRkZDhhMg==',
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
                caId: 'RCPT-0060-23-0.000.043',
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
