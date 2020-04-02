# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCopyTargetPopulationMutation::test_copy_target 1'] = {
    'data': {
        'copyTargetPopulation': {
            'targetPopulation': {
                'candidateListTargetingCriteria': {
                    'rules': [
                        {
                            'filters': [
                                {
                                    'arguments': [
                                        1
                                    ],
                                    'comparisionMethod': 'EQUALS',
                                    'fieldName': 'family_size',
                                    'isFlexField': False
                                }
                            ]
                        }
                    ]
                },
                'candidateListTotalHouseholds': 1,
                'candidateListTotalIndividuals': 1,
                'finalListTargetingCriteria': {
                    'rules': [
                        {
                            'filters': [
                                {
                                    'arguments': [
                                        2
                                    ],
                                    'comparisionMethod': 'EQUALS',
                                    'fieldName': 'family_size',
                                    'isFlexField': False
                                }
                            ]
                        }
                    ]
                },
                'finalListTotalHouseholds': 0,
                'finalListTotalIndividuals': None,
                'name': 'Test New Copy Name',
                'status': 'APPROVED'
            }
        }
    }
}

snapshots['TestCopyTargetPopulationMutation::test_copy_empty_target_1 1'] = {
    'data': {
        'copyTargetPopulation': {
            'targetPopulation': {
                'candidateListTargetingCriteria': None,
                'candidateListTotalHouseholds': 0,
                'candidateListTotalIndividuals': None,
                'finalListTargetingCriteria': None,
                'finalListTotalHouseholds': 0,
                'finalListTotalIndividuals': None,
                'name': 'test_copy_empty_target_1',
                'status': 'APPROVED'
            }
        }
    }
}
