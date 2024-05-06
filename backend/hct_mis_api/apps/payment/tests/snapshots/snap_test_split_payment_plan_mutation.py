# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSplitPaymentPlan::test_split_payment_plan_mutation 1'] = {
    'data': {
        'splitPaymentPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Payment plan with multiple delivery mechanisms cannot be split',
            'path': [
                'splitPaymentPlan'
            ]
        }
    ]
}

snapshots['TestSplitPaymentPlan::test_split_payment_plan_mutation 2'] = {
    'data': {
        'splitPaymentPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Payment plan is already sent to payment gateway',
            'path': [
                'splitPaymentPlan'
            ]
        }
    ]
}

snapshots['TestSplitPaymentPlan::test_split_payment_plan_mutation 3'] = {
    'data': {
        'splitPaymentPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "'>' not supported between instances of 'int' and 'MagicMock'",
            'path': [
                'splitPaymentPlan'
            ]
        }
    ]
}

snapshots['TestSplitPaymentPlan::test_split_payment_plan_mutation 4'] = {
    'data': {
        'splitPaymentPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "'>' not supported between instances of 'int' and 'MagicMock'",
            'path': [
                'splitPaymentPlan'
            ]
        }
    ]
}

snapshots['TestSplitPaymentPlan::test_split_payment_plan_mutation 5'] = {
    'data': {
        'splitPaymentPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Cannot split Payment Plan into more than 2 parts',
            'path': [
                'splitPaymentPlan'
            ]
        }
    ]
}

snapshots['TestSplitPaymentPlan::test_split_payment_plan_mutation 6'] = {
    'data': {
        'splitPaymentPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Payment Parts number should be between 10 and total number of payments',
            'path': [
                'splitPaymentPlan'
            ]
        }
    ]
}
