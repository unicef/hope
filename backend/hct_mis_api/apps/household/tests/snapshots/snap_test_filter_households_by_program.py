# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestFilterHouseholdsByProgram::test_filter_households_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'program': {
                            'name': 'Test program ONE'
                        }
                    }
                },
                {
                    'node': {
                        'program': {
                            'name': 'Test program ONE'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['TestFilterHouseholdsByProgram::test_filter_households_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}
