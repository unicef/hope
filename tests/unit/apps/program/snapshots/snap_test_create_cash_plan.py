# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestCreateCashPlan::test_create_cash_plan_not_authenticated 1'] = {
    'data': {
        'createCashPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'createCashPlan'
            ]
        }
    ]
}

snapshots['TestCreateCashPlan::test_create_cash_plan_invalid_dates_authenticated 1'] = {
    'data': {
        'createCashPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Start date cannot be greater than the end date.',
            'path': [
                'createCashPlan'
            ]
        }
    ]
}

snapshots['TestCreateCashPlan::test_create_cash_plan_valid_dates_authenticated 1'] = {
    'data': {
        'createCashPlan': {
            'cashPlan': {
                'cashAssistId': '2b7f0db7-9010-4d1d-8b1f-19357b29c7b0',
                'coverageDuration': 45,
                'coverageUnits': 'Day(s)',
                'currency': 'Indian Rupee',
                'disbursementDate': '2023-10-23T15:00:32',
                'dispersionDate': '2023-10-22',
                'distributionModality': '363-39',
                'endDate': '2023-10-23T15:00:32',
                'fsp': 'Hayes LLC',
                'name': 'Test Cash Plan',
                'numberOfHouseholds': 514,
                'program': {
                    'name': 'Test program'
                },
                'startDate': '2020-12-16T13:15:32',
                'status': 'STARTED',
                'targetPopulation': {
                    'name': 'Test Target Population'
                },
                'totalDeliveredQuantity': 10000.0,
                'totalEntitledQuantity': 30000.0,
                'totalUndeliveredQuantity': 20000.0
            }
        }
    }
}
