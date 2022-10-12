# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUpdateGrievanceTickets::test_bulk_update_grievance_assignee_0_with_permission 1'] = {
    'data': {
        'bulkUpdateGrievanceAssignee': {
            'grievanceTickets': [
                {
                    'assignedTo': {
                        'firstName': 'user_two'
                    }
                },
                {
                    'assignedTo': {
                        'firstName': 'user_two'
                    }
                },
                {
                    'assignedTo': {
                        'firstName': 'user_two'
                    }
                }
            ]
        }
    }
}

snapshots['TestUpdateGrievanceTickets::test_bulk_update_grievance_assignee_1_without_permission 1'] = {
    'data': {
        'bulkUpdateGrievanceAssignee': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'bulkUpdateGrievanceAssignee'
            ]
        }
    ]
}
