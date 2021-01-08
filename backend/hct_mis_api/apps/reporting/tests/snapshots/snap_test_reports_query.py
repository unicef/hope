# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestReportsQuery::test_report_query_single 1'] = {
    'data': {
        'report': {
            'reportType': 1,
            'status': 1
        }
    }
}

snapshots['TestReportsQuery::test_reports_query_all_0_all 1'] = {
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

snapshots['TestReportsQuery::test_reports_query_all_1_filter_by_status 1'] = {
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

snapshots['TestReportsQuery::test_reports_query_all_2_filter_by_type 1'] = {
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
