import { AllPaymentsForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentsForTable = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOjZmOTIxYmFlLTljODktNGRkYy1iNTRjLTI4Mzc3ZTA2YjUwNg==',

        first: 10,
        orderBy: '-created_at',
      },
    },
    result: {
      data: {
        allPayments: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          totalCount: 1,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudE5vZGU6YzY4YzMxY2MtNDNkZC00NWI1LWE0ZTMtMTgyMThiMDNjZDli',
                unicefId: 'RCPT-0060-23-0.000.121',
                status: 'PENDING',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTozYWI5ZDU3MC04NGI4LTQ2MDYtODg5YS0xNjc3MDBiOTBlMTE=',
                  unicefId: 'HH-23-0000.0017',
                  size: 8,
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                entitlementQuantity: null,
                entitlementQuantityUsd: null,
                currency: 'USD',
                deliveredQuantity: null,
                deliveredQuantityUsd: null,
                paymentPlanHardConflicted: false,
                paymentPlanSoftConflicted: false,
                paymentPlanHardConflictedData: [],
                paymentPlanSoftConflictedData: [],
                collector: {
                  id:
                    'SW5kaXZpZHVhbE5vZGU6ZDdhNDgwNWMtMzQ5My00ZTQ3LWIyNGEtMTJkZmU3NmMxMWQ0',
                  fullName: 'Emily Tracey Walter',
                  __typename: 'IndividualNode',
                },
                financialServiceProvider: null,
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
