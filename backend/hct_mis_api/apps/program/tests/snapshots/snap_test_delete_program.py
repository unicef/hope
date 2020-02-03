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
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'deleteProgram'
            ]
        }
    ]
}

snapshots['TestDeleteProgram::test_delete_active_program 1'] = {
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

snapshots['TestDeleteProgram::test_delete_program_authenticated 1'] = {
    'data': {
        'deleteProgram': {
            'ok': True
        }
    }
}
