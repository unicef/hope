import { AllCashPlansAndPaymentPlansDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllCashPlansAndPaymentPlans = [
  {
    request: {
      query: AllCashPlansAndPaymentPlansDocument,
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
        allCashPlansAndPaymentPlans: {
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            hasNextPage: true,
            hasPreviousPage: false,
            __typename: 'PageInfoNode',
          },
          totalCount: 7,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                objType: 'PaymentPlan',
                id:
                  'UGF5bWVudFBsYW5Ob2RlOmQ4NDdkZDFlLTkwYmYtNDQzZC1iNWI1LWNiZTcwMDQ5YzYyMA==',
                unicefId: 'PP-0060-23-00000017',
                verificationStatus: 'PENDING',
                currency: 'USD',
                totalDeliveredQuantity: 1000,
                startDate: '2023-07-01 00:00:00+00:00',
                endDate: '2023-07-31 00:00:00+00:00',
                programmeName: 'test_program',
                updatedAt: '2023-06-07 10:40:04.741354+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOjJjMWE5NjQyLWEyYTItNDhiOS1hYTM0LWNjMTA1ODA4ZmI1MQ==',
                    createdAt: '2023-06-13T21:02:41.201531+00:00',
                    unicefId: 'PVP-13',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: null,
                assistanceMeasurement: '',
                totalEntitledQuantity: 2200,
                totalUndeliveredQuantity: 1200,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                objType: 'PaymentPlan',
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjQ4YmU4NzVmLWUxYzMtNDM3OS1iMzc1LTgwMzlkYWU4ODQ5MQ==',
                unicefId: 'PP-0060-23-00000015',
                verificationStatus: 'PENDING',
                currency: 'ALL',
                totalDeliveredQuantity: 2800,
                startDate: '1500-02-04 00:00:00+00:00',
                endDate: '1500-02-05 00:00:00+00:00',
                programmeName: 'Jekub test for spec',
                updatedAt: '2023-05-28 22:40:30.724728+00:00',
                verificationPlans: [],
                totalNumberOfHouseholds: null,
                assistanceMeasurement: '',
                totalEntitledQuantity: 2800,
                totalUndeliveredQuantity: 0,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                objType: 'PaymentPlan',
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjBkNDVlNjQzLTY1YWMtNDIzOS04ZmI5LWIyNzRhNjlmMmE2ZA==',
                unicefId: 'PP-0060-23-00000005',
                verificationStatus: 'ACTIVE',
                currency: 'AUD',
                totalDeliveredQuantity: 150,
                startDate: '2023-04-20 00:00:00+00:00',
                endDate: '2024-04-20 00:00:00+00:00',
                programmeName: 'Test Program',
                updatedAt: '2023-04-21 10:43:49.390111+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmU4NDU3N2IyLWY5YzgtNDgyMS1iY2YzLTY0MWM3Njk4NjM3ZQ==',
                    createdAt: '2023-04-21T10:37:26.578218+00:00',
                    unicefId: 'PVP-11',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmM3N2NiYWZjLWNlYjktNDg2MC1iMTNhLWQzN2EwZGNhZjQzMw==',
                    createdAt: '2023-04-21T10:39:30.886897+00:00',
                    unicefId: 'PVP-12',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: null,
                assistanceMeasurement: '',
                totalEntitledQuantity: 200,
                totalUndeliveredQuantity: 50,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                objType: 'PaymentPlan',
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjc3MDQ1YmUwLTUzOTUtNDdlNy1hZWZiLTYwZjNjNDgxNzE5Zg==',
                unicefId: 'PP-0060-23-00000001',
                verificationStatus: 'ACTIVE',
                currency: 'PLN',
                totalDeliveredQuantity: 600,
                startDate: '2023-03-01 00:00:00+00:00',
                endDate: '2023-03-15 00:00:00+00:00',
                programmeName: 'jkekljeil',
                updatedAt: '2023-04-05 11:04:12.583452+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOjNjMDdiNDk2LTBiMzktNGFiYi1hMWMwLWMyMzVmMGQyNzYwZQ==',
                    createdAt: '2023-04-20T08:26:59.514454+00:00',
                    unicefId: 'PVP-10',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: null,
                assistanceMeasurement: '',
                totalEntitledQuantity: 700,
                totalUndeliveredQuantity: 100,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                objType: 'CashPlan',
                id:
                  'Q2FzaFBsYW5Ob2RlOjk1NGY3OWE3LTdiZDYtNDU5ZS05ZGE4LTQzNjg3ZDY0NjYyNg==',
                unicefId: '123-21-CSH-00003',
                verificationStatus: 'PENDING',
                currency: 'BHD',
                totalDeliveredQuantity: 14923041.29,
                startDate: '2021-07-07 15:22:22+00:00',
                endDate: '2023-05-09 15:22:22+00:00',
                programmeName:
                  'Total western including stay spring western issue.',
                updatedAt: '2023-01-13 15:47:16.805453+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOjNiMDM1MWQxLTdmYTktNDRhOS1iNjA5LTBiZGYyMjE4YmQzYg==',
                    createdAt: '2023-03-22T16:18:00.161858+00:00',
                    unicefId: 'PVP-8',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: 5,
                assistanceMeasurement: '',
                totalEntitledQuantity: 2463289.03,
                totalUndeliveredQuantity: 16301871.34,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
          ],
          __typename: 'PaginatedCashPlanAndPaymentPlanNode',
        },
      },
    },
  },
];
