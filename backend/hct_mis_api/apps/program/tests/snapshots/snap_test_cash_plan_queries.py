# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCashPlanQueries::test_cash_plans_0_all_with_permission 1'] = {
    'data': {
        'allCashPlans': {
            'edges': [
                {
                    'node': {
                        'assistanceMeasurement': 'Cuban peso',
                        'assistanceThrough': 'Cairo Amman Bank',
                        'caId': '04b9d44b-67fe-425c-9095-509e31ba7494',
                        'coverageDuration': 19,
                        'coverageUnit': 'Week(s)',
                        'deliveryType': 'Deposit to Card',
                        'dispersionDate': '2020-02-22T00:00:00+00:00',
                        'endDate': '2028-03-31T18:44:15+00:00',
                        'name': 'Despite action TV after.',
                        'startDate': '2041-06-14T10:15:44+00:00',
                        'status': 'TRANSACTION_COMPLETED',
                        'totalDeliveredQuantity': 41935107.03,
                        'totalEntitledQuantity': 38204833.92,
                        'totalPersonsCovered': 100,
                        'totalUndeliveredQuantity': 63098825.46
                    }
                },
                {
                    'node': {
                        'assistanceMeasurement': 'Syrian pound',
                        'assistanceThrough': 'Cairo Amman Bank',
                        'caId': '7ff3542c-8c48-4ed4-8283-41966093995b',
                        'coverageDuration': 21,
                        'coverageUnit': 'Day(s)',
                        'deliveryType': 'Deposit to Card',
                        'dispersionDate': '2020-04-25T00:00:00+00:00',
                        'endDate': '2064-03-14T22:52:54+00:00',
                        'name': 'Far yet reveal area bar almost dinner.',
                        'startDate': '2051-11-30T00:02:09+00:00',
                        'status': 'TRANSACTION_COMPLETED',
                        'totalDeliveredQuantity': 53477453.27,
                        'totalEntitledQuantity': 56657648.82,
                        'totalPersonsCovered': 540,
                        'totalUndeliveredQuantity': 55497021.04
                    }
                }
            ]
        }
    }
}

snapshots['TestCashPlanQueries::test_cash_plans_1_all_without_permission 1'] = {
    'data': {
        'allCashPlans': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allCashPlans'
            ]
        }
    ]
}

snapshots['TestCashPlanQueries::test_cash_plans_2_single_with_permission 1'] = {
    'data': {
        'cashPlan': {
            'assistanceMeasurement': 'Syrian pound',
            'assistanceThrough': 'Cairo Amman Bank',
            'caId': '7ff3542c-8c48-4ed4-8283-41966093995b',
            'coverageDuration': 21,
            'coverageUnit': 'Day(s)',
            'deliveryType': 'Deposit to Card',
            'dispersionDate': '2020-04-25T00:00:00+00:00',
            'endDate': '2064-03-14T22:52:54+00:00',
            'name': 'Far yet reveal area bar almost dinner.',
            'startDate': '2051-11-30T00:02:09+00:00',
            'status': 'TRANSACTION_COMPLETED',
            'totalDeliveredQuantity': 53477453.27,
            'totalEntitledQuantity': 56657648.82,
            'totalPersonsCovered': 540,
            'totalUndeliveredQuantity': 55497021.04
        }
    }
}

snapshots['TestCashPlanQueries::test_cash_plans_3_single_without_permission 1'] = {
    'data': {
        'cashPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'cashPlan'
            ]
        }
    ]
}
