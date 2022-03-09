import { AllCashPlansDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllCashPlansPaymentVerification = [
  {
    request: {
      query: AllCashPlansDocument,
      variables: { businessArea: 'afghanistan', first: 5, orderBy: null },
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
          totalCount: 22,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'Q2FzaFBsYW5Ob2RlOjViZWQ0OTUyLTMyNmItNDgxNS04MjA5LTBmOGNmYjIyMTc2NA==',
                caId: '123-21-CSH-00002',
                verificationStatus: 'FINISHED',
                assistanceThrough: 'dfea92a6-b415-43dc-8407-6000b6ab33f6',
                totalNumberOfHouseholds: 5,
                serviceProvider: null,
                deliveryType: 'Mobile Money',
                startDate: '2021-01-11T13:27:23',
                endDate: '2022-05-31T13:27:23',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6ZDM4YWI4MTQtOTQyNy00ZmJkLTg4ODctOGUyYzlkMzcxYjg2',
                  name: 'Notice hair fall college enough perhaps.',
                  __typename: 'ProgramNode',
                },
                totalPersonsCovered: 2,
                dispersionDate: '2021-04-26T13:27:23',
                assistanceMeasurement: 'Zambian kwacha',
                status: 'TRANSACTION_COMPLETED',
                currency: 'KES',
                totalEntitledQuantity: 50116186.49,
                totalDeliveredQuantity: 56371986.28,
                totalUndeliveredQuantity: 63934749.59,
                updatedAt: '2022-01-14T09:45:25.992870',
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
