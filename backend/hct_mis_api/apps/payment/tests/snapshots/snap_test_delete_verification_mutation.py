# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestDeleteVerificationMutation::test_delete_pending_verification_plan_0_with_permission 1'] = {
    'data': {
        'deleteCashPlanPaymentVerification': {
            'cashPlan': {
                'name': 'TEST',
                'verificationPlans': {
                    'edges': [
                        {
                            'node': {
                                'status': 'ACTIVE'
                            }
                        }
                    ]
                }
            }
        }
    }
}

snapshots['TestDeleteVerificationMutation::test_delete_pending_verification_plan_1_without_permission 1'] = {
    'data': {
        'deleteCashPlanPaymentVerification': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'deleteCashPlanPaymentVerification'
            ]
        }
    ]
}

snapshots['TestDeleteVerificationMutation::test_delete_active_verification_plan_0_with_permission 1'] = {
    'data': {
        'deleteCashPlanPaymentVerification': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'You can delete only PENDING verification',
            'path': [
                'deleteCashPlanPaymentVerification'
            ]
        }
    ]
}

snapshots['TestDeleteVerificationMutation::test_delete_active_verification_plan_1_without_permission 1'] = {
    'data': {
        'deleteCashPlanPaymentVerification': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'deleteCashPlanPaymentVerification'
            ]
        }
    ]
}
