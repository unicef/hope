# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestUpdateProgram::test_update_program_not_authenticated 1'] = {
    'data': {
        'updateProgram': None
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
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_authenticated_0_with_permissions 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'name': 'updated name',
                'status': 'ACTIVE'
            }
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_authenticated_1_with_partial_permissions 1'] = {
    'data': {
        'updateProgram': None
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
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_authenticated_2_without_permissions 1'] = {
    'data': {
        'updateProgram': None
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
                'updateProgram'
            ]
        }
    ]
}
