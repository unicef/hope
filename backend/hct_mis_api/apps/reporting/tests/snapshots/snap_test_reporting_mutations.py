# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestReportingMutation::test_create_report_with_no_extra_filters_0_with_permission_individuals_report_with_earlier_dateTo 1'] = {
    'data': {
        'createReport': {
            'report': {
                'dateFrom': '2019-01-01',
                'dateTo': '2020-01-02',
                'reportType': 1,
                'status': 1
            }
        }
    }
}

snapshots['TestReportingMutation::test_create_report_with_no_extra_filters_1_with_permission_individuals_report_with_later_dateTo 1'] = {
    'data': {
        'createReport': {
            'report': {
                'dateFrom': '2019-01-01',
                'dateTo': '2022-01-02',
                'reportType': 1,
                'status': 1
            }
        }
    }
}

snapshots['TestReportingMutation::test_create_report_with_no_extra_filters_2_with_permission_households_report_with_earlier_dateTo 1'] = {
    'data': {
        'createReport': {
            'report': {
                'dateFrom': '2019-01-01',
                'dateTo': '2020-01-02',
                'reportType': 2,
                'status': 1
            }
        }
    }
}

snapshots['TestReportingMutation::test_create_report_with_no_extra_filters_3_with_permission_households_report_with_later_dateTo 1'] = {
    'data': {
        'createReport': {
            'report': {
                'dateFrom': '2019-01-01',
                'dateTo': '2022-01-02',
                'reportType': 2,
                'status': 1
            }
        }
    }
}

snapshots['TestReportingMutation::test_create_report_with_no_extra_filters_4_without_permission_individuals_report 1'] = {
    'data': {
        'createReport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createReport'
            ]
        }
    ]
}

snapshots['TestReportingMutation::test_restart_create_report_0_with_permission 1'] = {
    'data': {
        'restartCreateReport': {
            'report': {
                'reportType': 1,
                'status': 2
            }
        }
    }
}

snapshots['TestReportingMutation::test_restart_create_report_1_without_permission 1'] = {
    'data': {
        'restartCreateReport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'restartCreateReport'
            ]
        }
    ]
}

snapshots['TestReportingMutation::test_restart_create_report_invalid_status_update_time 1'] = {
    'data': {
        'restartCreateReport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': "Impossible restart now. Status must be 'Processing' and more than 30 mins after last running.",
            'path': [
                'restartCreateReport'
            ]
        }
    ]
}

snapshots['TestReportingMutation::test_restart_create_report_invalid_status_update_time 2'] = {
    'data': {
        'restartCreateReport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': "Impossible restart now. Status must be 'Processing' and more than 30 mins after last running.",
            'path': [
                'restartCreateReport'
            ]
        }
    ]
}
