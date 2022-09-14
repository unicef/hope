# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestPaymentPlanQueries::test_fetch_all_payment_plans 1"] = {
    "data": {
        "allPaymentPlans": {
            "edges": [
                {
                    "node": {
                        "approvalNumberRequired": 2,
                        "approvalProcess": {"totalCount": 1},
                        "authorizationNumberRequired": 2,
                        "dispersionEndDate": "2020-12-10",
                        "dispersionStartDate": "2020-08-10",
                        "endDate": "2020-11-10",
                        "exchangeRate": 2.0,
                        "femaleAdultsCount": 0,
                        "femaleChildrenCount": 1,
                        "financeReviewNumberRequired": 3,
                        "maleAdultsCount": 0,
                        "maleChildrenCount": 1,
                        "paymentItems": {"totalCount": 2},
                        "paymentsConflictsCount": 1,
                        "startDate": "2020-09-10",
                        "status": "OPEN",
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
                    }
                },
                {
                    "node": {
                        "approvalNumberRequired": 2,
                        "approvalProcess": {"totalCount": 0},
                        "authorizationNumberRequired": 2,
                        "dispersionEndDate": "2020-10-10",
                        "dispersionStartDate": "2020-10-10",
                        "endDate": "2020-11-10",
                        "exchangeRate": 2.0,
                        "femaleAdultsCount": 1,
                        "femaleChildrenCount": 0,
                        "financeReviewNumberRequired": 3,
                        "maleAdultsCount": 1,
                        "maleChildrenCount": 0,
                        "paymentItems": {"totalCount": 2},
                        "paymentsConflictsCount": 0,
                        "startDate": "2020-09-10",
                        "status": "LOCKED",
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
                }
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

snapshots["TestPaymentPlanQueries::test_fetch_all_payments_for_locked_payment_plan 1"] = {
    "data": {
        "allPayments": {
            "edgeCount": 1,
            "edges": [
                {
                    "node": {
                        "deliveredQuantity": 50.0,
                        "deliveredQuantityUsd": 100.0,
                        "entitlementQuantity": 100.0,
                        "entitlementQuantityUsd": 200.0,
                        "excluded": False,
                        "parent": {"unicefId": "PP-02"},
                        "paymentPlanHardConflicted": False,
                        "paymentPlanHardConflictedData": [],
                        "paymentPlanSoftConflicted": True,
                        "paymentPlanSoftConflictedData": [
                            {
                                "paymentPlanEndDate": "2020-11-10",
                                "paymentPlanStartDate": "2020-09-10",
                                "paymentPlanStatus": "OPEN",
                            }
                        ],
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
                        "deliveredQuantity": 50.0,
                        "deliveredQuantityUsd": 100.0,
                        "entitlementQuantity": 100.0,
                        "entitlementQuantityUsd": 200.0,
                        "excluded": False,
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
                        "deliveredQuantity": 50.0,
                        "deliveredQuantityUsd": 100.0,
                        "entitlementQuantity": 100.0,
                        "entitlementQuantityUsd": 200.0,
                        "excluded": True,
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
            {"name": "Open", "value": "OPEN"},
            {"name": "Locked", "value": "LOCKED"},
            {"name": "Locked FSP", "value": "LOCKED_FSP"},
            {"name": "In Approval", "value": "IN_APPROVAL"},
            {"name": "In Authorization", "value": "IN_AUTHORIZATION"},
            {"name": "In Review", "value": "IN_REVIEW"},
            {"name": "Accepted", "value": "ACCEPTED"},
        ]
    }
}
