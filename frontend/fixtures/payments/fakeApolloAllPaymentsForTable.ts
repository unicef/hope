import { AllPaymentsForTableDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllPaymentsForTable = [
  {
    request: {
      query: AllPaymentsForTableDocument,
      variables: {
        businessArea: 'afghanistan',
        paymentPlanId:
          'UGF5bWVudFBsYW5Ob2RlOmM2ZWYyMzJjLTgyODEtNGM0Yy05MTdhLTdmMWZkYzhhYTI0Ng==',
        first: 5,
        orderBy: '-created_at',
      },
    },
    result: {
      "data": {
        "allPayments": {
          "pageInfo": {
            "hasNextPage": false,
            "hasPreviousPage": false,
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
            "endCursor": "YXJyYXljb25uZWN0aW9uOjE=",
            "__typename": "PageInfo"
          },
          "totalCount": 2,
          "edges": [
            {
              "cursor": "YXJyYXljb25uZWN0aW9uOjA=",
              "node": {
                "id": "UGF5bWVudE5vZGU6MTAwMDAwMDAtZmVlZC1iZWVmLTAwMDAtMDAwMDBiYWRmMDBk",
                "unicefId": "RCPT-0060-22-0.000.015",
                "household": {
                  "id": "SG91c2Vob2xkTm9kZTphYTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDE=",
                  "unicefId": "HH-21-0000.0003",
                  "size": 4,
                  "admin2": null,
                  "__typename": "HouseholdNode"
                },
                "entitlementQuantity": null,
                "entitlementQuantityUsd": null,
                "currency": "",
                "deliveredQuantity": null,
                "deliveredQuantityUsd": null,
                "paymentPlanHardConflicted": false,
                "paymentPlanSoftConflicted": false,
                "paymentPlanHardConflictedData": [],
                "paymentPlanSoftConflictedData": [],
                "collector": {
                  "id": "SW5kaXZpZHVhbE5vZGU6Y2MwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAx",
                  "fullName": "Jan Kowalski",
                  "__typename": "IndividualNode"
                },
                "hasPaymentChannel": true,
                "financialServiceProvider": {
                  "id": "RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTowMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC1mMDAwMDAwMDAwMDE=",
                  "name": "Test FSP 1",
                  "__typename": "FinancialServiceProviderNode"
                },
                "__typename": "PaymentNode"
              },
              "__typename": "PaymentNodeEdge"
            },
            {
              "cursor": "YXJyYXljb25uZWN0aW9uOjE=",
              "node": {
                "id": "UGF5bWVudE5vZGU6MjAwMDAwMDAtZmVlZC1iZWVmLTAwMDAtMDAwMDBiYWRmMDBk",
                "unicefId": "RCPT-0060-22-0.000.016",
                "household": {
                  "id": "SG91c2Vob2xkTm9kZTphYTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDI=",
                  "unicefId": "HH-21-0000.0004",
                  "size": 4,
                  "admin2": null,
                  "__typename": "HouseholdNode"
                },
                "entitlementQuantity": null,
                "entitlementQuantityUsd": null,
                "currency": "",
                "deliveredQuantity": null,
                "deliveredQuantityUsd": null,
                "paymentPlanHardConflicted": false,
                "paymentPlanSoftConflicted": false,
                "paymentPlanHardConflictedData": [],
                "paymentPlanSoftConflictedData": [],
                "collector": {
                  "id": "SW5kaXZpZHVhbE5vZGU6Y2MwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAy",
                  "fullName": "Adam Nowak",
                  "__typename": "IndividualNode"
                },
                "hasPaymentChannel": true,
                "financialServiceProvider": {
                  "id": "RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTowMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC1mMDAwMDAwMDAwMDE=",
                  "name": "Test FSP 1",
                  "__typename": "FinancialServiceProviderNode"
                },
                "__typename": "PaymentNode"
              },
              "__typename": "PaymentNodeEdge"
            }
          ],
          "__typename": "PaymentNodeConnection"
        }
      }
    },
  },
];
