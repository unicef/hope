import { AllPaymentsForTableDocument } from '@generated/graphql';

export const fakeApolloAllPaymentsHousehold = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 10,
        orderBy: '-created_at',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOjgyZTUzYzE3LTM4MmMtNGI2My05ZTk5LTg0ZTMxMGZhNGRmYQ==',
      },
    },
    result: {
      data: {
        allPayments: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            __typename: 'PageInfo',
          },
          totalCount: 5,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id: 'UGF5bWVudE5vZGU6MDk5MjQ3YTYtM2FjYS00ZjRhLWFiZjMtMGEwNmVkNjAyZTIx',
                unicefId: 'RCPT-0060-25-0.000.014',
                status: 'PENDING',
                vulnerabilityScore: null,
                parent: {
                  program: {
                    id: 'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                    name: 'Test Program',
                    __typename: 'ProgramNode',
                  },
                  __typename: 'PaymentPlanNode',
                },
                household: {
                  id: 'SG91c2Vob2xkTm9kZTo0MWJiNjNhNy0xNTM1LTQxY2ItOWRlZS04MGFjYWUxMjVjYTk=',
                  unicefId: 'HH-0',
                  size: 5,
                  admin2: null,
                  headOfHousehold: {
                    id: 'SW5kaXZpZHVhbE5vZGU6ODdhZGM2ODQtZGQ5MS00MzNiLTk2MTMtZTAxMGU2MGNmZDQz',
                    unicefId: 'IND-0',
                    fullName: 'Pamela Tara Miller',
                    __typename: 'IndividualNode',
                  },
                  individuals: {
                    edges: [
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ODdhZGM2ODQtZGQ5MS00MzNiLTk2MTMtZTAxMGU2MGNmZDQz',
                          unicefId: 'IND-0',
                          fullName: 'Pamela Tara Miller',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6NWRiZmZmNDItYjcwNy00YzE5LThlM2ItZmNhYjE5ZmYyNDhl',
                          unicefId: 'IND-1',
                          fullName: 'John Mia Waters',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MjNiY2QyMjYtM2ZmYS00NjE1LTkwYjQtMGY1ZWI1MjFkYTUz',
                          unicefId: 'IND-2',
                          fullName: 'Raymond Lisa Brown',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MmEwN2MzNDEtYjdlYS00MTEyLWFmNWItNGM3MTQ2Y2VkZDZi',
                          unicefId: 'IND-3',
                          fullName: 'James Derrick Davis',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6NTE0NDMxNzgtNjI1MS00NzA4LWIxMDktNTdkYTE4MTNkZDk5',
                          unicefId: 'IND-4',
                          fullName: 'Matthew Andrew Clarke',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6NDY0YmZmNjAtMDRkMS00MTk3LTllZTEtZWI0MjUzYmZhMGVh',
                          unicefId: 'IND-5',
                          fullName: 'Gwendolyn Shannon Shields',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6YzBiNzNjNWYtNTI3Yy00NDcyLThkNTgtNTA4MjViZGM0MmI0',
                          unicefId: 'IND-6',
                          fullName: 'Terry Elizabeth Bradshaw',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                    ],
                    __typename: 'IndividualNodeConnection',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantity: 1686,
                entitlementQuantityUsd: 1686,
                currency: 'USD',
                deliveredQuantity: 423,
                deliveredQuantityUsd: 423,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id: 'SW5kaXZpZHVhbE5vZGU6NDY0YmZmNjAtMDRkMS00MTk3LTllZTEtZWI0MjUzYmZhMGVh',
                  unicefId: 'IND-5',
                  fullName: 'Gwendolyn Shannon Shields',
                  __typename: 'IndividualNode',
                },
                financialServiceProvider: {
                  id: 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTowMDRiMGZkOC0wNzVmLTQyNDEtODJiMi1hMTZmZGZiOWE0NmM=',
                  name: 'Rowe-Horne',
                  __typename: 'FinancialServiceProviderNode',
                },
                fspAuthCode: '',
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id: 'UGF5bWVudE5vZGU6ZjE0MjU1YTMtNDllYi00ZjAxLTgyNGYtMDFiZGI1NDRiZDM1',
                unicefId: 'RCPT-0060-25-0.000.015',
                status: 'PENDING',
                vulnerabilityScore: null,
                parent: {
                  program: {
                    id: 'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                    name: 'Test Program',
                    __typename: 'ProgramNode',
                  },
                  __typename: 'PaymentPlanNode',
                },
                household: {
                  id: 'SG91c2Vob2xkTm9kZTowMWY2MDA3Yy1lYzMzLTQ4MTMtODRkZS04ZGQ3YzM4M2VjNzM=',
                  unicefId: 'HH-1',
                  size: 4,
                  admin2: null,
                  headOfHousehold: {
                    id: 'SW5kaXZpZHVhbE5vZGU6ZDJhNGQ2MTEtY2RjYS00M2Q1LWJhMmYtYjc3Y2E2YzY2N2Y3',
                    unicefId: 'IND-7',
                    fullName: 'Eugene Kelly Weiss',
                    __typename: 'IndividualNode',
                  },
                  individuals: {
                    edges: [
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZDJhNGQ2MTEtY2RjYS00M2Q1LWJhMmYtYjc3Y2E2YzY2N2Y3',
                          unicefId: 'IND-7',
                          fullName: 'Eugene Kelly Weiss',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MDdhN2I1MjctNzFmNi00MDZjLTg1OTktNmE2NmM5OTI2NmQz',
                          unicefId: 'IND-8',
                          fullName: 'Kayla Brandon Rodriguez',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6NjVmZjBhZTMtNjFmMC00MmIwLWFiZjUtMjFkZGQ5MmY1MmJi',
                          unicefId: 'IND-9',
                          fullName: 'Tina Patrick Shannon',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6OTAzZDlhZTQtM2VlOS00MmY4LTk3MzktNjkwMjhlNTQ1MWE1',
                          unicefId: 'IND-10',
                          fullName: 'Elizabeth Tracy Vasquez',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6NzhjMDM0NTctZGUyMy00YmZjLWJjNDgtM2RmZTYyOTk5ODk1',
                          unicefId: 'IND-11',
                          fullName: 'Keith Alicia Perkins',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZDk2MjI4NmEtNWE0Yi00NjA5LWIyMGUtMjM2ZTMzMDgzYmUy',
                          unicefId: 'IND-12',
                          fullName: 'Brandon John Smith',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                    ],
                    __typename: 'IndividualNodeConnection',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantity: 3180,
                entitlementQuantityUsd: 3180,
                currency: 'USD',
                deliveredQuantity: 6549,
                deliveredQuantityUsd: 6549,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id: 'SW5kaXZpZHVhbE5vZGU6NzhjMDM0NTctZGUyMy00YmZjLWJjNDgtM2RmZTYyOTk5ODk1',
                  unicefId: 'IND-11',
                  fullName: 'Keith Alicia Perkins',
                  __typename: 'IndividualNode',
                },
                financialServiceProvider: {
                  id: 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTowMjA4NGFkNy1mYjFmLTRlN2UtYWFmMi05YzBiYzRjZDA0NmI=',
                  name: 'Tate LLC',
                  __typename: 'FinancialServiceProviderNode',
                },
                fspAuthCode: '',
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id: 'UGF5bWVudE5vZGU6NDIzNDhlNTgtY2YwNi00OTQwLTlhMDctMjNlZjMxNzY4ZGE3',
                unicefId: 'RCPT-0060-25-0.000.016',
                status: 'NOT_DISTRIBUTED',
                vulnerabilityScore: null,
                parent: {
                  program: {
                    id: 'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                    name: 'Test Program',
                    __typename: 'ProgramNode',
                  },
                  __typename: 'PaymentPlanNode',
                },
                household: {
                  id: 'SG91c2Vob2xkTm9kZTo5NDAzNmRiOS1iMDE0LTQ5ZWItYjNiYi1mMDRkMGVkMDVmM2U=',
                  unicefId: 'HH-2',
                  size: 5,
                  admin2: null,
                  headOfHousehold: {
                    id: 'SW5kaXZpZHVhbE5vZGU6MjgxMmY0NTYtOGFjYS00NTJkLTliZTQtNWFlNjFjYzMwNjNk',
                    unicefId: 'IND-13',
                    fullName: 'Rachael Hannah Lewis',
                    __typename: 'IndividualNode',
                  },
                  individuals: {
                    edges: [
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MjgxMmY0NTYtOGFjYS00NTJkLTliZTQtNWFlNjFjYzMwNjNk',
                          unicefId: 'IND-13',
                          fullName: 'Rachael Hannah Lewis',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZTg2Mjc0NDctMTgwMC00MmVkLWI3NzktOTE3YWE1OTUxZWEz',
                          unicefId: 'IND-14',
                          fullName: 'Laurie Todd Johnson',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZGE1YWFmZGUtODk4ZC00NDUyLWI0NWMtMmUzOWQzMDQ0NjMy',
                          unicefId: 'IND-15',
                          fullName: 'Thomas Deborah Smith',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZDk4OWE4OWMtYmJkNS00ZTcwLWIwNjktZDViMWQ4NThjMTM1',
                          unicefId: 'IND-16',
                          fullName: 'Joseph Benjamin Benjamin',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZDNmNmZlMGEtZjgzZi00YzUwLWI3YTUtMTRmYjk1NDgyODZh',
                          unicefId: 'IND-17',
                          fullName: 'Brandon Brandon Cohen',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MzJiMzczY2MtMTM0ZC00ZTdjLWI3NmItZjFmYjkyNDA5ZjZh',
                          unicefId: 'IND-18',
                          fullName: 'Austin Alexander Reynolds',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZDJjNTM2MTUtMDYyNi00NjlhLWExZTQtMzVjZGQyZmM1MThi',
                          unicefId: 'IND-19',
                          fullName: 'Kimberly Kevin Henry',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                    ],
                    __typename: 'IndividualNodeConnection',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantity: 3473,
                entitlementQuantityUsd: 3473,
                currency: 'USD',
                deliveredQuantity: 0,
                deliveredQuantityUsd: 0,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id: 'SW5kaXZpZHVhbE5vZGU6MzJiMzczY2MtMTM0ZC00ZTdjLWI3NmItZjFmYjkyNDA5ZjZh',
                  unicefId: 'IND-18',
                  fullName: 'Austin Alexander Reynolds',
                  __typename: 'IndividualNode',
                },
                financialServiceProvider: {
                  id: 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo2MDc0ZDM2My0xMWZmLTQzZTctODUwYS03MWEwNGViNjc0ODk=',
                  name: 'Jones Inc',
                  __typename: 'FinancialServiceProviderNode',
                },
                fspAuthCode: '',
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id: 'UGF5bWVudE5vZGU6ZTU5ZjU2YzUtNzEwMC00MzU3LWI2OWEtZDE2MDA1ZGFjYTEz',
                unicefId: 'RCPT-0060-25-0.000.017',
                status: 'TRANSACTION_ERRONEOUS',
                vulnerabilityScore: null,
                parent: {
                  program: {
                    id: 'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                    name: 'Test Program',
                    __typename: 'ProgramNode',
                  },
                  __typename: 'PaymentPlanNode',
                },
                household: {
                  id: 'SG91c2Vob2xkTm9kZTo3OTg3ZWM4ZS05OWE3LTRiZTktODkwZi02ODg5M2RkM2I4NzU=',
                  unicefId: 'HH-3',
                  size: 5,
                  admin2: null,
                  headOfHousehold: {
                    id: 'SW5kaXZpZHVhbE5vZGU6NTMxOGNmMGQtMDRiZS00YmE3LThlMDItYzQ3OGE2NjRlYjc1',
                    unicefId: 'IND-20',
                    fullName: 'Leslie Jill Elliott',
                    __typename: 'IndividualNode',
                  },
                  individuals: {
                    edges: [
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6NTMxOGNmMGQtMDRiZS00YmE3LThlMDItYzQ3OGE2NjRlYjc1',
                          unicefId: 'IND-20',
                          fullName: 'Leslie Jill Elliott',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MDMwOWI2YzktN2JhMS00NzliLWE1ZGMtOThjY2YzYzEyYjdj',
                          unicefId: 'IND-21',
                          fullName: 'Jeffrey Joseph Jones',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZDhhZDI0MjAtMDE1My00NTQ2LWEwZWItZDdmZmEzMjE3Yzlk',
                          unicefId: 'IND-22',
                          fullName: 'Cindy Michael Pace',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZGU2ZjhlNDAtZmNhZS00ZjRjLTk4ZGUtODIwZDI2ZTEzNTVi',
                          unicefId: 'IND-23',
                          fullName: 'Kelly Tamara Gutierrez',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6Nzg0ZGUxNTctZTUyMC00ZDRmLTg3NGQtYTFkNmQ5YWM4Njc0',
                          unicefId: 'IND-24',
                          fullName: 'Stephanie Katherine Bradshaw',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MWQxN2FhNjQtZDY1Yy00Y2ViLWI0ZDEtMTg0MTI2MTVmNmE1',
                          unicefId: 'IND-25',
                          fullName: 'Elizabeth Daniel Riley',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6YjAxNTUwMDMtYTAwYS00MWZjLWJlZDgtYjA0OWFmNTlmMDU2',
                          unicefId: 'IND-26',
                          fullName: 'Crystal Heather Jones',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                    ],
                    __typename: 'IndividualNodeConnection',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantity: 6431,
                entitlementQuantityUsd: 6431,
                currency: 'USD',
                deliveredQuantity: null,
                deliveredQuantityUsd: null,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id: 'SW5kaXZpZHVhbE5vZGU6MWQxN2FhNjQtZDY1Yy00Y2ViLWI0ZDEtMTg0MTI2MTVmNmE1',
                  unicefId: 'IND-25',
                  fullName: 'Elizabeth Daniel Riley',
                  __typename: 'IndividualNode',
                },
                financialServiceProvider: {
                  id: 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo3YWRlMTU1Ni1jMjk0LTQ5MGMtYTRhZC1mMjcxMTNkYWYxODA=',
                  name: 'Norman Inc',
                  __typename: 'FinancialServiceProviderNode',
                },
                fspAuthCode: '',
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                id: 'UGF5bWVudE5vZGU6Y2I3MzJjN2UtZjAxYy00ZDM1LWJkOGMtNjFjMTg5YmMwODhh',
                unicefId: 'RCPT-0060-25-0.000.018',
                status: 'PENDING',
                vulnerabilityScore: null,
                parent: {
                  program: {
                    id: 'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                    name: 'Test Program',
                    __typename: 'ProgramNode',
                  },
                  __typename: 'PaymentPlanNode',
                },
                household: {
                  id: 'SG91c2Vob2xkTm9kZTplMTQ4YTVmZC00NWZiLTRjNmEtODk1MS0zMGI2NTZmYjNiYTY=',
                  unicefId: 'HH-4',
                  size: 4,
                  admin2: null,
                  headOfHousehold: {
                    id: 'SW5kaXZpZHVhbE5vZGU6ODljMjc3ZmItYjhkZi00MzAxLTg5NGQtMmRhNmJiMzBhNmQy',
                    unicefId: 'IND-27',
                    fullName: 'Bradley Janice Gonzalez',
                    __typename: 'IndividualNode',
                  },
                  individuals: {
                    edges: [
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ODljMjc3ZmItYjhkZi00MzAxLTg5NGQtMmRhNmJiMzBhNmQy',
                          unicefId: 'IND-27',
                          fullName: 'Bradley Janice Gonzalez',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZWZmNjlhNmItZTQ3MC00YjlmLWI4ZDgtZGJlMjE2OTgxYjI1',
                          unicefId: 'IND-28',
                          fullName: 'Adrienne Melissa Golden',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZDI1MzY0NTktYmQ4ZC00OTg2LTkxYzUtZmM3MDA5ZDEyNTZi',
                          unicefId: 'IND-29',
                          fullName: 'Calvin Tiffany Rivera',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6MzQyYTgyM2MtNTdkYS00OWQwLTkzMGUtMWFjNjA4NzM0NGRk',
                          unicefId: 'IND-30',
                          fullName: 'Shelby Diane Vazquez',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6ZGZhZmQyOTYtOTIyMS00MjBhLWI0MmItODc4YmI5YzhiZjQx',
                          unicefId: 'IND-31',
                          fullName: 'Jeremiah Stacy Greene',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                      {
                        node: {
                          id: 'SW5kaXZpZHVhbE5vZGU6NGU3MjZhNDgtNzNiZi00NTllLWJkMGUtOGE3MzViOWUzYWI0',
                          unicefId: 'IND-32',
                          fullName: 'Kim Scott Oconnor',
                          __typename: 'IndividualNode',
                        },
                        __typename: 'IndividualNodeEdge',
                      },
                    ],
                    __typename: 'IndividualNodeConnection',
                  },
                  __typename: 'HouseholdNode',
                },
                entitlementQuantity: 800,
                entitlementQuantityUsd: 800,
                currency: 'USD',
                deliveredQuantity: 1754,
                deliveredQuantityUsd: 1754,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id: 'SW5kaXZpZHVhbE5vZGU6ZGZhZmQyOTYtOTIyMS00MjBhLWI0MmItODc4YmI5YzhiZjQx',
                  unicefId: 'IND-31',
                  fullName: 'Jeremiah Stacy Greene',
                  __typename: 'IndividualNode',
                },
                financialServiceProvider: {
                  id: 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTplZWIwMmVjZi00ZDYwLTRkZDktOThhNS05YTk1ZTJlYmYxZjY=',
                  name: 'Taylor and Sons',
                  __typename: 'FinancialServiceProviderNode',
                },
                fspAuthCode: '',
                __typename: 'PaymentNode',
              },
              __typename: 'PaymentNodeEdge',
            },
          ],
          __typename: 'PaymentNodeConnection',
        },
      },
    },
  },
];
