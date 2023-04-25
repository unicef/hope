# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPaymentPlanQueries::test_fetch_all_payment_plans 1'] = {
    'data': {
        'allPaymentPlans': {
            'edges': [
                {
                    'node': {
                        'approvalProcess': {
                            'edges': [
                                {
                                    'node': {
                                        'approvalNumberRequired': 2,
                                        'authorizationNumberRequired': 2,
                                        'financeReleaseNumberRequired': 3
                                    }
                                }
                            ],
                            'totalCount': 1
                        },
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'endDate': '2020-11-10',
                        'exchangeRate': 2.0,
                        'femaleAdultsCount': 0,
                        'femaleChildrenCount': 1,
                        'maleAdultsCount': 0,
                        'maleChildrenCount': 1,
                        'paymentItems': {
                            'totalCount': 2
                        },
                        'paymentsConflictsCount': 1,
                        'startDate': '2020-09-10',
                        'status': 'OPEN',
                        'totalDeliveredQuantity': 50.0,
                        'totalDeliveredQuantityUsd': 100.0,
                        'totalEntitledQuantity': 100.0,
                        'totalEntitledQuantityRevised': 0.0,
                        'totalEntitledQuantityRevisedUsd': 0.0,
                        'totalEntitledQuantityUsd': 200.0,
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2,
                        'totalUndeliveredQuantity': 50.0,
                        'totalUndeliveredQuantityUsd': 100.0,
                        'unicefId': 'PP-01'
                    }
                },
                {
                    'node': {
                        'approvalProcess': {
                            'edges': [
                            ],
                            'totalCount': 0
                        },
                        'dispersionEndDate': '2020-10-10',
                        'dispersionStartDate': '2020-10-10',
                        'endDate': '2020-11-10',
                        'exchangeRate': 2.0,
                        'femaleAdultsCount': 1,
                        'femaleChildrenCount': 0,
                        'maleAdultsCount': 1,
                        'maleChildrenCount': 0,
                        'paymentItems': {
                            'totalCount': 2
                        },
                        'paymentsConflictsCount': 0,
                        'startDate': '2020-09-10',
                        'status': 'LOCKED',
                        'totalDeliveredQuantity': 50.0,
                        'totalDeliveredQuantityUsd': 100.0,
                        'totalEntitledQuantity': 100.0,
                        'totalEntitledQuantityRevised': 0.0,
                        'totalEntitledQuantityRevisedUsd': 0.0,
                        'totalEntitledQuantityUsd': 200.0,
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2,
                        'totalUndeliveredQuantity': 50.0,
                        'totalUndeliveredQuantityUsd': 100.0,
                        'unicefId': 'PP-02'
                    }
                }
            ]
        }
    }
}

snapshots['TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 1'] = {
    'data': {
        'allPaymentPlans': {
            'edges': [
                {
                    'node': {
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'status': 'OPEN',
                        'totalEntitledQuantity': 100.0,
                        'unicefId': 'PP-01'
                    }
                }
            ]
        }
    }
}

snapshots['TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 2'] = {
    'data': {
        'allPaymentPlans': {
            'edges': [
                {
                    'node': {
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'status': 'OPEN',
                        'totalEntitledQuantity': 100.0,
                        'unicefId': 'PP-01'
                    }
                }
            ]
        }
    }
}

snapshots['TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 3'] = {
    'data': {
        'allPaymentPlans': {
            'edges': [
                {
                    'node': {
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'status': 'OPEN',
                        'totalEntitledQuantity': 100.0,
                        'unicefId': 'PP-01'
                    }
                },
                {
                    'node': {
                        'dispersionEndDate': '2020-10-10',
                        'dispersionStartDate': '2020-10-10',
                        'status': 'LOCKED',
                        'totalEntitledQuantity': 100.0,
                        'unicefId': 'PP-02'
                    }
                }
            ]
        }
    }
}

