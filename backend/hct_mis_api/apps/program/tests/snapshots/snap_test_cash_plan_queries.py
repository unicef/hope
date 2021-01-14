# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCashPlanQueries::test_cash_plans_0_all_with_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "allCashPlans" on type "Query".'
        }
    ]
}

snapshots['TestCashPlanQueries::test_cash_plans_1_all_without_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "allCashPlans" on type "Query".'
        }
    ]
}

snapshots['TestCashPlanQueries::test_cash_plans_2_single_with_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "cashPlan" on type "Query".'
        }
    ]
}

snapshots['TestCashPlanQueries::test_cash_plans_3_single_without_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "cashPlan" on type "Query".'
        }
    ]
}
