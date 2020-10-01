# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_draft_mutation_unknown_comparision_method 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['Unknown comparision method - BLABLA']",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_draft_mutation_unknown_core_field_name 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': '["Can\'t find any core field attribute associated with foo_bar field name"]',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_draft_mutation_unknown_flex_field_name 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': '["Can\'t find any flex field attribute associated with foo_bar field name"]',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_draft_mutation_wrong_args_count 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['Comparision method - EQUALS expect 1 arguments, 2 given']",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_draft_mutation_wrong_comparision_method 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['size is INTEGER type filter and does not accept - CONTAINS comparision method']",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_approved_mutation 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "'NoneType' object has no attribute 'individual_data_needed'",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_draft_mutation 1'] = {
    'data': {
        'updateTargetPopulation': {
            'targetPopulation': {
                'candidateListTargetingCriteria': {
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
                'candidateListTotalHouseholds': 2,
                'candidateListTotalIndividuals': 6,
                'finalListTargetingCriteria': None,
                'finalListTotalHouseholds': None,
                'finalListTotalIndividuals': None,
                'name': 'draft_target_population updated',
                'status': 'DRAFT'
            }
        }
    }
}
