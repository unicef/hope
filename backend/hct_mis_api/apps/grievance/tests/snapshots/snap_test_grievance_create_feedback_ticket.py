# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateFeedbackTicketQuery::test_create_positive_feedback_ticket 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 7,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'status': 1
                }
            ]
        }
    }
}
