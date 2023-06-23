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
                'rapidProUrl': 'https://rapidpro.io/flow/results/flow123/',
                'title': 'Test survey'
            }
        }
    }
}

snapshots['TestCreateSurvey::test_create_survey_and_send_via_rapidpro 1'] = {
    'data': {
        'createSurvey': {
            'survey': {
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Doe'
                },
                'numberOfRecipients': 3,
                'rapidProUrl': 'https://rapidpro.io/flow/results/flow123/',
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
            'message': 'There are no selected recipients.',
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

snapshots['TestCreateSurvey::test_getting_available_flows 1'] = {
    'data': {
        'availableFlows': [
            {
                'id': '123',
                'name': 'flow2'
            },
            {
                'id': '234',
                'name': 'flow2'
            }
        ]
    }
}
