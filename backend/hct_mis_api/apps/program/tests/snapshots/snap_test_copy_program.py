# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCopyProgram::test_update_program_authenticated_0_with_permissions 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'populationGoal': 150000,
                'scope': 'UNICEF',
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            }
        }
    }
}

snapshots['TestCopyProgram::test_update_program_authenticated_1_without_permissions 1'] = {
    'data': {
        'copyProgram': None
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
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_update_program_not_authenticated 1'] = {
    'data': {
        'copyProgram': None
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
                'copyProgram'
            ]
        }
    ]
}
