import { AllPaymentPlansForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentPlansForTable = [
  {
    request: {
      query: AllPaymentPlansForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 5,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allPaymentPlans: {
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
                  'UGF5bWVudFBsYW5Ob2RlOmM2ZWYyMzJjLTgyODEtNGM0Yy05MTdhLTdmMWZkYzhhYTI0Ng==',
                unicefId: 'PP-0060-22-00000010',
                status: 'ACCEPTED',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OGE5ZmRkMWMtZDlkNi00NTNmLWIzNzgtMzExYzI4YmM2Mzdk',
                  name: 'test program 1663138001318',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6OTIwMWUxOWYtYmIxNy00ZWY0LWI3NzktNzdiMDZmMDlmM2Uw',
                  name: 'test TP 1663138001318',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'AFN',
                currencyName: 'Afghan afghani',
                startDate: '2022-12-12',
                endDate: '2022-12-23',
                dispersionStartDate: '2023-12-12',
                dispersionEndDate: '2023-12-23',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 1,
                maleAdultsCount: 2,
                totalHouseholdsCount: 3,
                totalIndividualsCount: 3,
                totalEntitledQuantity: 0,
                totalDeliveredQuantity: 0,
                totalUndeliveredQuantity: 0,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOmJhN2NhOWJkLWYyZDctNGY5Mi04NjdlLWUyMzM1OWE2ZGVmOQ==',
                unicefId: 'PP-0060-22-00000009',
                status: 'LOCKED_FSP',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6Y2NhNzM1ODItYjVjMy00MjA3LWJhNzEtMDA4NjYwMWYwYTEx',
                  name: 'test program 1663078722963',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6NDIxYmRiNzItYTIzZC00ZDk5LTk4ZTAtYWYxZTg3MTM5YzM1',
                  name: 'test TP 1663078722963',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'AFN',
                currencyName: 'Afghan afghani',
                startDate: '2022-12-12',
                endDate: '2022-12-23',
                dispersionStartDate: '2023-12-12',
                dispersionEndDate: '2023-12-23',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 2,
                maleAdultsCount: 1,
                totalHouseholdsCount: 3,
                totalIndividualsCount: 3,
                totalEntitledQuantity: 0,
                totalDeliveredQuantity: 0,
                totalUndeliveredQuantity: 0,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOmY0YTBlNDhlLTIxZTktNDkxYy05ZTRlLWJjZmU2YWVmYWY4ZQ==',
                unicefId: 'PP-0060-22-00000008',
                status: 'LOCKED',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6OGE3YWFiMWMtNTBjZC00NjkxLThlZTAtOTY1NDJiZjY0YjMw',
                  name: 'test program 1663078308581',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6YWQxMWY5NTQtMzNmNS00MzllLTgwYzktNzk3NWU2ZjJkZjkz',
                  name: 'test TP 1663078308581',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'AFN',
                currencyName: 'Afghan afghani',
                startDate: '2022-12-12',
                endDate: '2022-12-23',
                dispersionStartDate: '2023-12-12',
                dispersionEndDate: '2023-12-23',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 1,
                maleAdultsCount: 2,
                totalHouseholdsCount: 3,
                totalIndividualsCount: 3,
                totalEntitledQuantity: 0,
                totalDeliveredQuantity: 0,
                totalUndeliveredQuantity: 0,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjM5ZWU0NjFkLWQyYjktNDMxNi05OGM4LTkzMTc2MDE2MDYzZA==',
                unicefId: 'PP-0060-22-00000007',
                status: 'LOCKED',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6ZWQyMTFlNWUtM2ZlZC00YzhjLTg5NmMtMzYyYWEzMjE5MTRj',
                  name: 'test program 1663077997178',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6OTM3NWNkOWQtYjZiYy00MWRlLWJmYzYtYTczNGViNjc4OWRl',
                  name: 'test TP 1663077997178',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'AFN',
                currencyName: 'Afghan afghani',
                startDate: '2022-12-12',
                endDate: '2022-12-23',
                dispersionStartDate: '2023-12-12',
                dispersionEndDate: '2023-12-23',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 2,
                maleAdultsCount: 1,
                totalHouseholdsCount: 3,
                totalIndividualsCount: 3,
                totalEntitledQuantity: 0,
                totalDeliveredQuantity: 0,
                totalUndeliveredQuantity: 0,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOmQ2ZjAxOGY3LWQwNTYtNGQ0Zi04NzVkLWRkMDIxMjEyYzc0Nw==',
                unicefId: 'PP-0060-22-00000006',
                status: 'LOCKED',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6N2E5NTViYTAtZjgzNy00YWJkLTg1YjctMTI1Nzc3YjAzZjMx',
                  name: 'test program 1663077520870',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZTg3YjcyMGUtMWZkYS00MjJlLTkxYTctYzZmMzhiNWJkOGMw',
                  name: 'test TP 1663077520870',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'AFN',
                currencyName: 'Afghan afghani',
                startDate: '2022-12-12',
                endDate: '2022-12-23',
                dispersionStartDate: '2023-12-12',
                dispersionEndDate: '2023-12-23',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 18,
                maleAdultsCount: 17,
                totalHouseholdsCount: 35,
                totalIndividualsCount: 35,
                totalEntitledQuantity: 0,
                totalDeliveredQuantity: 0,
                totalUndeliveredQuantity: 0,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
          ],
          __typename: 'PaymentPlanNodeConnection',
        },
      },
    },
  },
];
