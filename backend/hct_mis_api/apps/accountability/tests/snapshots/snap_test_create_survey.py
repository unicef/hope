# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateSurvey::test_create_survey 1'] = {
    'data': {
        'createSurvey': {
            'survey': {
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Doe'
                },
                'numberOfRecipients': 3,
                'title': 'Test survey'
            }
        }
    }
}

snapshots['TestCreateSurvey::test_create_survey_without_permission 1'] = {
    'data': {
        'createSurvey': None
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
                'createSurvey'
            ]
        }
    ]
}

snapshots['TestCreateSurvey::test_create_survey_without_recipients 1'] = {
    'data': {
        'createSurvey': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['No recipients found for the given criteria.']",
            'path': [
                'createSurvey'
            ]
        }
    ]
}

snapshots['TestCreateSurvey::test_create_survey_without_target_population_and_program 1'] = {
    'data': {
        'createSurvey': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['Target population or program should be provided.']",
            'path': [
                'createSurvey'
            ]
        }
    ]
}
