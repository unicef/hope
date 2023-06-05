import { AllPaymentPlansForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentPlansForTable = [
  {
    request: {
      query: AllPaymentPlansForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 5,
        orderBy: '-created_at',
        isFollowUp: null,
      },
    },
    result: {
      data: {
        allPaymentPlans: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjM=',
            __typename: 'PageInfo',
          },
          totalCount: 4,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOmU3NjE4MzA4LTgyYmQtNDAxYi1iNjkzLTAyZGRlZGU3MmY2NQ==',
                unicefId: 'PP-0060-23-00000004',
                isFollowUp: true,
                followUps: {
                  totalCount: 0,
                  edges: [],
                  __typename: 'PaymentPlanNodeConnection',
                },
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
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMTIz',
                  name: 'Test Target Population',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'USD',
                currencyName: 'United States dollar',
                startDate: '2023-05-12',
                endDate: '2023-06-11',
                dispersionStartDate: '2023-05-12',
                dispersionEndDate: '2023-05-17',
                femaleChildrenCount: 0,
                femaleAdultsCount: 3,
                maleChildrenCount: 0,
                maleAdultsCount: 2,
                totalHouseholdsCount: 1,
                totalIndividualsCount: 5,
                totalEntitledQuantity: 2123,
                totalDeliveredQuantity: 0,
                totalUndeliveredQuantity: 2123,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjI1ODY3MDQwLWIzOWQtNDhjMS04MDdlLTZmZjYzMzE0MzA2YQ==',
                unicefId: 'PP-0060-23-00000003',
                isFollowUp: true,
                followUps: {
                  totalCount: 0,
                  edges: [],
                  __typename: 'PaymentPlanNodeConnection',
                },
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
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMTIz',
                  name: 'Test Target Population',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'USD',
                currencyName: 'United States dollar',
                startDate: '2023-05-12',
                endDate: '2023-06-11',
                dispersionStartDate: '2023-05-12',
                dispersionEndDate: '2023-05-24',
                femaleChildrenCount: 0,
                femaleAdultsCount: 4,
                maleChildrenCount: 0,
                maleAdultsCount: 0,
                totalHouseholdsCount: 1,
                totalIndividualsCount: 4,
                totalEntitledQuantity: 1546,
                totalDeliveredQuantity: 0,
                totalUndeliveredQuantity: 1546,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjA4ZWYzNGUwLThmNzYtNDRmOC1hMDRiLWY5NjQ0OTdmZDY3ZQ==',
                unicefId: 'PP-0060-22-11223344',
                isFollowUp: false,
                followUps: {
                  totalCount: 2,
                  edges: [
                    {
                      node: {
                        id:
                          'UGF5bWVudFBsYW5Ob2RlOjI1ODY3MDQwLWIzOWQtNDhjMS04MDdlLTZmZjYzMzE0MzA2YQ==',
                        unicefId: 'PP-0060-23-00000003',
                        __typename: 'PaymentPlanNode',
                      },
                      __typename: 'PaymentPlanNodeEdge',
                    },
                    {
                      node: {
                        id:
                          'UGF5bWVudFBsYW5Ob2RlOmU3NjE4MzA4LTgyYmQtNDAxYi1iNjkzLTAyZGRlZGU3MmY2NQ==',
                        unicefId: 'PP-0060-23-00000004',
                        __typename: 'PaymentPlanNode',
                      },
                      __typename: 'PaymentPlanNodeEdge',
                    },
                  ],
                  __typename: 'PaymentPlanNodeConnection',
                },
                status: 'FINISHED',
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
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMTIz',
                  name: 'Test Target Population',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'USD',
                currencyName: 'United States dollar',
                startDate: '2023-05-12',
                endDate: '2023-06-11',
                dispersionStartDate: '2023-05-12',
                dispersionEndDate: '2023-05-26',
                femaleChildrenCount: 0,
                femaleAdultsCount: 14,
                maleChildrenCount: 0,
                maleAdultsCount: 14,
                totalHouseholdsCount: 5,
                totalIndividualsCount: 28,
                totalEntitledQuantity: null,
                totalDeliveredQuantity: 999,
                totalUndeliveredQuantity: null,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjAwMDAwMDAwLWZlZWQtYmVlZi0wMDAwLTAwMDAwYmFkZjAwZA==',
                unicefId: 'PP-0060-23-00000001',
                isFollowUp: false,
                followUps: {
                  totalCount: 0,
                  edges: [],
                  __typename: 'PaymentPlanNodeConnection',
                },
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
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMTIz',
                  name: 'Test Target Population',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'USD',
                currencyName: 'United States dollar',
                startDate: '2023-05-12',
                endDate: '2023-06-11',
                dispersionStartDate: '2023-05-12',
                dispersionEndDate: '2023-05-26',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 0,
                maleAdultsCount: 2,
                totalHouseholdsCount: 2,
                totalIndividualsCount: 2,
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
