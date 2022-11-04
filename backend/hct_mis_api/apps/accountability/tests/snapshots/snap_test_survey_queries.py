# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSurveyQueries::test_query_list_filter_by_created_by 1'] = {
    'data': {
        'allSurveys': {
            'totalCount': 4
        }
    }
}

snapshots['TestSurveyQueries::test_query_list_filter_by_search 1'] = {
    'data': {
        'allSurveys': {
            'totalCount': 1
        }
    }
}

snapshots['TestSurveyQueries::test_query_list_filter_by_target_population 1'] = {
    'data': {
        'allSurveys': {
            'totalCount': 4
        }
    }
}

snapshots['TestSurveyQueries::test_query_list_without_permissions 1'] = {
    'data': {
        'allSurveys': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allSurveys'
            ]
        }
    ]
}

snapshots['TestSurveyQueries::test_single_survey_0_without_permission 1'] = {
    'data': {
        'survey': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'survey'
            ]
        }
    ]
}

snapshots['TestSurveyQueries::test_single_survey_1_with_permission 1'] = {
    'data': {
        'survey': {
            'body': '',
            'createdBy': {
                'firstName': 'John',
                'lastName': 'Wick'
            },
            'numberOfRecipients': 0,
            'title': 'Test survey single'
        }
    }
}
