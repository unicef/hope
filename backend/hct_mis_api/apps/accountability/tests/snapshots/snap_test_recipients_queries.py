# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSurveyQueries::test_query_list_0_without_permissions 1'] = {
    'data': {
        'recipients': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'recipients'
            ]
        }
    ]
}

snapshots['TestSurveyQueries::test_query_list_1_with_permissions 1'] = {
    'data': {
        'recipients': {
            'totalCount': 4
        }
    }
}
