# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDeleteProgram::test_delete_program_not_authenticated 1'] = {
    'data': {
        'deleteProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "'AnonymousUser' object has no attribute 'email'",
            'path': [
                'deleteProgram'
            ]
        }
    ]
}

snapshots['TestDeleteProgram::test_delete_program_authenticated_0_with_permission_in_draft 1'] = {
    'data': {
        'deleteProgram': {
            'ok': True
        }
    }
}

snapshots['TestDeleteProgram::test_delete_program_authenticated_1_without_permission_in_draft 1'] = {
    'data': {
        'deleteProgram': None
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
                'deleteProgram'
            ]
        }
    ]
}

snapshots['TestDeleteProgram::test_delete_program_authenticated_2_with_permission_in_active 1'] = {
    'data': {
        'deleteProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Only Draft Program can be deleted.',
            'path': [
                'deleteProgram'
            ]
        }
    ]
}
