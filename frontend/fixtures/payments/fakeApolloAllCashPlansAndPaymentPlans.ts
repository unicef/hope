import { AllCashPlansAndPaymentPlansDocument, AllCashPlansAndPaymentPlansQueryVariables, AllCashPlansAndPaymentPlansQuery } from '../../src/__generated__/graphql';

export const fakeApolloAllCashPlansAndPaymentPlans = [
  {
    request: {
      query: AllCashPlansAndPaymentPlansDocument,
      variables: {
        businessArea: 'afghanistan',
        program: null,
        search: '',
        first: 5,
        serviceProvider: null,
        deliveryType: null,
        verificationStatus: null,
        startDateGte: null,
        endDateLte: null,
        orderBy: null,
        last: null,
        before: null,
        after: null,
      } as AllCashPlansAndPaymentPlansQueryVariables,
    },
    result: {
      data: {
        allCashPlansAndPaymentPlans: {
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            hasNextPage: true,
            hasPreviousPage: false,
          },
          totalCount: 4,
          edges: [
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjA=",
              node: {
                objType: "PaymentPlan",
                id: "UGF5bWVudFBsYW5Ob2RlOmIyNTYzN2VjLWNkYmUtNDEzMC04N2JlLWU1OGIzYzcxMDdkMg==",
                unicefId: "PP-0060-22-11223344",
                verificationStatus: "ACTIVE",
                currency: "USD",
                totalDeliveredQuantity: 999,
                startDate: "2022-10-26 08:15:09.816535+00:00",
                endDate: "2022-11-25 08:15:09.816535+00:00",
                programmeName: "Test Program",
                updatedAt: "2022-10-26 08:15:09.845202+00:00",
                verificationPlans: [
                  {
                    id: "UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmQ1YWVmZjE1LWQ0ZDAtNGE0YS1hMzIzLWNlMGMwOTM2MzU3Ng==",
                    createdAt: "2022-10-26T08:15:09.851087+00:00",
                    unicefId: "PVP-1"
                  }
                ],
                totalNumberOfHouseholds: null,
                assistanceMeasurement: "HH",
                totalEntitledQuantity: null,
                totalUndeliveredQuantity: null,
                dispersionDate: "",
                serviceProviderFullName: ""
              }
            },
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjE=",
              node: {
                objType: "CashPlan",
                id: "Q2FzaFBsYW5Ob2RlOmZiY2MxZDY4LWU1YzUtNGM3ZC05ZjA3LTRkZGU4NjU4NTU3Yg==",
                unicefId: "123-21-CSH-00003",
                verificationStatus: "PENDING",
                currency: "KWD",
                totalDeliveredQuantity: 71007093.19,
                startDate: "2020-08-10 23:41:14+00:00",
                endDate: "2021-12-26 23:41:14+00:00",
                programmeName: "Skin can laugh experience.",
                updatedAt: "2022-10-26 08:15:08.781020+00:00",
                verificationPlans: [],
                totalNumberOfHouseholds: 5,
                assistanceMeasurement: "HH",
                totalEntitledQuantity: 60422683.87,
                totalUndeliveredQuantity: 45476368.48,
                dispersionDate: "",
                serviceProviderFullName: ""
              }
            },
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjI=",
              node: {
                objType: "CashPlan",
                id: "Q2FzaFBsYW5Ob2RlOmE3NmNjNTRhLWE5YWMtNDgyNS05OTg5LTk1ZTYwMTUwODE0MA==",
                unicefId: "123-21-CSH-00002",
                verificationStatus: "PENDING",
                currency: "CDF",
                totalDeliveredQuantity: 18271344.05,
                startDate: "2022-03-18 16:08:14+00:00",
                endDate: "2024-06-02 16:08:14+00:00",
                programmeName: "Skin can laugh experience.",
                updatedAt: "2022-10-26 08:15:08.764013+00:00",
                verificationPlans: [],
                totalNumberOfHouseholds: 5,
                assistanceMeasurement: "HH",
                totalEntitledQuantity: 40010736.01,
                totalUndeliveredQuantity: 18320390.85,
                dispersionDate: "",
                serviceProviderFullName: ""
              }
            },
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjM=",
              node: {
                objType: "CashPlan",
                id: "Q2FzaFBsYW5Ob2RlOjE3MWMzOWYxLTI3Y2EtNDQ2Zi05OGMyLWNlYjRiMWY2YjhjZg==",
                unicefId: "123-21-CSH-00001",
                verificationStatus: "PENDING",
                currency: "BZD",
                totalDeliveredQuantity: 37836624.22,
                startDate: "2020-04-20 20:23:11+00:00",
                endDate: "2021-04-08 20:23:11+00:00",
                programmeName: "Skin can laugh experience.",
                updatedAt: "2022-10-26 08:15:08.743046+00:00",
                verificationPlans: [],
                totalNumberOfHouseholds: 5,
                assistanceMeasurement: "HH",
                totalEntitledQuantity: 49925970.55,
                totalUndeliveredQuantity: 43002539.53,
                dispersionDate: "",
                serviceProviderFullName: ""
              }
            }
          ],
        },
      } as AllCashPlansAndPaymentPlansQuery,
    },
  },
];
