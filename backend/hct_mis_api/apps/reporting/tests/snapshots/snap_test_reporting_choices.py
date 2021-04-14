# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestProgramChoices::test_report_types_choices 1'] = {
    'data': {
        'reportTypesChoices': [
            {
                'name': 'Individuals',
                'value': '1'
            },
            {
                'name': 'Household Demographics',
                'value': '2'
            },
            {
                'name': 'Cash Plan Verification',
                'value': '3'
            },
            {
                'name': 'Payments',
                'value': '4'
            },
            {
                'name': 'Payment verification',
                'value': '5'
            },
            {
                'name': 'Cash Plan',
                'value': '6'
            },
            {
                'name': 'Program',
                'value': '7'
            },
            {
                'name': 'Individuals and Payment',
                'value': '8'
            }
        ]
    }
}

snapshots['TestProgramChoices::test_status_choices_query 1'] = {
    'data': {
        'reportStatusChoices': [
            {
                'name': 'Processing',
                'value': '1'
            },
            {
                'name': 'Generated',
                'value': '2'
            },
            {
                'name': 'Failed',
                'value': '3'
            }
        ]
    }
}
