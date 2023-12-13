import { AllPaymentPlansForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentPlansForTable = [
  {
    request: {
      query: AllPaymentPlansForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        search: '',
        status: [],
        totalEntitledQuantityFrom: null,
        totalEntitledQuantityTo: null,
        dispersionStartDate: null,
        dispersionEndDate: null,
        isFollowUp: null,
        program:
          'UHJvZ3JhbU5vZGU6YzRkNTY1N2QtMWEyOS00NmUxLTgxOTAtZGY3Zjg1YTBkMmVm',
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
            endCursor: 'YXJyYXljb25uZWN0aW9uOjE=',
            __typename: 'PageInfo',
          },
          totalCount: 2,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOmJmOTBkOWQzLTkyY2QtNGMyMC1iODc3LTU1OTFiNzUwZjlkZQ==',
                unicefId: 'PP-0060-22-11223344',
                isFollowUp: false,
                followUps: {
                  totalCount: 0,
                  edges: [],
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
                startDate: '2023-09-29',
                endDate: '2023-10-29',
                dispersionStartDate: '2023-09-29',
                dispersionEndDate: '2023-10-13',
                femaleChildrenCount: 0,
                femaleAdultsCount: 13,
                maleChildrenCount: 1,
                maleAdultsCount: 15,
                totalHouseholdsCount: 5,
                totalIndividualsCount: 29,
                totalEntitledQuantity: 2999,
                totalDeliveredQuantity: 999,
                totalUndeliveredQuantity: null,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOjAwMDAwMDAwLWZlZWQtYmVlZi0wMDAwLTAwMDAwYmFkZjAwZA==',
                unicefId: 'PP-0060-23-00000013',
                isFollowUp: false,
                followUps: {
                  totalCount: 0,
                  edges: [],
                  __typename: 'PaymentPlanNodeConnection',
                },
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
                startDate: '2023-09-29',
                endDate: '2023-10-29',
                dispersionStartDate: '2023-09-29',
                dispersionEndDate: '2023-10-13',
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
