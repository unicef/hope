import { AllPaymentPlansForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentPlansForTable = [
  {
    request: {
      query: AllPaymentPlansForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 5,
        orderBy: null,
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
                  'UGF5bWVudFBsYW5Ob2RlOjFmN2U5NmRkLTJmNDAtNDllNC04NzUyLTRjMzRjMGNiOGVjZQ==',
                unicefId: 'PP-0060-22-00000004',
                status: 'IN_REVIEW',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NmE5NWNmNTgtMDQzMS00NGU1LTkxMWEtMzljNmNiYmFiYTM2',
                  firstName: 'Brittany',
                  lastName: 'Freeman',
                  email: 'brittany.freeman_1661355260399366869@unicef.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6M2E4ZTc1NzktMzlkMS00Nzk4LTk3YWYtODliZTAwOTU0ODc4',
                  name: 'He risk wish.',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MTQ0OWMxNWQtZGNiNi00ZjRhLWFhMTAtNzQ5YmE1ODY1ZTY3',
                  name: 'Century per cup.',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'SZL',
                currencyName: 'Swazi lilangeni',
                startDate: '2020-07-25',
                endDate: '2022-06-24',
                dispersionStartDate: '2026-06-14',
                dispersionEndDate: '2028-07-30',
                femaleChildrenCount: 0,
                femaleAdultsCount: 0,
                maleChildrenCount: 0,
                maleAdultsCount: 0,
                totalHouseholdsCount: 0,
                totalIndividualsCount: 0,
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
                  'UGF5bWVudFBsYW5Ob2RlOmRiNWYxNDM4LTdjMTYtNDBmYi1iMzlmLTYwYTlmOGM3ZDkzNg==',
                unicefId: 'PP-0060-22-00000005',
                status: 'LOCKED',
                createdBy: {
                  id:
                    'VXNlck5vZGU6YjE5ZDYzYWQtMjk4My00MjUzLTllMmItMDAwYWFkZGJhY2Mw',
                  firstName: 'Derek',
                  lastName: 'Barrera',
                  email: 'derek.barrera_1661355260418320541@unicef.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6M2E4ZTc1NzktMzlkMS00Nzk4LTk3YWYtODliZTAwOTU0ODc4',
                  name: 'He risk wish.',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MzJiOWNjNGYtYmFhYS00ZjZlLTliMDctNjljODc3OGVmNTFm',
                  name: 'Least leave serious claim.',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'EUR',
                currencyName: 'Euro',
                startDate: '2021-06-22',
                endDate: '2023-06-29',
                dispersionStartDate: '2025-04-25',
                dispersionEndDate: '2025-11-22',
                femaleChildrenCount: 0,
                femaleAdultsCount: 2,
                maleChildrenCount: 0,
                maleAdultsCount: 0,
                totalHouseholdsCount: 1,
                totalIndividualsCount: 2,
                totalEntitledQuantity: 3063.97,
                totalDeliveredQuantity: 3053,
                totalUndeliveredQuantity: 10.97,
                __typename: 'PaymentPlanNode',
              },
              __typename: 'PaymentPlanNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'UGF5bWVudFBsYW5Ob2RlOmE2ODliYmYxLWMwZTAtNGU3OS04ZWFlLWNmMzI4NjNkOTMwMA==',
                unicefId: 'PP-0060-22-00000006',
                status: 'OPEN',
                createdBy: {
                  id:
                    'VXNlck5vZGU6ZTRkYjJlYWUtNmE1OC00YTgyLWExNDItOGE0ZWQ0NTRjZjA5',
                  firstName: 'Sandra',
                  lastName: 'Boyd',
                  email: 'sandra.boyd_1661355260432650130@unicef.com',
                  __typename: 'UserNode',
                },
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6M2E4ZTc1NzktMzlkMS00Nzk4LTk3YWYtODliZTAwOTU0ODc4',
                  name: 'He risk wish.',
                  __typename: 'ProgramNode',
                },
                targetPopulation: {
                  id:
                    'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6M2QzNzU3MzAtNzliOS00YThkLTkzMDUtYzBlNGY0YTc0NTA1',
                  name: 'Fall real big learn main entire clearly.',
                  __typename: 'TargetPopulationNode',
                },
                currency: 'MDL',
                currencyName: 'Moldovan leu',
                startDate: '2020-01-15',
                endDate: '2022-03-28',
                dispersionStartDate: '2027-05-30',
                dispersionEndDate: '2029-05-10',
                femaleChildrenCount: 3,
                femaleAdultsCount: 3,
                maleChildrenCount: 2,
                maleAdultsCount: 4,
                totalHouseholdsCount: 2,
                totalIndividualsCount: 15,
                totalEntitledQuantity: 21421915.5,
                totalDeliveredQuantity: 66158452.15,
                totalUndeliveredQuantity: 88358964.67,
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
