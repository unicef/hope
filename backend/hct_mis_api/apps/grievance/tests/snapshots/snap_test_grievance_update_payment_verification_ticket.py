# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_payment_verification_ticket_approve_payment_details_0_with_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': '''Syntax Error GraphQL (7:13) Expected Name, found }

6:             grievanceTicket {
7:             }
               ^
8:           }
'''
        }
    ]
}

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_payment_verification_ticket_approve_payment_details_1_without_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': '''Syntax Error GraphQL (7:13) Expected Name, found }

6:             grievanceTicket {
7:             }
               ^
8:           }
'''
        }
    ]
}

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_update_payment_verification_ticket_with_new_received_amount_extras_0_with_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': '''Syntax Error GraphQL (7:13) Expected Name, found }

6:             grievanceTicket {
7:             }
               ^
8:           }
'''
        }
    ]
}

snapshots['TestGrievanceUpdatePaymentVerificationTicketQuery::test_update_payment_verification_ticket_with_new_received_amount_extras_1_without_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': '''Syntax Error GraphQL (7:13) Expected Name, found }

6:             grievanceTicket {
7:             }
               ^
8:           }
'''
        }
    ]
}
