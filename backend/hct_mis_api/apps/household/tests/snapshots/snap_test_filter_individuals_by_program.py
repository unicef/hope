# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestFilterIndividualsByProgram::test_individual_query_all_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
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

snapshots['TestFilterIndividualsByProgram::test_individual_query_all_1_without_permission 1'] = {
    'data': {
        'allIndividuals': None
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
                'allIndividuals'
            ]
        }
    ]
}
