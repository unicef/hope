# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_payment_verification_ticket_approve_payment_details_0_with_permission 1'] = {
    'data': {
        'approvePaymentDetails': {
            'grievanceTicket': {
                'paymentVerificationTicketDetails': {
                    'approveStatus': True
                }
            }
        }
    }
}

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_payment_verification_ticket_approve_payment_details_1_without_permission 1'] = {
    'data': {
        'approvePaymentDetails': None
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
                'approvePaymentDetails'
            ]
        }
    ]
}

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_update_payment_verification_ticket_with_new_received_amount_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'paymentVerificationTicketDetails': {
                    'newReceivedAmount': 1234.99,
                    'newStatus': 'RECEIVED'
                }
            }
        }
    }
}

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_update_payment_verification_ticket_with_new_received_amount_extras_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
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
                'updateGrievanceTicket'
            ]
        }
    ]
}
