# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_0_with_permission 1'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'name': 'Example name 5',
                'status': 'OPEN',
                'targetingCriteria': {
                    'rules': [
                        {
                            'filters': [
                                {
                                    'arguments': [
                                        3
                                    ],
                                    'comparisionMethod': 'EQUALS',
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

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_1_without_permission 1'] = {
    'data': {
        'createTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createTargetPopulation'
            ]
        }
    ]
}
