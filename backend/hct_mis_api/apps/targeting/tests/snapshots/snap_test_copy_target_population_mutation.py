# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCopyTargetPopulationMutation::test_copy_empty_target_1_0_with_permission 1'] = {
    'data': {
        'copyTargetPopulation': {
            'targetPopulation': {
                'name': 'test_copy_empty_target_1',
                'status': 'OPEN',
                'targetingCriteria': None,
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCopyTargetPopulationMutation::test_copy_empty_target_1_1_without_permission 1'] = {
    'data': {
        'copyTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'copyTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCopyTargetPopulationMutation::test_copy_target_0_with_permission 1'] = {
    'data': {
        'copyTargetPopulation': {
            'targetPopulation': {
                'name': 'Test New Copy Name',
                'status': 'OPEN',
                'targetingCriteria': {
                    'rules': [
                        {
                            'filters': [
                                {
                                    'arguments': [
                                        1
                                    ],
                                    'comparisonMethod': 'EQUALS',
                                    'fieldName': 'size',
                                    'isFlexField': False
                                }
                            ]
                        }
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCopyTargetPopulationMutation::test_copy_target_1_without_permission 1'] = {
    'data': {
        'copyTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'copyTargetPopulation'
            ]
        }
    ]
}
