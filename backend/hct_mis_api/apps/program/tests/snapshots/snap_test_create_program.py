# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateProgram::test_create_program_authenticated 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': 20000000.0,
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20T15:00:00',
                'frequencyOfPayments': 'REGULAR',
                'name': 'Test',
                'populationGoal': 150000,
                'programCaId': '5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3',
                'scope': 'FULL',
                'sector': 'EDUCATION',
                'startDate': '2019-12-20T15:00:00',
                'status': 'DRAFT'
            }
        }
    }
}

snapshots['TestCreateProgram::test_create_program_not_authenticated 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_invalid_dates 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': 20000000.0,
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20T15:00:00',
                'frequencyOfPayments': 'REGULAR',
                'name': 'Test',
                'populationGoal': 150000,
                'programCaId': '5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3',
                'scope': 'FULL',
                'sector': 'EDUCATION',
                'startDate': '2019-12-20T15:00:00',
                'status': 'DRAFT'
            }
        }
    }
}
