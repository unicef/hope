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
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'isFollowUp': False,
                        'listOfPaymentPlans': [
                            '56aca38c-dc16-48a9-ace4-70d88b41d462',
                            '5b04f7c3-579a-48dd-a232-424daaefffe7'
                        ],
                        'sourcePaymentPlan': None,
                        'unicefId': 'PP-01'
                    }
                },
                {
                    'node': {
                        'dispersionEndDate': '2020-10-10',
                        'dispersionStartDate': '2020-10-10',
                        'isFollowUp': False,
                        'listOfPaymentPlans': [
                        ],
                        'sourcePaymentPlan': None,
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
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'isFollowUp': True,
                        'listOfPaymentPlans': [
                        ],
                        'sourcePaymentPlan': {
                            'unicefId': 'PP-01'
                        },
                        'unicefId': 'PP-0060-20-00000005'
                    }
                },
                {
                    'node': {
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'isFollowUp': True,
                        'listOfPaymentPlans': [
                        ],
                        'sourcePaymentPlan': {
                            'unicefId': 'PP-01'
                        },
                        'unicefId': 'PP-0060-20-00000006'
                    }
                }
            ]
        }
    }
}
