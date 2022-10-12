# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestCreatePaymentVerificationMutation::test_create_cash_plan_payment_verification_0_with_permission 1'] = {
    'data': {
        'createPaymentVerificationPlan': {
            'cashPlan': {
                'id': 'Q2FzaFBsYW5Ob2RlOjBlMjkyN2FmLWM4NGQtNDg1Mi1iYjBiLTc3M2VmZTA1OWUwNQ=='
            }
        }
    }
}

snapshots['TestCreatePaymentVerificationMutation::test_create_cash_plan_payment_verification_1_without_permission 1'] = {
    'data': {
        'createPaymentVerificationPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createPaymentVerificationPlan'
            ]
        }
    ]
}

snapshots['TestCreatePaymentVerificationMutation::test_create_cash_plan_payment_verification_when_invalid_arguments 1'] = {
    'data': {
        'createPaymentVerificationPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'You have to provide full_list_arguments in FULL_LIST',
            'path': [
                'createPaymentVerificationPlan'
            ]
        }
    ]
}

snapshots['TestCreatePaymentVerificationMutation::test_create_cash_plan_payment_verification_when_invalid_arguments 2'] = {
    'data': {
        'createPaymentVerificationPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'You have to provide random_sampling_arguments in RANDOM',
            'path': [
                'createPaymentVerificationPlan'
            ]
        }
    ]
}

snapshots['TestCreatePaymentVerificationMutation::test_create_cash_plan_payment_verification_when_invalid_arguments 3'] = {
    'data': {
        'createPaymentVerificationPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': "You can't provide full_list_arguments in RANDOM",
            'path': [
                'createPaymentVerificationPlan'
            ]
        }
    ]
}

snapshots['TestCreatePaymentVerificationMutation::test_can_t_create_cash_plan_payment_verification_when_there_are_not_available_payment_record 1'] = {
    'data': {
        'createPaymentVerificationPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'There are no payment records that could be assigned to a new verification plan.',
            'path': [
                'createPaymentVerificationPlan'
            ]
        }
    ]
}
