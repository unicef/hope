# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGetProgram::test_user_access_program_with_his_partner 1'] = {
    'data': {
        'program': {
            'endDate': '2023-11-21',
            'name': 'test_program',
            'startDate': '2023-11-11',
            'status': 'ACTIVE'
        }
    }
}

snapshots['TestGetProgram::test_user_does_not_access_program_with_another_partner 1'] = {
    'data': {
        'program': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'program'
            ]
        }
    ]
}
