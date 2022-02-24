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
                  'Q2FzaFBsYW5Ob2RlOjI4N2EwMDA4LWI1NWItNGQ1Ny05MTE4LTFlOWNlYzc5NjM2Mg==',
                caId: '123-21-CSH-00003',
                verificationStatus: 'PENDING',
                assistanceThrough: '123-21-SRV-00001',
                totalNumberOfHouseholds: 5,
                serviceProvider: null,
                deliveryType: 'Cash by FSP',
                startDate: '2020-03-30T19:54:58',
                endDate: '2021-11-05T19:54:58',
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6NTI4OWFkYWUtNGEwNC00MDFlLWJjNDAtZDJiYTNkMGJmMTVk',
                  name: 'Ok serious only reach letter movie.',
                  __typename: 'ProgramNode',
                },
                totalPersonsCovered: 3,
                dispersionDate: '2020-10-13T19:54:58',
                assistanceMeasurement: 'Maldivian rufiyaa',
                status: 'TRANSACTION_COMPLETED',
                currency: 'HKD',
                totalEntitledQuantity: 63528696.08,
                totalDeliveredQuantity: 58615107.8,
                totalUndeliveredQuantity: 81978986.49,
                updatedAt: '2022-02-23T19:48:05.415681',
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
