import { AllPaymentVerificationsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentVerifications = [
  {
    request: {
      query: AllPaymentVerificationsDocument,
      variables: {
        businessArea: 'afghanistan',
        cashPlanId:
          'Q2FzaFBsYW5Ob2RlOmNiNzBjYjdmLWY0N2EtNDI5Yy04Y2FjLTk0YzU0MDRiOTFkZA==',
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
            endCursor: 'YXJyYXljb25uZWN0aW9uOjM=',
            __typename: 'PageInfo',
          },
          totalCount: 4,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6NDg4OWMyNjItNWYzMi00NDhkLWE1MmEtNjFiYjlhMDQ5ZDBk',
                cashPlanPaymentVerification: {
                  id:
                    'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo2ZGIzY2Q0ZS02YzBkLTRjOTktYWJlZi02ZDBjZWEyMmEzY2Y=',
                  unicefId: 'PVP-1',
                  verificationChannel: 'MANUAL',
                  __typename: 'CashPlanPaymentVerificationNode',
                },
                paymentRecord: {
                  id:
                    'UGF5bWVudFJlY29yZE5vZGU6YmIzN2UzNDMtNDU0Mi00NTU0LWIzYjMtN2E1YTg2ZjQyZDAy',
                  caId: '123-21-PR-00014',
                  deliveredQuantity: 3525.0,
                  currency: 'NAD',
                  household: {
                    status: 'ACTIVE',
                    unicefId: 'HH-20-0000.0001',
                    id:
                      'SG91c2Vob2xkTm9kZTpmMTdkYTkyZS02YWMwLTQ0YmEtYmQ3Yi0wZTFmODRkOWJlNzc=',
                    headOfHousehold: {
                      id:
                        'SW5kaXZpZHVhbE5vZGU6OWM2ZDljMmUtZTgxNC00NDk3LWJkNTAtYzgzYmM2ODY3ZWJm',
                      fullName: 'Agata Kowalska',
                      phoneNo: '0048875012932',
                      phoneNoAlternative: '',
                      __typename: 'IndividualNode',
                    },
                    __typename: 'HouseholdNode',
                  },
                  __typename: 'PaymentRecordNode',
                },
                status: 'RECEIVED',
                receivedAmount: 3525.0,
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
