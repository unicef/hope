# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSurveyQueries::test_create_export_survey_sample_with_invalid_survey_id 1'] = {
    'data': {
        'exportSurveySample': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'No Survey matches the given query.',
            'path': [
                'exportSurveySample'
            ]
        }
    ]
}

snapshots['TestSurveyQueries::test_create_export_survey_sample_with_valid_survey_id 1'] = {
    'data': {
        'exportSurveySample': {
            'survey': {
                'targetPopulation': {
                    'name': 'Test Target Population'
                },
                'title': 'Test survey'
            }
        }
    }
}

snapshots['TestSurveyQueries::test_create_export_survey_sample_without_permissions 1'] = {
    'data': {
        'exportSurveySample': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'exportSurveySample'
            ]
        }
    ]
}
