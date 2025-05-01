# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestPaymentPlanQueries::test_all_payment_plans_filter_by_delivery_types 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "status": "OPEN",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-01",
                    }
                },
                {
                    "node": {
                        "dispersionEndDate": "2020-10-10",
                        "dispersionStartDate": "2020-10-10",
                        "status": "LOCKED",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-02",
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_all_payment_verification_log_entries 1"] = {
    "data": {
        "allPaymentVerificationLogEntries": {
            "edges": [{"node": {"action": "CREATE", "isUserGenerated": None}}],
            "totalCount": 1,
        }
    }
}

snapshots["TestPaymentPlanQueries::test_all_payments_filter_by_household_id 1"] = {
    "data": {
        "allPayments": {
            "edgeCount": 1,
            "edges": [
                {
                    "node": {
                        "conflicted": False,
                        "deliveredQuantity": 50.0,
                        "deliveredQuantityUsd": 100.0,
                        "entitlementQuantity": 100.0,
                        "entitlementQuantityUsd": 200.0,
                        "fspAuthCode": "",
                        "parent": {"unicefId": "PP-01"},
                        "paymentPlanHardConflicted": False,
                        "paymentPlanHardConflictedData": [],
                        "paymentPlanSoftConflicted": False,
                        "paymentPlanSoftConflictedData": [],
                        "unicefId": "RCPT-0060-20-0.000.001",
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "approvalProcess": {
                            "edges": [
                                {
                                    "node": {
                                        "approvalNumberRequired": 2,
                                        "authorizationNumberRequired": 2,
                                        "financeReleaseNumberRequired": 3,
                                    }
                                }
                            ],
                            "totalCount": 1,
                        },
                        "availablePaymentRecordsCount": 0,
                        "canCreateFollowUp": False,
                        "canCreateXlsxWithFspAuthCode": False,
                        "canDownloadXlsx": False,
                        "canExportXlsx": False,
                        "canSendToPaymentGateway": False,
                        "canSendXlsxPassword": False,
                        "canSplit": False,
                        "currencyName": "Polish złoty",
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "exchangeRate": 2.0,
                        "excludedHouseholds": [],
                        "excludedIndividuals": [],
                        "femaleAdultsCount": 0,
                        "femaleChildrenCount": 1,
                        "fspCommunicationChannel": "XLSX",
                        "hasFspDeliveryMechanismXlsxTemplate": False,
                        "hasPaymentListExportFile": False,
                        "importedFileName": "",
                        "maleAdultsCount": 0,
                        "maleChildrenCount": 1,
                        "paymentItems": {"totalCount": 2},
                        "paymentsConflictsCount": 1,
                        "program": {"name": "Test All PP QS"},
                        "programCycle": {"endDate": "2020-11-10", "startDate": "2020-09-10"},
                        "splitChoices": [
                            {"name": "By Admin Area 1", "value": "BY_ADMIN_AREA1"},
                            {"name": "By Admin Area 2", "value": "BY_ADMIN_AREA2"},
                            {"name": "By Admin Area 3", "value": "BY_ADMIN_AREA3"},
                            {"name": "By Collector", "value": "BY_COLLECTOR"},
                            {"name": "By Records", "value": "BY_RECORDS"},
                            {"name": "No Split", "value": "NO_SPLIT"},
                        ],
                        "status": "OPEN",
                        "supportingDocuments": [{"title": "Test File 123"}],
                        "totalDeliveredQuantity": 50.0,
                        "totalDeliveredQuantityUsd": 100.0,
                        "totalEntitledQuantity": 100.0,
                        "totalEntitledQuantityRevised": 0.0,
                        "totalEntitledQuantityRevisedUsd": 0.0,
                        "totalEntitledQuantityUsd": 200.0,
                        "totalHouseholdsCount": 1,
                        "totalIndividualsCount": 2,
                        "totalUndeliveredQuantity": 50.0,
                        "totalUndeliveredQuantityUsd": 100.0,
                        "unicefId": "PP-01",
                        "unsuccessfulPaymentsCount": 0,
                        "verificationPlans": {"totalCount": 0},
                    }
                },
                {
                    "node": {
                        "approvalProcess": {"edges": [], "totalCount": 0},
                        "availablePaymentRecordsCount": 0,
                        "canCreateFollowUp": False,
                        "canCreateXlsxWithFspAuthCode": False,
                        "canDownloadXlsx": False,
                        "canExportXlsx": False,
                        "canSendToPaymentGateway": False,
                        "canSendXlsxPassword": False,
                        "canSplit": False,
                        "currencyName": "Ukrainian hryvnia",
                        "dispersionEndDate": "2020-10-10",
                        "dispersionStartDate": "2020-10-10",
                        "exchangeRate": 2.0,
                        "excludedHouseholds": [],
                        "excludedIndividuals": [],
                        "femaleAdultsCount": 1,
                        "femaleChildrenCount": 0,
                        "fspCommunicationChannel": "XLSX",
                        "hasFspDeliveryMechanismXlsxTemplate": False,
                        "hasPaymentListExportFile": False,
                        "importedFileName": "",
                        "maleAdultsCount": 1,
                        "maleChildrenCount": 0,
                        "paymentItems": {"totalCount": 2},
                        "paymentsConflictsCount": 0,
                        "program": {"name": "Test All PP QS"},
                        "programCycle": {"endDate": "2020-11-10", "startDate": "2020-09-10"},
                        "splitChoices": [
                            {"name": "By Admin Area 1", "value": "BY_ADMIN_AREA1"},
                            {"name": "By Admin Area 2", "value": "BY_ADMIN_AREA2"},
                            {"name": "By Admin Area 3", "value": "BY_ADMIN_AREA3"},
                            {"name": "By Collector", "value": "BY_COLLECTOR"},
                            {"name": "By Records", "value": "BY_RECORDS"},
                            {"name": "No Split", "value": "NO_SPLIT"},
                        ],
                        "status": "LOCKED",
                        "supportingDocuments": [],
                        "totalDeliveredQuantity": 50.0,
                        "totalDeliveredQuantityUsd": 100.0,
                        "totalEntitledQuantity": 100.0,
                        "totalEntitledQuantityRevised": 0.0,
                        "totalEntitledQuantityRevisedUsd": 0.0,
                        "totalEntitledQuantityUsd": 200.0,
                        "totalHouseholdsCount": 1,
                        "totalIndividualsCount": 2,
                        "totalUndeliveredQuantity": 50.0,
                        "totalUndeliveredQuantityUsd": 100.0,
                        "unicefId": "PP-02",
                        "unsuccessfulPaymentsCount": 0,
                        "verificationPlans": {"totalCount": 0},
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "status": "OPEN",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-01",
                    }
                },
                {
                    "node": {
                        "dispersionEndDate": "2020-10-10",
                        "dispersionStartDate": "2020-10-10",
                        "status": "LOCKED",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-02",
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 2"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-10-10",
                        "dispersionStartDate": "2020-10-10",
                        "status": "LOCKED",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-02",
                    }
                }
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 3"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "status": "OPEN",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-01",
                    }
                },
                {
                    "node": {
                        "dispersionEndDate": "2020-10-10",
                        "dispersionStartDate": "2020-10-10",
                        "status": "LOCKED",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-02",
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 4"] = {
    "data": {"allPaymentPlans": {"edges": []}}
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 5"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "status": "OPEN",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-01",
                    }
                }
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 6"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "status": "OPEN",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-01",
                    }
                }
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 7"] = {
    "data": {"allPaymentPlans": {"edges": []}}
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 8"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "status": "OPEN",
                        "totalEntitledQuantity": 100.0,
                        "unicefId": "PP-01",
                    }
                }
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payments_for_locked_payment_plan 1"] = {
    "data": {
        "allPayments": {
            "edgeCount": 1,
            "edges": [
                {
                    "node": {
                        "conflicted": False,
                        "deliveredQuantity": 50.0,
                        "deliveredQuantityUsd": 100.0,
                        "entitlementQuantity": 100.0,
                        "entitlementQuantityUsd": 200.0,
                        "fspAuthCode": "",
                        "parent": {"unicefId": "PP-02"},
                        "paymentPlanHardConflicted": False,
                        "paymentPlanHardConflictedData": [],
                        "paymentPlanSoftConflicted": False,
                        "paymentPlanSoftConflictedData": [],
                        "unicefId": "RCPT-0060-20-0.000.003",
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_all_payments_for_open_payment_plan 1"] = {
    "data": {
        "allPayments": {
            "edgeCount": 2,
            "edges": [
                {
                    "node": {
                        "conflicted": False,
                        "deliveredQuantity": 50.0,
                        "deliveredQuantityUsd": 100.0,
                        "entitlementQuantity": 100.0,
                        "entitlementQuantityUsd": 200.0,
                        "fspAuthCode": "123",
                        "parent": {"unicefId": "PP-01"},
                        "paymentPlanHardConflicted": False,
                        "paymentPlanHardConflictedData": [],
                        "paymentPlanSoftConflicted": False,
                        "paymentPlanSoftConflictedData": [],
                        "unicefId": "RCPT-0060-20-0.000.001",
                    }
                },
                {
                    "node": {
                        "conflicted": True,
                        "deliveredQuantity": 50.0,
                        "deliveredQuantityUsd": 100.0,
                        "entitlementQuantity": 100.0,
                        "entitlementQuantityUsd": 200.0,
                        "fspAuthCode": "",
                        "parent": {"unicefId": "PP-01"},
                        "paymentPlanHardConflicted": True,
                        "paymentPlanHardConflictedData": [
                            {
                                "paymentPlanEndDate": "2020-11-10",
                                "paymentPlanStartDate": "2020-09-10",
                                "paymentPlanStatus": "LOCKED",
                            }
                        ],
                        "paymentPlanSoftConflicted": False,
                        "paymentPlanSoftConflictedData": [],
                        "unicefId": "RCPT-0060-20-0.000.002",
                    }
                },
            ],
            "totalCount": 2,
        }
    }
}

snapshots["TestPaymentPlanQueries::test_fetch_payment_plan_status_choices 1"] = {
    "data": {
        "paymentPlanStatusChoices": [
            {"name": "Accepted", "value": "ACCEPTED"},
            {"name": "Draft", "value": "DRAFT"},
            {"name": "Finished", "value": "FINISHED"},
            {"name": "In Approval", "value": "IN_APPROVAL"},
            {"name": "In Authorization", "value": "IN_AUTHORIZATION"},
            {"name": "In Review", "value": "IN_REVIEW"},
            {"name": "Locked", "value": "TP_LOCKED"},
            {"name": "Locked", "value": "LOCKED"},
            {"name": "Locked FSP", "value": "LOCKED_FSP"},
            {"name": "Open", "value": "TP_OPEN"},
            {"name": "Open", "value": "OPEN"},
            {"name": "Preparing", "value": "PREPARING"},
            {"name": "Processing", "value": "PROCESSING"},
            {"name": "Steficon Completed", "value": "STEFICON_COMPLETED"},
            {"name": "Steficon Error", "value": "STEFICON_ERROR"},
            {"name": "Steficon Run", "value": "STEFICON_RUN"},
            {"name": "Steficon Wait", "value": "STEFICON_WAIT"},
        ]
    }
}

snapshots["TestPaymentPlanQueries::test_filter_payment_plans_with_source_id 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "followUps": {"edges": [], "totalCount": 0},
                        "isFollowUp": True,
                        "sourcePaymentPlan": {"unicefId": "PP-01"},
                        "unicefId": "PP-0060-20-00000003",
                    }
                },
                {
                    "node": {
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "followUps": {"edges": [], "totalCount": 0},
                        "isFollowUp": True,
                        "sourcePaymentPlan": {"unicefId": "PP-01"},
                        "unicefId": "PP-0060-20-00000004",
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_node_with_legacy_data 1"] = {
    "data": {
        "payment": {
            "additionalCollectorName": None,
            "fullName": "First1 Mid1 Last1",
            "reasonForUnsuccessfulPayment": "reason 123",
            "snapshotCollectorBankAccountNumber": None,
            "snapshotCollectorBankName": None,
            "snapshotCollectorDebitCardNumber": None,
            "snapshotCollectorDeliveryPhoneNo": None,
            "snapshotCollectorFullName": None,
            "totalPersonsCovered": 5,
            "verification": None,
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_node_with_legacy_data 2"] = {
    "data": {
        "payment": {
            "additionalCollectorName": "AddCollectorName11",
            "fullName": "First2 Mid2 Last3",
            "reasonForUnsuccessfulPayment": "reason 222",
            "snapshotCollectorBankAccountNumber": "PrimaryCollBankNumber",
            "snapshotCollectorBankName": "PrimaryCollBankName",
            "snapshotCollectorDebitCardNumber": "PrimaryCollDebitCardNumber",
            "snapshotCollectorDeliveryPhoneNo": "1111111",
            "snapshotCollectorFullName": "PrimaryCollectorFullName",
            "totalPersonsCovered": 99,
            "verification": None,
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_node_with_legacy_data 3"] = {
    "data": {
        "payment": {
            "additionalCollectorName": "AddCollectorName22",
            "fullName": "First3 Mid3 Last3",
            "reasonForUnsuccessfulPayment": "reason 333",
            "snapshotCollectorBankAccountNumber": "AlternateCollBankNumber",
            "snapshotCollectorBankName": "AlternateCollBankName",
            "snapshotCollectorDebitCardNumber": "AlternateCollDebitCardNumber",
            "snapshotCollectorDeliveryPhoneNo": "222222222",
            "snapshotCollectorFullName": "AlternateCollectorFullName",
            "totalPersonsCovered": 55,
            "verification": None,
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_available_funds_commitments 1"] = {
    "data": {"paymentPlan": {"availableFundsCommitments": [], "status": "IN_REVIEW"}}
}

snapshots["TestPaymentPlanQueries::test_payment_plan_available_funds_commitments 2"] = {
    "data": {
        "paymentPlan": {
            "availableFundsCommitments": [
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "001", "paymentPlan": None, "recSerialNumber": 1},
                        {"fundsCommitmentItem": "002", "paymentPlan": None, "recSerialNumber": 2},
                    ],
                    "fundsCommitmentNumber": "123",
                },
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "001", "paymentPlan": None, "recSerialNumber": 3},
                        {"fundsCommitmentItem": "002", "paymentPlan": None, "recSerialNumber": 4},
                    ],
                    "fundsCommitmentNumber": "345",
                },
            ],
            "status": "IN_REVIEW",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_available_funds_commitments 3"] = {
    "data": {
        "paymentPlan": {
            "availableFundsCommitments": [
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "002", "paymentPlan": None, "recSerialNumber": 2},
                        {"fundsCommitmentItem": "001", "paymentPlan": {"name": "FC TEST"}, "recSerialNumber": 1},
                    ],
                    "fundsCommitmentNumber": "123",
                },
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "001", "paymentPlan": None, "recSerialNumber": 3},
                        {"fundsCommitmentItem": "002", "paymentPlan": None, "recSerialNumber": 4},
                    ],
                    "fundsCommitmentNumber": "345",
                },
            ],
            "status": "IN_REVIEW",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_available_funds_commitments 4"] = {
    "data": {
        "paymentPlan": {
            "availableFundsCommitments": [
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "001", "paymentPlan": {"name": "FC TEST"}, "recSerialNumber": 1},
                        {"fundsCommitmentItem": "002", "paymentPlan": {"name": "FC TEST"}, "recSerialNumber": 2},
                    ],
                    "fundsCommitmentNumber": "123",
                },
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "001", "paymentPlan": None, "recSerialNumber": 3},
                        {"fundsCommitmentItem": "002", "paymentPlan": None, "recSerialNumber": 4},
                    ],
                    "fundsCommitmentNumber": "345",
                },
            ],
            "status": "IN_REVIEW",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_available_funds_commitments 5"] = {
    "data": {
        "paymentPlan": {
            "availableFundsCommitments": [
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "001", "paymentPlan": {"name": "FC TEST"}, "recSerialNumber": 1},
                        {"fundsCommitmentItem": "002", "paymentPlan": {"name": "FC TEST"}, "recSerialNumber": 2},
                    ],
                    "fundsCommitmentNumber": "123",
                },
                {
                    "fundsCommitmentItems": [{"fundsCommitmentItem": "002", "paymentPlan": None, "recSerialNumber": 4}],
                    "fundsCommitmentNumber": "345",
                },
            ],
            "status": "IN_REVIEW",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_available_funds_commitments 6"] = {
    "data": {
        "paymentPlan": {
            "availableFundsCommitments": [
                {
                    "fundsCommitmentItems": [
                        {"fundsCommitmentItem": "001", "paymentPlan": {"name": "FC TEST"}, "recSerialNumber": 1},
                        {"fundsCommitmentItem": "002", "paymentPlan": {"name": "FC TEST"}, "recSerialNumber": 2},
                    ],
                    "fundsCommitmentNumber": "123",
                }
            ],
            "status": "IN_REVIEW",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_is_payment_plan 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "Payment Plan within FINISHED status",
                        "status": "FINISHED",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                },
                {"node": {"name": "Main Payment Plan", "status": "OPEN", "totalHouseholdsCountWithValidPhoneNo": 1}},
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_is_payment_plan 2"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "Payment Plan within FINISHED status",
                        "status": "FINISHED",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                },
                {"node": {"name": "Main Payment Plan", "status": "OPEN", "totalHouseholdsCountWithValidPhoneNo": 1}},
                {
                    "node": {
                        "name": "Payment Plan within TP_LOCK status",
                        "status": "TP_LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_is_target_population 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "Payment Plan within DRAFT status",
                        "status": "DRAFT",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
                {
                    "node": {
                        "name": "Payment Plan within TP_LOCK status",
                        "status": "TP_LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_is_target_population 2"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "Payment Plan within DRAFT status",
                        "status": "DRAFT",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                },
                {"node": {"name": "Main Payment Plan", "status": "OPEN", "totalHouseholdsCountWithValidPhoneNo": 1}},
                {
                    "node": {
                        "name": "Payment Plan within TP_LOCK status",
                        "status": "TP_LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_name 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                }
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_not_status 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                }
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_status_assigned 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                },
                {"node": {"name": "Main Payment Plan", "status": "OPEN", "totalHouseholdsCountWithValidPhoneNo": 1}},
                {"node": {"name": "NEW TP OPEN", "status": "TP_OPEN", "totalHouseholdsCountWithValidPhoneNo": 0}},
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_status_assigned 2"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [{"node": {"name": "NEW TP OPEN", "status": "TP_OPEN", "totalHouseholdsCountWithValidPhoneNo": 0}}]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_total_households_count_max 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "Payment Plan with 2 payments",
                        "status": "DRAFT",
                        "totalHouseholdsCountWithValidPhoneNo": 2,
                    }
                },
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                },
                {"node": {"name": "Main Payment Plan", "status": "OPEN", "totalHouseholdsCountWithValidPhoneNo": 1}},
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_total_households_count_min 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "Payment Plan with 3 payments",
                        "status": "DRAFT",
                        "totalHouseholdsCountWithValidPhoneNo": 3,
                    }
                },
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                },
                {"node": {"name": "Main Payment Plan", "status": "OPEN", "totalHouseholdsCountWithValidPhoneNo": 1}},
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_total_households_count_with_valid_phone_no_max_2 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "PaymentPlan with conflicts",
                        "status": "LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 1,
                    }
                },
                {"node": {"name": "Main Payment Plan", "status": "OPEN", "totalHouseholdsCountWithValidPhoneNo": 1}},
                {
                    "node": {
                        "name": "Payment Plan just random with invalid phone numbers",
                        "status": "PROCESSING",
                        "totalHouseholdsCountWithValidPhoneNo": 0,
                    }
                },
                {
                    "node": {
                        "name": "Payment Plan with valid 2 phone numbers",
                        "status": "TP_LOCKED",
                        "totalHouseholdsCountWithValidPhoneNo": 2,
                    }
                },
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plan_filter_total_households_count_with_valid_phone_no_min_2 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "name": "Payment Plan with valid 2 phone numbers",
                        "status": "DRAFT",
                        "totalHouseholdsCountWithValidPhoneNo": 2,
                    }
                }
            ]
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plans_export_download_properties_0_with_permission_api 1"] = {
    "data": {
        "paymentPlan": {
            "canCreateXlsxWithFspAuthCode": True,
            "canDownloadXlsx": False,
            "canExportXlsx": True,
            "canSendToPaymentGateway": False,
            "canSendXlsxPassword": False,
            "fspCommunicationChannel": "API",
            "name": "Test Finished PP",
            "status": "FINISHED",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plans_export_download_properties_1_without_permission_api 1"] = {
    "data": {
        "paymentPlan": {
            "canCreateXlsxWithFspAuthCode": True,
            "canDownloadXlsx": False,
            "canExportXlsx": False,
            "canSendToPaymentGateway": False,
            "canSendXlsxPassword": False,
            "fspCommunicationChannel": "API",
            "name": "Test Finished PP",
            "status": "FINISHED",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plans_export_download_properties_2_with_permission_xlsx 1"] = {
    "data": {
        "paymentPlan": {
            "canCreateXlsxWithFspAuthCode": False,
            "canDownloadXlsx": False,
            "canExportXlsx": False,
            "canSendToPaymentGateway": False,
            "canSendXlsxPassword": False,
            "fspCommunicationChannel": "XLSX",
            "name": "Test Finished PP",
            "status": "FINISHED",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plans_export_download_properties_3_without_permission_xlsx 1"] = {
    "data": {
        "paymentPlan": {
            "canCreateXlsxWithFspAuthCode": False,
            "canDownloadXlsx": False,
            "canExportXlsx": False,
            "canSendToPaymentGateway": False,
            "canSendXlsxPassword": False,
            "fspCommunicationChannel": "XLSX",
            "name": "Test Finished PP",
            "status": "FINISHED",
        }
    }
}

snapshots["TestPaymentPlanQueries::test_payment_plans_with_targeting_criteria 1"] = {
    "data": {
        "paymentPlan": {
            "name": "Test PP with TargetingCriteria",
            "status": "TP_OPEN",
            "targetingCriteria": {
                "flagExcludeIfActiveAdjudicationTicket": False,
                "flagExcludeIfOnSanctionList": False,
                "householdIds": "HH-1, HH-2",
                "individualIds": "IND-01, IND-02",
            },
        }
    }
}
