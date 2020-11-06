# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_status_change 1'] = {
    'data': {
        'grievanceStatusChange': {
            'grievanceTicket': {
                'status': 2
            }
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_status_change_fail 1'] = {
    'data': {
        'grievanceStatusChange': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'New status is incorrect',
            'path': [
                'grievanceStatusChange'
            ]
        }
    ]
}
