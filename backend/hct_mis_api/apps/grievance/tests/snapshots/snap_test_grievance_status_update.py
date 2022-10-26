# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_assign_user_0_with_permission 1'] = {
    'data': {
        'grievanceStatusChange': {
            'grievanceTicket': {
                'status': 2
            }
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_assign_user_1_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'grievanceStatusChange'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_status_change_0_with_permission 1'] = {
    'data': {
        'grievanceStatusChange': {
            'grievanceTicket': {
                'status': 2
            }
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_status_change_1_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'grievanceStatusChange'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_status_change_fail_0_with_permission 1'] = {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_status_change_fail_1_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'grievanceStatusChange'
            ]
        }
    ]
}
