# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_0_wrong_args_count 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "'TargetingCriteriaRuleFilterObjectType' object has no attribute 'parametrizer'",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_1_wrong_comparison_method 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "'TargetingCriteriaRuleFilterObjectType' object has no attribute 'parametrizer'",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_2_unknown_comparison_method 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "['Unknown comparison method - BLABLA']",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_3_unknown_flex_field_name 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
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

snapshots['TestUpdateTargetPopulationMutation::test_fail_update_4_unknown_core_field_name 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
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

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_0_with_permission_draft 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "'TargetingCriteriaRuleFilterObjectType' object has no attribute 'parametrizer'",
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_1_without_permission_draft 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_2_with_permission_approved 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': '["Name can\'t be changed when Target Population is in Locked status"]',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUpdateTargetPopulationMutation::test_update_mutation_correct_variables_3_without_permission_approved 1'] = {
    'data': {
        'updateTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateTargetPopulation'
            ]
        }
    ]
}
