# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDiscardVerificationMutation::test_discard_active_0_with_permission 1'] = {
    'data': {
        'discardCashPlanPaymentVerification': {
            'cashPlan': {
                'name': 'TEST',
                'verificationPlans': {
                    'edges': [
                        {
                            'node': {
                                'paymentRecordVerifications': {
                                    'edges': [
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        },
                                        {
                                            'node': {
                                                'status': 'PENDING'
                                            }
                                        }
                                    ]
                                },
                                'status': 'PENDING'
                            }
                        }
                    ]
                }
            }
        }
    }
}

snapshots['TestDiscardVerificationMutation::test_discard_active_1_without_permission 1'] = {
    'data': {
        'discardCashPlanPaymentVerification': None
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
                'discardCashPlanPaymentVerification'
            ]
        }
    ]
}
