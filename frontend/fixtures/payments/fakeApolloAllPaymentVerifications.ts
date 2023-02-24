import { AllPaymentVerificationsDocument, PaymentVerificationNodeConnection } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentVerifications = [
  {
    request: {
      query: AllPaymentVerificationsDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
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
              cursor: "YXJyYXljb25uZWN0aW9uOjA=",
              node: {
                id: "UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6NDYyODNkMTktMWJjMS00NjljLWI0Y2MtODQ5NjJlOGU0YTU5",
                paymentVerificationPlan: {
                  id: "UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmQ1YWVmZjE1LWQ0ZDAtNGE0YS1hMzIzLWNlMGMwOTM2MzU3Ng==",
                  unicefId: "PVP-1",
                  verificationChannel: "RAPIDPRO",
                  __typename: "PaymentVerificationPlanNode"
                },
                payment: {
                  id: "UGF5bWVudE5vZGU6NzBjYmU4ZjgtNzUxYy00NTliLTlmZjEtZDg4M2Y4ZTFjNGFj",
                  unicefId: "RCPT-0060-22-0.000.005",
                  deliveredQuantity: 2274,
                  currency: "NOK",
                  household: {
                    status: "ACTIVE",
                    unicefId: "HH-22-0000.0007",
                    id: "SG91c2Vob2xkTm9kZTo1YzhhYTJkNy0zNWY0LTQ3ZjMtODNkNy1jZjQwNTMxYmQzMjI=",
                    headOfHousehold: {
                      id: "SW5kaXZpZHVhbE5vZGU6Yjc5MjlkNjMtNTIzZS00YmNjLWI3YTUtODA0ZjAxYmJiYjA1",
                      fullName: "Denise Laurie Schwartz",
                      familyName: "Schwartz",
                      phoneNo: "+1 684 1511478743",
                      phoneNoAlternative: "",
                      __typename: "IndividualNode"
                    },
                    __typename: "HouseholdNode"
                  },
                  __typename: "GenericPaymentNode"
                },
                status: "PENDING",
                receivedAmount: null,
                __typename: "PaymentVerificationNode"
              },
              __typename: "PaymentVerificationNodeEdge"
            },
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjE=",
              node: {
                id: "UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6OGJkM2RlMjYtODZjMi00OTcyLTgyM2QtYWMyMjc5MDA4ZWNm",
                paymentVerificationPlan: {
                  id: "UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmQ1YWVmZjE1LWQ0ZDAtNGE0YS1hMzIzLWNlMGMwOTM2MzU3Ng==",
                  unicefId: "PVP-1",
                  verificationChannel: "RAPIDPRO",
                  __typename: "PaymentVerificationPlanNode"
                },
                payment: {
                  id: "UGF5bWVudE5vZGU6ZmI4NjIzM2EtNWRiOS00NjQ2LWJiN2UtN2Q3OTVhNWI3Njc2",
                  unicefId: "RCPT-0060-22-0.000.007",
                  deliveredQuantity: 5526,
                  currency: "BYR",
                  household: {
                    status: "ACTIVE",
                    unicefId: "HH-22-0000.0009",
                    id: "SG91c2Vob2xkTm9kZTpkNGNjZjliMy01N2M0LTQ4M2UtODIxMS1jODZkN2M5Yzc0Zjk=",
                    headOfHousehold: {
                      id: "SW5kaXZpZHVhbE5vZGU6MzAyNmI3ZTUtZGI0Ny00ZGUwLWIzOGMtNGYwMGY1ODQ2MGFl",
                      fullName: "John Sally Martin",
                      familyName: "Martin",
                      phoneNo: "+993 0684121090",
                      phoneNoAlternative: "",
                      __typename: "IndividualNode"
                    },
                    __typename: "HouseholdNode"
                  },
                  __typename: "GenericPaymentNode"
                },
                status: "PENDING",
                receivedAmount: null,
                __typename: "PaymentVerificationNode"
              },
              __typename: "PaymentVerificationNodeEdge"
            },
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjI=",
              node: {
                id: "UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6OTEyNWIxYWMtY2Y2Zi00ZDg2LTk4OWEtNDFmMDlkZTg3ZTQ0",
                paymentVerificationPlan: {
                  id: "UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmQ1YWVmZjE1LWQ0ZDAtNGE0YS1hMzIzLWNlMGMwOTM2MzU3Ng==",
                  unicefId: "PVP-1",
                  verificationChannel: "RAPIDPRO",
                  __typename: "PaymentVerificationPlanNode"
                },
                payment: {
                  id: "UGF5bWVudE5vZGU6M2UyZTQ4NjktZWRmNC00NTA4LWI4ZjAtY2YwZjZmNmUzNzY3",
                  unicefId: "RCPT-0060-22-0.000.003",
                  deliveredQuantity: 1877,
                  currency: "SLL",
                  household: {
                    status: "ACTIVE",
                    unicefId: "HH-22-0000.0005",
                    id: "SG91c2Vob2xkTm9kZTo3ZDhjOTYwMi1iMWIzLTQzM2ItODI4My0xMGQ3NGU2ZWU4NGY=",
                    headOfHousehold: {
                      id: "SW5kaXZpZHVhbE5vZGU6NzU5MzQzYTEtMWJjNy00Y2JhLThkZDEtZjA5YjQ1NzRkMmFi",
                      fullName: "Kristina Katrina Russo",
                      familyName: "Russo",
                      phoneNo: "+232 5632769040",
                      phoneNoAlternative: "",
                      __typename: "IndividualNode"
                    },
                    __typename: "HouseholdNode"
                  },
                  __typename: "GenericPaymentNode"
                },
                status: "PENDING",
                receivedAmount: null,
                __typename: "PaymentVerificationNode"
              },
              __typename: "PaymentVerificationNodeEdge"
            },
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjM=",
              node: {
                id: "UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6ZDFhNTUxZGMtNjcyMi00ZmNiLTk5NjQtN2Q4MTg5MWJjYzY1",
                paymentVerificationPlan: {
                  id: "UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmQ1YWVmZjE1LWQ0ZDAtNGE0YS1hMzIzLWNlMGMwOTM2MzU3Ng==",
                  unicefId: "PVP-1",
                  verificationChannel: "RAPIDPRO",
                  __typename: "PaymentVerificationPlanNode"
                },
                payment: {
                  id: "UGF5bWVudE5vZGU6ZTE2YTUxNWUtNjlhOC00NTM2LTg0MGMtMjczN2FmMjgyYmQw",
                  unicefId: "RCPT-0060-22-0.000.004",
                  deliveredQuantity: 1156,
                  currency: "BWP",
                  household: {
                    status: "ACTIVE",
                    unicefId: "HH-22-0000.0006",
                    id: "SG91c2Vob2xkTm9kZTpmMDM4ZDA1MS02YmQ5LTQ0NWMtOGFkOC1lMWRhOWI4YjQ2MzA=",
                    headOfHousehold: {
                      id: "SW5kaXZpZHVhbE5vZGU6OWIxM2IwYzUtZWI4Yi00ODVhLWE0ODktNDc5NzQ3YjU2ZmEy",
                      fullName: "Barbara Jeremy James",
                      familyName: "James",
                      phoneNo: "+965 0452689882",
                      phoneNoAlternative: "",
                      __typename: "IndividualNode"
                    },
                    __typename: "HouseholdNode"
                  },
                  __typename: "GenericPaymentNode"
                },
                status: "PENDING",
                receivedAmount: null,
                __typename: "PaymentVerificationNode"
              },
              __typename: "PaymentVerificationNodeEdge"
            },
            {
              cursor: "YXJyYXljb25uZWN0aW9uOjQ=",
              node: {
                id: "UGF5bWVudFZlcmlmaWNhdGlvbk5vZGU6ZWMxMDgzODktM2UzZS00NmZlLThmMDItNmRmMjBjM2M0YjBl",
                paymentVerificationPlan: {
                  id: "UGF5bWVudFZlcmlmaWNhdGlvblBsYW5Ob2RlOmQ1YWVmZjE1LWQ0ZDAtNGE0YS1hMzIzLWNlMGMwOTM2MzU3Ng==",
                  unicefId: "PVP-1",
                  verificationChannel: "RAPIDPRO",
                  __typename: "PaymentVerificationPlanNode"
                },
                payment: {
                  id: "UGF5bWVudE5vZGU6ZjI3NTQxNzMtZjdjMC00NWJhLTgxNDctMmE4MTVjNWZmZmI3",
                  unicefId: "RCPT-0060-22-0.000.006",
                  deliveredQuantity: 974,
                  currency: "YER",
                  household: {
                    status: "ACTIVE",
                    unicefId: "HH-22-0000.0008",
                    id: "SG91c2Vob2xkTm9kZTo5MmNmMzk3NC01MzVmLTRkMTMtYmRmNC1iOWJlNTJiNzMwN2E=",
                    headOfHousehold: {
                      id: "SW5kaXZpZHVhbE5vZGU6YTJmZTQ5OTAtY2Q0MC00MTBjLTg3YTktMmE0MTM1MjFjMmJl",
                      fullName: "Michelle Eric Williams",
                      familyName: "Williams",
                      phoneNo: "+1 441 4461030202",
                      phoneNoAlternative: "",
                      __typename: "IndividualNode"
                    },
                    __typename: "HouseholdNode"
                  },
                  __typename: "GenericPaymentNode"
                },
                status: "PENDING",
                receivedAmount: null,
                __typename: "PaymentVerificationNode"
              },
              __typename: "PaymentVerificationNodeEdge"
            },
          ],
          __typename: 'PaymentVerificationNodeConnection',
        } as PaymentVerificationNodeConnection,
      },
    },
  },
];
