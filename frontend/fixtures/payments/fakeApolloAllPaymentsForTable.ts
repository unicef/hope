import { AllPaymentsForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentsForTable = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOjI1ZTNkODA0LTAzMzEtNDhkOC1iYTk2LWVmZjEzYmU3ZDdiYQ==',
        first: 5,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allPayments: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: "YXJyYXljb25uZWN0aW9uOjA=",
            endCursor: "YXJyYXljb25uZWN0aW9uOjQ=",
            __typename: "PageInfo"
          },
          totalCount: 2,
          edges: [
            {
              cursor:  "YXJyYXljb25uZWN0aW9uOjA=",
              node:  {
                id:  "UGF5bWVudE5vZGU6N2E2M2E5NjItZmZlNC00NGU2LTlkN2MtMWU4YmExMWE1YTVj",
                unicefId:  "RCPT-0060-22-0.000.014",
                household:  {
                  id:  "SG91c2Vob2xkTm9kZTo5NjBmN2VlZS1kNDVhLTQ3OGEtYjRiNC04MmQwZThlODBhZGQ=",
                  unicefId:  "HH-20-0000.0002",
                  size:  4,
                  admin2:  {
                    id:  "QXJlYU5vZGU6NWYwNmViMzEtM2I1ZC00YmQ1LWIyOTMtYTg5YmE3OTgxYmZj",
                    name:  "Abband",
                    __typename:  "AreaNode"
                  },
                  __typename:  "HouseholdNode"
                },
                entitlementQuantityUsd:  1223,
                paymentPlanHardConflicted:  false,
                paymentPlanSoftConflicted:  true,
                paymentPlanHardConflictedData:  [],
                paymentPlanSoftConflictedData:  [
                  {
                    paymentPlanUnicefId:  "PP-0060-22-00000008",
                    paymentPlanId:  "70868e2e-2794-40fc-b90a-66d93d60e0f3",
                    paymentPlanStartDate:  "2020-07-26",
                    paymentPlanEndDate:  "2022-08-08",
                    paymentPlanStatus:  "OPEN",
                    paymentId:  "3288ceea-eb63-486c-90ea-338af08254ce",
                    paymentUnicefId:  "RCPT-0060-22-0.000.016",
                    __typename:  "PaymentConflictDataNode"
                  }
                ],
                collector:  {
                  id:  "SW5kaXZpZHVhbE5vZGU6Y2VkZDRiNDktNTRlMC00NDA4LThmZDItMTAzMGYwNWE3YTZh",
                  fullName:  "Jan Romaniak",
                  __typename:  "IndividualNode"
                },
                hasPaymentChannel:  true,
                __typename:  "PaymentNode"
              },
              __typename:  "PaymentNodeEdge"
            },
            {
              cursor:  "YXJyYXljb25uZWN0aW9uOjE=",
              node:  {
                id:  "UGF5bWVudE5vZGU6NzlkYTg5NTctYWZhMy00YTQ0LWI2ZTUtMzJhZjE3NGRhMWQx",
                unicefId:  "RCPT-0060-22-0.000.013",
                household:  {
                  id:  "SG91c2Vob2xkTm9kZTowOWI4YWE2ZC1hOTViLTQ5NWEtYTM0ZS1kMGM0YmQyNWE4Njc=",
                  unicefId:  "HH-20-0000.0001",
                  size:  4,
                  admin2:  {
                    id:  "QXJlYU5vZGU6NzYxZjhkODQtOTljZi00MWExLTk1MmYtMTQ5ZWFhNjJkZDJh",
                    name:  "Achin",
                    __typename:  "AreaNode"
                  },
                  __typename:  "HouseholdNode"
                },
                entitlementQuantityUsd:  1708,
                paymentPlanHardConflicted:  false,
                paymentPlanSoftConflicted:  true,
                paymentPlanHardConflictedData:  [],
                paymentPlanSoftConflictedData:  [
                  {
                    paymentPlanUnicefId:  "PP-0060-22-00000008",
                    paymentPlanId:  "70868e2e-2794-40fc-b90a-66d93d60e0f3",
                    paymentPlanStartDate:  "2020-07-26",
                    paymentPlanEndDate:  "2022-08-08",
                    paymentPlanStatus:  "OPEN",
                    paymentId:  "81340b96-1920-412e-a42d-794c71837590",
                    paymentUnicefId:  "RCPT-0060-22-0.000.015",
                    __typename:  "PaymentConflictDataNode"
                  }
                ],
                collector:  {
                  id:  "SW5kaXZpZHVhbE5vZGU6N2JhZjlhMGItODQ4My00MDA0LTg2NzAtMGU4YTUwZjI1YTMw",
                  fullName:  "Agata Kowalska",
                  __typename:  "IndividualNode"
                },
                hasPaymentChannel:  true,
                __typename:  "PaymentNode"
              },
              __typename:  "PaymentNodeEdge"
            }
          ],
          __typename: "PaymentNodeConnection"
        }
      }
    },
  },
];
