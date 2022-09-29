import { AllCashPlansDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllCashPlansPaymentVerification = [
  {
    request: {
      query: AllCashPlansDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 5,
        orderBy: null,
      },
    },
    result: {
      data: {
        allCashPlans: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            __typename: 'PageInfo',
          },
          totalCount: 6,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'Q2FzaFBsYW5Ob2RlOmNiNzBjYjdmLWY0N2EtNDI5Yy04Y2FjLTk0YzU0MDRiOTFkZA==',
                caId: '123-21-CSH-00003',
                assistanceThrough: '123-21-SRV-00002',
                totalNumberOfHouseholds: 5,
                serviceProvider: null,
                deliveryType: 'Referral',
                startDate: '2020-01-21T01:16:12',
                endDate: '2020-03-22T01:16:12',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6N2RiNzkwMDctMzA3My00ZDU5LWIxYzktNGY2MDQ2ZjM3MmIw',
                  name: 'Picture manage product score five agree.',
                  __typename: 'ProgramNode',
                },
                totalPersonsCovered: 4,
                dispersionDate: '2021-11-03T01:16:12',
                assistanceMeasurement: 'Aruban florin',
                status: 'TRANSACTION_COMPLETED',
                currency: 'AED',
                totalEntitledQuantity: 81968631.29,
                totalDeliveredQuantity: 24029588.26,
                totalUndeliveredQuantity: 53795776.44,
                updatedAt: '2022-02-24T09:56:48.875230',
                // paymentVerificationSummary: {
                //   id:
                //     'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uU3VtbWFyeU5vZGU6NGNhNTdkZDUtYmY4ZC00MGIxLWE3NWEtOTM0Yzg4OTc3ZTM4',
                //   status: 'PENDING',
                //   __typename: 'PaymentVerificationPlanSummaryNode',
                // },
                __typename: 'CashPlanNode',
              },
              __typename: 'CashPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'Q2FzaFBsYW5Ob2RlOjhlNGYwMzYxLTRkNGUtNDZmZC05M2M0LWNiMGExZDA5YjJjMA==',
                caId: '123-21-CSH-00002',
                assistanceThrough: '123-21-SRV-00001',
                totalNumberOfHouseholds: 5,
                serviceProvider: null,
                deliveryType: 'In Kind',
                startDate: '2021-05-15T10:01:49',
                endDate: '2023-12-20T10:01:49',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6N2RiNzkwMDctMzA3My00ZDU5LWIxYzktNGY2MDQ2ZjM3MmIw',
                  name: 'Picture manage product score five agree.',
                  __typename: 'ProgramNode',
                },
                totalPersonsCovered: 2,
                dispersionDate: '2021-09-03T10:01:49',
                assistanceMeasurement: 'Argentine peso',
                status: 'TRANSACTION_COMPLETED',
                currency: 'ARS',
                totalEntitledQuantity: 43776249.87,
                totalDeliveredQuantity: 58957757.27,
                totalUndeliveredQuantity: 65864422.88,
                updatedAt: '2022-02-24T09:56:48.857869',
                paymentVerificationSummary: {
                  id:
                    'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uU3VtbWFyeU5vZGU6YzE1M2FmZmYtNTNmOS00ZDRjLWEyMmUtNTJmNmQ2NzczNjVj',
                  status: 'PENDING',
                  __typename: 'PaymentVerificationPlanSummaryNode',
                },
                __typename: 'CashPlanNode',
              },
              __typename: 'CashPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'Q2FzaFBsYW5Ob2RlOjIxZGZkZDEwLTMwOWMtNDlhYS04ZmQ5LTQ5NTk2ODhmODY2ZA==',
                caId: '123-21-CSH-00001',
                assistanceThrough: '123-21-SRV-00001',
                totalNumberOfHouseholds: 5,
                serviceProvider: null,
                deliveryType: 'Transfer to Account',
                startDate: '2021-02-20T18:59:16',
                endDate: '2021-09-10T18:59:16',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6N2RiNzkwMDctMzA3My00ZDU5LWIxYzktNGY2MDQ2ZjM3MmIw',
                  name: 'Picture manage product score five agree.',
                  __typename: 'ProgramNode',
                },
                totalPersonsCovered: 4,
                dispersionDate: '2022-08-11T18:59:16',
                assistanceMeasurement: 'Guernsey pound',
                status: 'TRANSACTION_COMPLETED_WITH_ERRORS',
                currency: 'LAK',
                totalEntitledQuantity: 81109280.05,
                totalDeliveredQuantity: 13479474.6,
                totalUndeliveredQuantity: 13013349.03,
                updatedAt: '2022-02-24T09:56:48.842605',
                paymentVerificationSummary: {
                  id:
                    'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uU3VtbWFyeU5vZGU6NjZlODU1YmQtZDUxMS00OWEzLTljYWItNGIwMmQ1YzQzYzBk',
                  status: 'PENDING',
                  __typename: 'PaymentVerificationPlanSummaryNode',
                },
                __typename: 'CashPlanNode',
              },
              __typename: 'CashPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'Q2FzaFBsYW5Ob2RlOmY1OWVkNDg1LTA4YTctNGMwYS1hYjRkLTczNzNlZmE3NmE4Ng==',
                caId: '123-21-CSH-00003',
                assistanceThrough: '123-21-SRV-00002',
                totalNumberOfHouseholds: 0,
                serviceProvider: null,
                deliveryType: 'Transfer to Account',
                startDate: '2021-02-11T08:28:15',
                endDate: '2021-09-10T08:28:15',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDBkNWI4MmYtMjRlMy00MDE2LWFhN2EtODNlODE0NjM5Mzcx',
                  name: 'Teacher start pick give dinner story return.',
                  __typename: 'ProgramNode',
                },
                totalPersonsCovered: 1,
                dispersionDate: '2021-12-20T08:28:15',
                assistanceMeasurement: 'Cuban convertible peso',
                status: 'TRANSACTION_COMPLETED',
                currency: null,
                totalEntitledQuantity: 35958176.84,
                totalDeliveredQuantity: 34133204.79,
                totalUndeliveredQuantity: 35280201.96,
                updatedAt: '2022-02-24T09:12:49.386140',
                paymentVerificationSummary: {
                  id:
                    'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uU3VtbWFyeU5vZGU6NjdjN2I3YWYtZDU4Zi00NWFlLTliYmQtNjFlYTA1M2IwOWZh',
                  status: 'PENDING',
                  __typename: 'PaymentVerificationPlanSummaryNode',
                },
                __typename: 'CashPlanNode',
              },
              __typename: 'CashPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                id:
                  'Q2FzaFBsYW5Ob2RlOmRiYzdhNGZiLTUyOTItNDZkZS1hYzIzLTcxMTQ2ZTQzODYwOQ==',
                caId: '123-21-CSH-00002',
                assistanceThrough: '123-21-SRV-00003',
                totalNumberOfHouseholds: 0,
                serviceProvider: null,
                deliveryType: 'Deposit to Card',
                startDate: '2021-08-27T14:10:08',
                endDate: '2022-05-20T14:10:08',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDBkNWI4MmYtMjRlMy00MDE2LWFhN2EtODNlODE0NjM5Mzcx',
                  name: 'Teacher start pick give dinner story return.',
                  __typename: 'ProgramNode',
                },
                totalPersonsCovered: 2,
                dispersionDate: '2022-01-31T14:10:08',
                assistanceMeasurement: 'Sri Lankan rupee',
                status: 'TRANSACTION_COMPLETED_WITH_ERRORS',
                currency: null,
                totalEntitledQuantity: 56247007.42,
                totalDeliveredQuantity: 43876864.16,
                totalUndeliveredQuantity: 88674540.93,
                updatedAt: '2022-02-24T09:12:49.372607',
                paymentVerificationSummary: {
                  id:
                    'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uU3VtbWFyeU5vZGU6NzRlNWU1NzUtYTgyNi00MTgyLThhYWMtN2EyZjVlOTQ5YWY4',
                  status: 'PENDING',
                  __typename: 'PaymentVerificationPlanSummaryNode',
                },
                __typename: 'CashPlanNode',
              },
              __typename: 'CashPlanNodeEdge',
            },
          ],
          __typename: 'CashPlanNodeConnection',
        },
      },
    },
  },
];
