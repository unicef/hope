import { AllCashPlansDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllCashPlans = [
  {
    request: {
      query: AllCashPlansDocument,
      variables: {
        program:
          'UHJvZ3JhbU5vZGU6YzRkNTY1N2QtMWEyOS00NmUxLTgxOTAtZGY3Zjg1YTBkMmVm',
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
          totalCount: 1,
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
                paymentVerificationSummary: {
                  edges: [
                    {
                      cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
                      node: {
                        id:
                          'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uU3VtbWFyeU5vZGU6NGNhNTdkZDUtYmY4ZC00MGIxLWE3NWEtOTM0Yzg4OTc3ZTM4',
                        status: 'PENDING',
                        __typename: 'PaymentVerificationPlanSummaryNode',
                      },
                      __typename: 'PaymentVerificationPlanSummaryEdge',
                    },
                  ],
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
