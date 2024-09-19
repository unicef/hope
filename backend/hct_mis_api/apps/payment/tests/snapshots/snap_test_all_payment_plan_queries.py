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
                        'canCreateFollowUp': False,
                        'dispersionEndDate': '2020-12-10',
                        'dispersionStartDate': '2020-08-10',
                        'exchangeRate': 2.0,
                        'femaleAdultsCount': 0,
                        'femaleChildrenCount': 1,
                        'maleAdultsCount': 0,
                        'maleChildrenCount': 1,
                        'paymentItems': {
                            'totalCount': 2
                        },
                        'paymentsConflictsCount': 1,
                        'programCycle': {
                            'endDate': '2020-11-10',
                            'startDate': '2020-09-10'
                        },
                        'status': 'OPEN',
                        'supportingDocuments': [
                            {
                                'title': 'Test File 123'
                            }
                        ],
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
                        'canCreateFollowUp': False,
                        'dispersionEndDate': '2020-10-10',
                        'dispersionStartDate': '2020-10-10',
                        'exchangeRate': 2.0,
                        'femaleAdultsCount': 1,
                        'femaleChildrenCount': 0,
                        'maleAdultsCount': 1,
                        'maleChildrenCount': 0,
                        'paymentItems': {
                            'totalCount': 2
                        },
                        'paymentsConflictsCount': 0,
                        'programCycle': {
                            'endDate': '2020-11-10',
                            'startDate': '2020-09-10'
                        },
                        'status': 'LOCKED',
                        'supportingDocuments': [
                        ],
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
