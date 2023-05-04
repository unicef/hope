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
            endCursor: 'YXJyYXljb25uZWN0aW9uOjI=',
            __typename: 'PageInfo',
          },
          totalCount: 3,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjZmOTIxYmFlLTljODktNGRkYy1iNTRjLTI4Mzc3ZTA2YjUwNg==',
                unicefId: 'PP-0060-23-00000041',
                isFollowUp: true,
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
                startDate: '2023-05-04',
                endDate: '2023-06-03',
                dispersionStartDate: '2023-05-04',
                dispersionEndDate: '2023-05-18',
                femaleChildrenCount: 0,
                femaleAdultsCount: 2,
                maleChildrenCount: 0,
                maleAdultsCount: 6,
                totalHouseholdsCount: 1,
                totalIndividualsCount: 8,
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
                  'UGF5bWVudFBsYW5Ob2RlOjQxZTUwYmE1LTM3MDgtNGIyNS1iYjRjLTk0ZGNiY2JjMTVlNQ==',
                unicefId: 'PP-0060-22-11223344',
                isFollowUp: false,
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
                startDate: '2023-05-04',
                endDate: '2023-06-03',
                dispersionStartDate: '2023-05-04',
                dispersionEndDate: '2023-05-18',
                femaleChildrenCount: 0,
                femaleAdultsCount: 13,
                maleChildrenCount: 0,
                maleAdultsCount: 20,
                totalHouseholdsCount: 5,
                totalIndividualsCount: 33,
                totalEntitledQuantity: null,
                totalDeliveredQuantity: 999,
                totalUndeliveredQuantity: null,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjAwMDAwMDAwLWZlZWQtYmVlZi0wMDAwLTAwMDAwYmFkZjAwZA==',
                unicefId: 'PP-0060-23-00000039',
                isFollowUp: false,
                status: 'OPEN',
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
                startDate: '2023-05-04',
                endDate: '2023-06-03',
                dispersionStartDate: '2023-05-04',
                dispersionEndDate: '2023-05-18',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 0,
                maleAdultsCount: 2,
                totalHouseholdsCount: 2,
                totalIndividualsCount: 2,
                totalEntitledQuantity: null,
                totalDeliveredQuantity: null,
                totalUndeliveredQuantity: null,
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
