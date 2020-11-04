# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateFeedbackTicketQuery::test_create_positive_feedback_ticket 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "'utf-8' codec can't decode byte 0xd7 in position 1: invalid continuation byte",
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}
