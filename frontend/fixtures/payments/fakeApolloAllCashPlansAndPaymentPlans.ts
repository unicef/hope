import { AllCashPlansAndPaymentPlansDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllCashPlansAndPaymentPlans = [
  {
    request: {
      query: AllCashPlansAndPaymentPlansDocument,
      variables: {
        businessArea: 'afghanistan',
        search: '',
        serviceProvider: '',
        deliveryType: [],
        verificationStatus: [],
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
          totalCount: 32,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                objType: 'CashPlan',
                id:
                  'Q2FzaFBsYW5Ob2RlOmM4NWRhN2ExLTM0YjgtNDc5MS05YjM5LWU4ZGQyOTU3ZTAwNQ==',
                unicefId: 'FTT-22-CSH-00006',
                verificationStatus: 'ACTIVE',
                currency: 'AFN',
                totalDeliveredQuantity: 33061500,
                startDate: '2022-03-14 00:00:00+00:00',
                endDate: '2022-05-31 00:00:00+00:00',
                programmeName:
                  'APMU - Emergency - Winterization - November 2021',
                updatedAt: '2023-08-25 01:00:00.773741+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmM5Zjc5MzRjLTMxOGItNDc3ZS1hNmQ4LWEyZDQwN2EwNzg5ZA==',
                    createdAt: '2023-08-24T07:30:03.925417+00:00',
                    unicefId: 'PVP-183',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: 2133,
                assistanceMeasurement: '',
                totalEntitledQuantity: 33061500,
                totalUndeliveredQuantity: null,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                objType: 'CashPlan',
                id:
                  'Q2FzaFBsYW5Ob2RlOmQwNTQ4ZjE4LTkzNzktNDUzNC05Y2E5LTRmYTkxNGI0OTVhYQ==',
                unicefId: 'FTT-23-CSH-00029',
                verificationStatus: 'FINISHED',
                currency: 'AFN',
                totalDeliveredQuantity: 34979000,
                startDate: '2023-03-15 00:00:00+00:00',
                endDate: '2023-06-30 00:00:00+00:00',
                programmeName: 'Winterization Programme',
                updatedAt: '2023-08-25 01:00:00.767764+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOjkzZGEwYzY4LTcxOTItNGQ2MS1hNDZkLTRlNTVkZjc2Yjk3Yw==',
                    createdAt: '2023-08-24T08:39:43.448362+00:00',
                    unicefId: 'PVP-193',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: 1841,
                assistanceMeasurement: '',
                totalEntitledQuantity: 34979000,
                totalUndeliveredQuantity: null,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                objType: 'CashPlan',
                id:
                  'Q2FzaFBsYW5Ob2RlOjk2MzE0M2Q4LTBiNjUtNGI0Mi05MjkxLWEzNGU3YWQ1ZTc1NQ==',
                unicefId: 'FTT-22-CSH-00009',
                verificationStatus: 'ACTIVE',
                currency: 'AFN',
                totalDeliveredQuantity: 17592500,
                startDate: '2022-03-14 00:00:00+00:00',
                endDate: '2022-04-30 00:00:00+00:00',
                programmeName:
                  'APMU - Emergency - Winterization - November 2021',
                updatedAt: '2023-08-25 01:00:00.761879+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOjIyYWFlZWFlLTllOGYtNDc4Yi1hZWJmLTQ5MjY2NmE3NjIyMA==',
                    createdAt: '2023-08-24T07:40:44.069224+00:00',
                    unicefId: 'PVP-184',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: 1135,
                assistanceMeasurement: '',
                totalEntitledQuantity: 17592500,
                totalUndeliveredQuantity: null,
                dispersionDate: '',
                serviceProviderFullName: '',
                __typename: 'CashPlanAndPaymentPlanNode',
              },
              __typename: 'CashPlanAndPaymentPlanEdges',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                objType: 'CashPlan',
                id:
                  'Q2FzaFBsYW5Ob2RlOjBiM2NkZjQ1LTY2YWMtNDQ5Yy04ZmM0LWVlMmJhNGYwZmE0ZQ==',
                unicefId: 'FTT-22-CSH-00022',
                verificationStatus: 'ACTIVE',
                currency: 'AFN',
                totalDeliveredQuantity: 1272000,
                startDate: '2022-10-01 00:00:00+00:00',
                endDate: '2022-11-15 00:00:00+00:00',
                programmeName: 'PMU CP Winterization Daykundi',
                updatedAt: '2023-08-25 01:00:00.755212+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOjU0ZDk3NzcyLTgwZDktNDBjNi05MGRiLWYwOTdkYTNhOWZmZA==',
                    createdAt: '2023-08-24T08:38:46.757181+00:00',
                    unicefId: 'PVP-190',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: 106,
                assistanceMeasurement: '',
                totalEntitledQuantity: 1272000,
                totalUndeliveredQuantity: null,
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
                  'Q2FzaFBsYW5Ob2RlOjFjNjcyOTNjLWU1NDQtNDQ0OC1hYmUwLTA4NzFlZTA0ZjcxNQ==',
                unicefId: 'FTT-23-CSH-00014',
                verificationStatus: 'FINISHED',
                currency: 'AFN',
                totalDeliveredQuantity: 14098000,
                startDate: '2023-02-06 00:00:00+00:00',
                endDate: '2023-03-31 00:00:00+00:00',
                programmeName: 'Winterization Programme',
                updatedAt: '2023-08-25 01:00:00.749088+00:00',
                verificationPlans: [
                  {
                    id:
                      'UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmExNDZjNzMyLTE2MTUtNDgwZC1hNjAxLTZlMDU2MzIzY2YyZA==',
                    createdAt: '2023-08-24T08:40:00.591181+00:00',
                    unicefId: 'PVP-194',
                    __typename: 'PaymentVerificationPlanNode',
                  },
                ],
                totalNumberOfHouseholds: 742,
                assistanceMeasurement: '',
                totalEntitledQuantity: 14098000,
                totalUndeliveredQuantity: null,
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
