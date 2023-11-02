# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateProgram::test_create_program_authenticated_0_with_permission 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': 'partial_individuals',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'Test',
                'populationGoal': 150000,
                'scope': 'UNICEF',
                'sector': 'EDUCATION',
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_authenticated_1_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_authenticated_2_with_permission_but_invalid_dates 1'] = {
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
            'message': 'Start date cannot be greater than the end date.',
            'path': [
                'createProgram'
            ]
        }
    ]
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

snapshots['TestCreateProgram::test_create_program_with_dct_from_other_ba 1'] = {
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
            'message': "This Data Collection Type is not assigned to the Program's Business Area",
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_deprecated_dct 1'] = {
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
            'message': 'Avoid using the deprecated DataCollectingType in Program',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_inactive_dct 1'] = {
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
            'message': 'Only active DataCollectingType can be used in Program',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_without_dct 1'] = {
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
            'message': "['DataCollectingType is required for creating new Program']",
            'path': [
                'createProgram'
            ]
        }
    ]
}
