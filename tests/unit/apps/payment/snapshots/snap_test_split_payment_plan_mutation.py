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
            'message': 'Payment plan is already sent to payment gateway',
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
            'message': 'Payment plan must be accepted to make a split',
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
            'message': 'Payment Number is required for split by records',
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
            'message': 'No payments to split',
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
        'splitPaymentPlan': {
            'paymentPlan': {
                'status': 'ACCEPTED'
            }
        }
    }
}

snapshots['TestSplitPaymentPlan::test_split_payment_plan_mutation 7'] = {
    'data': {
        'splitPaymentPlan': {
            'paymentPlan': {
                'status': 'ACCEPTED'
            }
        }
    }
}
