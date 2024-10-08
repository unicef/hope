# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestReportsQuery::test_reports_query_all_0_all_with_permissions 1'] = {
    'data': {
        'allReports': {
            'edges': [
                {
                    'node': {
                        'reportType': 1,
                        'status': 1
                    }
                },
                {
                    'node': {
                        'reportType': 4,
                        'status': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestReportsQuery::test_reports_query_all_1_all_without_permissions 1'] = {
    'data': {
        'allReports': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allReports'
            ]
        }
    ]
}

snapshots['TestReportsQuery::test_reports_query_all_2_filter_by_status_with_permissions 1'] = {
    'data': {
        'allReports': {
            'edges': [
                {
                    'node': {
                        'reportType': 1,
                        'status': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestReportsQuery::test_reports_query_all_3_filter_by_status_without_permissions 1'] = {
    'data': {
        'allReports': None
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
                'allReports'
            ]
        }
    ]
}

snapshots['TestReportsQuery::test_reports_query_all_4_filter_by_type_with_permissions 1'] = {
    'data': {
        'allReports': {
            'edges': [
                {
                    'node': {
                        'reportType': 1,
                        'status': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestReportsQuery::test_report_query_single_0_with_permissions 1'] = {
    'data': {
        'report': {
            'reportType': 1,
            'status': 1
        }
    }
}

snapshots['TestReportsQuery::test_report_query_single_1_without_permissions 1'] = {
    'data': {
        'report': None
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
                'report'
            ]
        }
    ]
}