snapshots['TestPaymentPlanQueries::test_fetch_all_payment_plans_filters 4'] = {
    'data': {
        'allPaymentPlans': {
            'edges': [
                {
                    'node': {
                        'dispersionEndDate': '2020-10-10',
                        'dispersionStartDate': '2020-10-10',
                        'status': 'LOCKED',
                        'totalEntitledQuantity': 100.0,
                        'unicefId': 'PP-02'
                    }
                }
            ]
        }
    }
}

snapshots['TestPaymentPlanQueries::test_fetch_all_payments_for_locked_payment_plan 1'] = {
    'data': {
        'allPayments': {
            'edgeCount': 1,
            'edges': [
                {
                    'node': {
                        'conflicted': False,
                        'deliveredQuantity': 50.0,
                        'deliveredQuantityUsd': 100.0,
                        'entitlementQuantity': 100.0,
                        'entitlementQuantityUsd': 200.0,
                        'parent': {
                            'unicefId': 'PP-02'
                        },
                        'paymentPlanHardConflicted': False,
                        'paymentPlanHardConflictedData': [
                        ],
                        'paymentPlanSoftConflicted': False,
                        'paymentPlanSoftConflictedData': [
                        ],
                        'unicefId': 'RCPT-0060-20-0.000.003'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['TestPaymentPlanQueries::test_fetch_all_payments_for_open_payment_plan 1'] = {
    'data': {
        'allPayments': {
            'edgeCount': 2,
            'edges': [
                {
                    'node': {
                        'conflicted': False,
                        'deliveredQuantity': 50.0,
                        'deliveredQuantityUsd': 100.0,
                        'entitlementQuantity': 100.0,
                        'entitlementQuantityUsd': 200.0,
                        'parent': {
                            'unicefId': 'PP-01'
                        },
                        'paymentPlanHardConflicted': False,
                        'paymentPlanHardConflictedData': [
                        ],
                        'paymentPlanSoftConflicted': False,
                        'paymentPlanSoftConflictedData': [
                        ],
                        'unicefId': 'RCPT-0060-20-0.000.001'
                    }
                },
                {
                    'node': {
                        'conflicted': True,
                        'deliveredQuantity': 50.0,
                        'deliveredQuantityUsd': 100.0,
                        'entitlementQuantity': 100.0,
                        'entitlementQuantityUsd': 200.0,
                        'parent': {
                            'unicefId': 'PP-01'
                        },
                        'paymentPlanHardConflicted': True,
                        'paymentPlanHardConflictedData': [
                            {
                                'paymentPlanEndDate': '2020-11-10',
                                'paymentPlanStartDate': '2020-09-10',
                                'paymentPlanStatus': 'LOCKED'
                            }
                        ],
                        'paymentPlanSoftConflicted': False,
                        'paymentPlanSoftConflictedData': [
                        ],
                        'unicefId': 'RCPT-0060-20-0.000.002'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['TestPaymentPlanQueries::test_fetch_payment_plan_status_choices 1'] = {
    'data': {
        'paymentPlanStatusChoices': [
            {
                'name': 'Accepted',
                'value': 'ACCEPTED'
            },
            {
                'name': 'Finished',
                'value': 'FINISHED'
            },
            {
                'name': 'In Approval',
                'value': 'IN_APPROVAL'
            },
            {
                'name': 'In Authorization',
                'value': 'IN_AUTHORIZATION'
            },
            {
                'name': 'In Review',
                'value': 'IN_REVIEW'
            },
            {
                'name': 'Locked',
                'value': 'LOCKED'
            },
            {
                'name': 'Locked FSP',
                'value': 'LOCKED_FSP'
            },
            {
                'name': 'Open',
                'value': 'OPEN'
            },
            {
                'name': 'Preparing',
                'value': 'PREPARING'
            }
        ]
    }
}

snapshots['TestPaymentPlanQueries::test_filter_payment_plans_with_follow_up_flag 1'] = {
    'data': {
        'allPaymentPlans': {
            'edges': [
                {
                    'node': {
                        'approvalProcess': {
                            'edges': [
                            ],
                            'totalCount': 0
                        },
                        'dispersionEndDate': '2029-12-08',
                        'dispersionStartDate': '2027-10-17',
                        'endDate': '2023-07-15',
                        'exchangeRate': 0.29,
                        'femaleAdultsCount': 2,
                        'femaleChildrenCount': 3,
                        'isFollowUp': False,
                        'listOfPaymentPlans': [
                            '3e06a2b6-70a0-48b2-9023-164c0d7edbb1',
                            'ee4fb70d-df30-4b6b-aefe-29f33fee621d'
                        ],
                        'maleAdultsCount': 4,
                        'maleChildrenCount': 2,
                        'paymentItems': {
                            'totalCount': 0
                        },
                        'paymentsConflictsCount': 0,
                        'sourcePaymentPlan': None,
                        'startDate': '2020-12-16',
                        'status': 'OPEN',
                        'totalDeliveredQuantity': 2793438.97,
                        'totalDeliveredQuantityUsd': 59130967.11,
                        'totalEntitledQuantity': 85482360.06,
                        'totalEntitledQuantityRevised': 0.0,
                        'totalEntitledQuantityRevisedUsd': 0.0,
                        'totalEntitledQuantityUsd': 25539245.06,
                        'totalHouseholdsCount': 2,
                        'totalIndividualsCount': 8,
                        'totalUndeliveredQuantity': 70077767.68,
                        'totalUndeliveredQuantityUsd': 78936197.05,
                        'unicefId': 'PP-0060-23-00000003'
                    }
                },
                {
                    'node': {
                        'approvalProcess': {
                            'edges': [
                                {
                                    'node': {
                                        'approvalNumberRequired': 2,
                                        'authorizationNumberRequired': 2,
                                        'financeReleaseNumberRequired': 3
                                    }
                                }
                            ],
                            'totalCount': 1
                        },
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'endDate': '2020-11-10',
                        'exchangeRate': 2.0,
                        'femaleAdultsCount': 0,
                        'femaleChildrenCount': 1,
                        'isFollowUp': False,
                        'listOfPaymentPlans': [
                        ],
                        'maleAdultsCount': 0,
                        'maleChildrenCount': 1,
                        'paymentItems': {
                            'totalCount': 2
                        },
                        'paymentsConflictsCount': 1,
                        'sourcePaymentPlan': None,
                        'startDate': '2020-09-10',
                        'status': 'OPEN',
                        'totalDeliveredQuantity': 50.0,
                        'totalDeliveredQuantityUsd': 100.0,
                        'totalEntitledQuantity': 100.0,
                        'totalEntitledQuantityRevised': 0.0,
                        'totalEntitledQuantityRevisedUsd': 0.0,
                        'totalEntitledQuantityUsd': 200.0,
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2,
                        'totalUndeliveredQuantity': 50.0,
                        'totalUndeliveredQuantityUsd': 100.0,
                        'unicefId': 'PP-01'
                    }
                },
                {
                    'node': {
                        'approvalProcess': {
                            'edges': [
                            ],
                            'totalCount': 0
                        },
                        'dispersionEndDate': '2020-10-10',
                        'dispersionStartDate': '2020-10-10',
                        'endDate': '2020-11-10',
                        'exchangeRate': 2.0,
                        'femaleAdultsCount': 1,
                        'femaleChildrenCount': 0,
                        'isFollowUp': False,
                        'listOfPaymentPlans': [
                        ],
                        'maleAdultsCount': 1,
                        'maleChildrenCount': 0,
                        'paymentItems': {
                            'totalCount': 2
                        },
                        'paymentsConflictsCount': 0,
                        'sourcePaymentPlan': None,
                        'startDate': '2020-09-10',
                        'status': 'LOCKED',
                        'totalDeliveredQuantity': 50.0,
                        'totalDeliveredQuantityUsd': 100.0,
                        'totalEntitledQuantity': 100.0,
                        'totalEntitledQuantityRevised': 0.0,
                        'totalEntitledQuantityRevisedUsd': 0.0,
                        'totalEntitledQuantityUsd': 200.0,
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2,
                        'totalUndeliveredQuantity': 50.0,
                        'totalUndeliveredQuantityUsd': 100.0,
                        'unicefId': 'PP-02'
                    }
                }
            ]
        }
    }
}

snapshots['TestPaymentPlanQueries::test_filter_payment_plans_with_source_id 1'] = {
    'data': {
        'allPaymentPlans': {
            'edges': [
                {
                    'node': {
                        'approvalProcess': {
                            'edges': [
                            ],
                            'totalCount': 0
                        },
                        'dispersionEndDate': '2023-09-26',
                        'dispersionStartDate': '2023-07-12',
                        'endDate': '2023-06-19',
                        'exchangeRate': 6.75,
                        'femaleAdultsCount': 2,
                        'femaleChildrenCount': 2,
                        'isFollowUp': True,
                        'listOfPaymentPlans': [
                        ],
                        'maleAdultsCount': 3,
                        'maleChildrenCount': 4,
                        'paymentItems': {
                            'totalCount': 0
                        },
                        'paymentsConflictsCount': 0,
                        'sourcePaymentPlan': {
                            'id': 'UGF5bWVudFBsYW5Ob2RlOmQxMjk4MDI2LTU3Y2QtNDA2YS1hMTIwLThiNTc5NWE2NmE3MQ=='
                        },
                        'startDate': '2022-12-15',
                        'status': 'OPEN',
                        'totalDeliveredQuantity': 71581388.61,
                        'totalDeliveredQuantityUsd': 15199018.8,
                        'totalEntitledQuantity': 54691567.29,
                        'totalEntitledQuantityRevised': 0.0,
                        'totalEntitledQuantityRevisedUsd': 0.0,
                        'totalEntitledQuantityUsd': 25314668.26,
                        'totalHouseholdsCount': 3,
                        'totalIndividualsCount': 11,
                        'totalUndeliveredQuantity': 86129941.77,
                        'totalUndeliveredQuantityUsd': 23290710.28,
                        'unicefId': 'PP-0060-23-00000004'
                    }
                },
                {
                    'node': {
                        'approvalProcess': {
                            'edges': [
                            ],
                            'totalCount': 0
                        },
                        'dispersionEndDate': '2027-11-01',
                        'dispersionStartDate': '2027-08-09',
                        'endDate': '2023-09-23',
                        'exchangeRate': 7.09,
                        'femaleAdultsCount': 4,
                        'femaleChildrenCount': 4,
                        'isFollowUp': True,
                        'listOfPaymentPlans': [
                        ],
                        'maleAdultsCount': 4,
                        'maleChildrenCount': 2,
                        'paymentItems': {
                            'totalCount': 0
                        },
                        'paymentsConflictsCount': 0,
                        'sourcePaymentPlan': {
                            'id': 'UGF5bWVudFBsYW5Ob2RlOmQxMjk4MDI2LTU3Y2QtNDA2YS1hMTIwLThiNTc5NWE2NmE3MQ=='
                        },
                        'startDate': '2021-04-25',
                        'status': 'OPEN',
                        'totalDeliveredQuantity': 3559682.95,
                        'totalDeliveredQuantityUsd': 10268303.3,
                        'totalEntitledQuantity': 11242797.9,
                        'totalEntitledQuantityRevised': 0.0,
                        'totalEntitledQuantityRevisedUsd': 0.0,
                        'totalEntitledQuantityUsd': 16895634.42,
                        'totalHouseholdsCount': 4,
                        'totalIndividualsCount': 8,
                        'totalUndeliveredQuantity': 46801546.21,
                        'totalUndeliveredQuantityUsd': 63897585.11,
                        'unicefId': 'PP-0060-23-00000005'
                    }
                }
            ]
        }
    }
}
