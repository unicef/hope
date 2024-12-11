import { AllTargetPopulationsQuery } from '../../src/__generated__/graphql';

export const fakeAllTargetPopulation = {
  {
    "allPaymentPlans": {
        "pageInfo": {
            "hasNextPage": true,
            "hasPreviousPage": false,
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
            "endCursor": "YXJyYXljb25uZWN0aW9uOjQ=",
            "__typename": "PageInfo"
        },
        "totalCount": 25,
        "edges": [
            {
                "cursor": "YXJyYXljb25uZWN0aW9uOjA=",
                "node": {
                    "id": "UGF5bWVudFBsYW5Ob2RlOmRjYTdlMTQzLTU4Y2UtNDQ0Mi1hMDY2LTY3ZTc2ZDA4YzljYg==",
                    "unicefId": "PP-0060-24-00000073",
                    "name": "tes tp",
                    "isFollowUp": false,
                    "followUps": {
                        "totalCount": 0,
                        "edges": [],
                        "__typename": "PaymentPlanNodeConnection"
                    },
                    "status": "LOCKED",
                    "createdBy": {
                        "id": "VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2",
                        "firstName": "Paulina",
                        "lastName": "Kujawa",
                        "email": "paulina.kujawa@kellton.com",
                        "__typename": "UserNode"
                    },
                    "program": {
                        "id": "UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw",
                        "name": "Test Program",
                        "__typename": "ProgramNode"
                    },
                    "targetPopulation": {
                        "id": "VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MDdkOGMwOGUtNzYxOS00NmUzLWJmM2UtMWIwYTk2ZjI5ZGRk",
                        "name": "tes tp",
                        "__typename": "TargetPopulationNode"
                    },
                    "currency": "ALL",
                    "currencyName": "Albanian lek",
                    "startDate": "2024-08-09",
                    "endDate": "2024-08-31",
                    "dispersionStartDate": "2024-08-09",
                    "dispersionEndDate": "2024-08-23",
                    "femaleChildrenCount": 5,
                    "femaleAdultsCount": 6,
                    "maleChildrenCount": 7,
                    "maleAdultsCount": 0,
                    "totalHouseholdsCount": 4,
                    "totalIndividualsCount": 18,
                    "totalEntitledQuantity": 0,
                    "totalDeliveredQuantity": 0,
                    "totalUndeliveredQuantity": 0,
                    "__typename": "PaymentPlanNode"
                },
                "__typename": "PaymentPlanNodeEdge"
            },
            {
                "cursor": "YXJyYXljb25uZWN0aW9uOjE=",
                "node": {
                    "id": "UGF5bWVudFBsYW5Ob2RlOjM2YTBkYWMwLWVlNjAtNDYyMC04MDk0LWI3Y2FjYjdjZjZlYQ==",
                    "unicefId": "PP-0060-24-00000072",
                    "name": "fdssdsdfsfdssdsdfsfdssdsdfs",
                    "isFollowUp": false,
                    "followUps": {
                        "totalCount": 0,
                        "edges": [],
                        "__typename": "PaymentPlanNodeConnection"
                    },
                    "status": "OPEN",
                    "createdBy": {
                        "id": "VXNlck5vZGU6NjZiN2MxMjMtMmRiOS00M2RjLWJlYTQtOTY5OTc5YjE3MjI5",
                        "firstName": "Jan",
                        "lastName": "Romaniak",
                        "email": "jan.romaniak@kellton.com",
                        "__typename": "UserNode"
                    },
                    "program": {
                        "id": "UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw",
                        "name": "Test Program",
                        "__typename": "ProgramNode"
                    },
                    "targetPopulation": {
                        "id": "VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZDE0ODJlMGMtNzJkMC00NDU3LWFkOWItMThmNzc1Zjg3MjVj",
                        "name": "fdssdsdfsfdssdsdfsfdssdsdfs",
                        "__typename": "TargetPopulationNode"
                    },
                    "currency": "AOA",
                    "currencyName": "Angolan kwanza",
                    "startDate": "2024-07-24",
                    "endDate": "2024-07-27",
                    "dispersionStartDate": "2024-07-24",
                    "dispersionEndDate": "2024-07-30",
                    "femaleChildrenCount": 0,
                    "femaleAdultsCount": 0,
                    "maleChildrenCount": 0,
                    "maleAdultsCount": 0,
                    "totalHouseholdsCount": 0,
                    "totalIndividualsCount": 0,
                    "totalEntitledQuantity": 0,
                    "totalDeliveredQuantity": 0,
                    "totalUndeliveredQuantity": 0,
                    "__typename": "PaymentPlanNode"
                },
                "__typename": "PaymentPlanNodeEdge"
            },
            {
                "cursor": "YXJyYXljb25uZWN0aW9uOjI=",
                "node": {
                    "id": "UGF5bWVudFBsYW5Ob2RlOmZmNTY4NWY0LTI1ZDEtNGI1YS1iMWU0LTFkNjRiN2ZkYThiMw==",
                    "unicefId": "PP-0060-24-00000063",
                    "name": "Test TP 1",
                    "isFollowUp": false,
                    "followUps": {
                        "totalCount": 0,
                        "edges": [],
                        "__typename": "PaymentPlanNodeConnection"
                    },
                    "status": "ACCEPTED",
                    "createdBy": {
                        "id": "VXNlck5vZGU6NjZiN2MxMjMtMmRiOS00M2RjLWJlYTQtOTY5OTc5YjE3MjI5",
                        "firstName": "Jan",
                        "lastName": "Romaniak",
                        "email": "jan.romaniak@kellton.com",
                        "__typename": "UserNode"
                    },
                    "program": {
                        "id": "UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw",
                        "name": "Test Program",
                        "__typename": "ProgramNode"
                    },
                    "targetPopulation": {
                        "id": "VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MzM3NDg0ZTAtYmVkMC00N2U0LWI2YzEtZWUyMmViNzFmZTY3",
                        "name": "Test TP 1",
                        "__typename": "TargetPopulationNode"
                    },
                    "currency": "ALL",
                    "currencyName": "Albanian lek",
                    "startDate": "2024-06-25",
                    "endDate": "2024-06-29",
                    "dispersionStartDate": "2024-06-25",
                    "dispersionEndDate": "2024-06-29",
                    "femaleChildrenCount": 45,
                    "femaleAdultsCount": 47,
                    "maleChildrenCount": 65,
                    "maleAdultsCount": 50,
                    "totalHouseholdsCount": 50,
                    "totalIndividualsCount": 207,
                    "totalEntitledQuantity": 10600,
                    "totalDeliveredQuantity": 0,
                    "totalUndeliveredQuantity": 10600,
                    "__typename": "PaymentPlanNode"
                },
                "__typename": "PaymentPlanNodeEdge"
            },
            {
                "cursor": "YXJyYXljb25uZWN0aW9uOjM=",
                "node": {
                    "id": "UGF5bWVudFBsYW5Ob2RlOjJjNDUwYzU1LWM4YWEtNDk5Ni1hMWU4LWU3OGYzMzgxYWVlNA==",
                    "unicefId": "PP-0060-24-00000057",
                    "name": "nazywam",
                    "isFollowUp": false,
                    "followUps": {
                        "totalCount": 0,
                        "edges": [],
                        "__typename": "PaymentPlanNodeConnection"
                    },
                    "status": "ACCEPTED",
                    "createdBy": {
                        "id": "VXNlck5vZGU6NmZiYTBhNDctN2U2Mi00ZjMyLWI0Y2EtNGNiNjkxZTk4ZmI0",
                        "firstName": "Szymon",
                        "lastName": "Wyderka",
                        "email": "szymon.wyderka@kellton.com",
                        "__typename": "UserNode"
                    },
                    "program": {
                        "id": "UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw",
                        "name": "Test Program",
                        "__typename": "ProgramNode"
                    },
                    "targetPopulation": {
                        "id": "VGFyZ2V0UG9wdWxhdGlvbk5vZGU6OTIyYzZiMmYtYWYxOS00NzM0LTg5M2QtZTg1YWM0NWQ4YjU1",
                        "name": "nazywam",
                        "__typename": "TargetPopulationNode"
                    },
                    "currency": "ARS",
                    "currencyName": "Argentine peso",
                    "startDate": "2024-06-12",
                    "endDate": "2024-06-14",
                    "dispersionStartDate": "2024-06-11",
                    "dispersionEndDate": "2024-06-21",
                    "femaleChildrenCount": 20,
                    "femaleAdultsCount": 5,
                    "maleChildrenCount": 13,
                    "maleAdultsCount": 4,
                    "totalHouseholdsCount": 10,
                    "totalIndividualsCount": 42,
                    "totalEntitledQuantity": 2120,
                    "totalDeliveredQuantity": 0,
                    "totalUndeliveredQuantity": 2120,
                    "__typename": "PaymentPlanNode"
                },
                "__typename": "PaymentPlanNodeEdge"
            },
            {
                "cursor": "YXJyYXljb25uZWN0aW9uOjQ=",
                "node": {
                    "id": "UGF5bWVudFBsYW5Ob2RlOjZiY2Y1NDFkLTliZGYtNGQ5Ny05NmYxLWU1M2MyZjYyZjkxMw==",
                    "unicefId": "PP-0060-24-00000056",
                    "name": null,
                    "isFollowUp": true,
                    "followUps": {
                        "totalCount": 0,
                        "edges": [],
                        "__typename": "PaymentPlanNodeConnection"
                    },
                    "status": "OPEN",
                    "createdBy": {
                        "id": "VXNlck5vZGU6NmZiYTBhNDctN2U2Mi00ZjMyLWI0Y2EtNGNiNjkxZTk4ZmI0",
                        "firstName": "Szymon",
                        "lastName": "Wyderka",
                        "email": "szymon.wyderka@kellton.com",
                        "__typename": "UserNode"
                    },
                    "program": {
                        "id": "UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw",
                        "name": "Test Program",
                        "__typename": "ProgramNode"
                    },
                    "targetPopulation": {
                        "id": "VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZmZlNjMyODQtYzFmOC00ZGI5LWE0MzktMzlkODI1ZTk3MjBi",
                        "name": "xxxxxxxx",
                        "__typename": "TargetPopulationNode"
                    },
                    "currency": "AWG",
                    "currencyName": "Aruban florin",
                    "startDate": "2024-04-01",
                    "endDate": "2024-04-02",
                    "dispersionStartDate": "2024-06-02",
                    "dispersionEndDate": "2024-06-29",
                    "femaleChildrenCount": 0,
                    "femaleAdultsCount": 5,
                    "maleChildrenCount": 0,
                    "maleAdultsCount": 3,
                    "totalHouseholdsCount": 1,
                    "totalIndividualsCount": 8,
                    "totalEntitledQuantity": 212,
                    "totalDeliveredQuantity": 0,
                    "totalUndeliveredQuantity": 212,
                    "__typename": "PaymentPlanNode"
                },
                "__typename": "PaymentPlanNodeEdge"
            }
        ],
        "__typename": "PaymentPlanNodeConnection"
}} as AllTargetPopulationsQuery;
