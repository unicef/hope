import { AllPaymentVerificationsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentVerifications = [
  {
    request: {
      query: AllPaymentVerificationsDocument,
      variables: {
        businessArea: 'afghanistan',
        cashPlanId:
          'Q2FzaFBsYW5Ob2RlOjIyODExYzJjLWVmYTktNDRiYy1hYjM0LWQ0YjJkNjFmYThlNA==',
        first: 5,
        orderBy: null,
      },
    },
    result: {
      data: {
        allPaymentVerifications: {
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
                  'UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6NjgyNmVmZjctZTU4Zi00N2MxLTliMDEtNjIxOWMyZmMyZTcz',
                cashPlanPaymentVerification: {
                  id:
                    'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTpmOTY1M2FlNi1iMzVmLTQxZWYtOGU1My0zMjk5MDRjN2JhNmM=',
                  unicefId: 'PVP-14',
                  verificationChannel: 'MANUAL',
                  __typename: 'CashPlanPaymentVerificationNode',
                },
                paymentRecord: {
                  id:
                    'UGF5bWVudFJlY29yZE5vZGU6YTY0NmIyOTAtNjM5Ny00OGE4LWEzZWItN2YwZmFmODBiOWQ4',
                  caId: '123-21-PR-00014',
                  deliveredQuantity: 3377.0,
                  currency: 'CUC',
                  household: {
                    status: 'ACTIVE',
                    unicefId: 'HH-20-0000.0001',
                    id:
                      'SG91c2Vob2xkTm9kZTpmMTdkYTkyZS02YWMwLTQ0YmEtYmQ3Yi0wZTFmODRkOWJlNzc=',
                    headOfHousehold: {
                      id:
                        'SW5kaXZpZHVhbE5vZGU6OWM2ZDljMmUtZTgxNC00NDk3LWJkNTAtYzgzYmM2ODY3ZWJm',
                      fullName: 'Agata Kowalska',
                      familyName: 'Kowalska',
                      phoneNo: '+48875012932',
                      phoneNoAlternative: '',
                      __typename: 'IndividualNode',
                    },
                    __typename: 'HouseholdNode',
                  },
                  __typename: 'PaymentRecordNode',
                },
                status: 'PENDING',
                receivedAmount: null,
                __typename: 'PaymentVerificationNode',
              },
              __typename: 'PaymentVerificationNodeEdge',
            },
          ],
          __typename: 'PaymentVerificationNodeConnection',
        },
      },
    },
  },
];
