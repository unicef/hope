# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestProgramChoices::test_dashboard_years_choices 1'] = {
    'data': {
        'dashboardYearsChoices': [
            '2021',
            '2020'
        ]
    }
}

snapshots['TestProgramChoices::test_dashboard_years_choices__no_objects 1'] = {
    'data': {
        'dashboardYearsChoices': [
            '2021',
            '2020'
        ]
    }
}

snapshots['TestProgramChoices::test_report_types_choices 1'] = {
    'data': {
        'reportTypesChoices': [
            {
                'name': 'Cash Plan',
                'value': '6'
            },
            {
                'name': 'Cash Plan Verification',
                'value': '3'
            },
            {
                'name': 'Grievances',
                'value': '9'
            },
            {
                'name': 'Households',
                'value': '2'
            },
            {
                'name': 'Individuals',
                'value': '1'
            },
            {
                'name': 'Individuals & Payment',
                'value': '8'
            },
            {
                'name': 'Payment Plan',
                'value': '10'
            },
            {
                'name': 'Payment verification',
                'value': '5'
            },
            {
                'name': 'Payments',
                'value': '4'
            },
        ]
    }
}

snapshots['TestProgramChoices::test_status_choices_query 1'] = {
    'data': {
        'reportStatusChoices': [
            {
                'name': 'Failed',
                'value': '3'
            },
            {
                'name': 'Generated',
                'value': '2'
            },
            {
                'name': 'Processing',
                'value': '1'
            }
        ]
    }
}
