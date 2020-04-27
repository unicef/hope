# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestApproveTargetPopulationMutation::test_approve_fail_target_population 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 10
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['TestApproveTargetPopulationMutation::test_approve_target_population 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 10
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_fail_target_population 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 9
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        },
        {
            'locations': [
                {
                    'column': 25,
                    'line': 18
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 9
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        },
        {
            'locations': [
                {
                    'column': 25,
                    'line': 18
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_with_final_criteria 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 9
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        },
        {
            'locations': [
                {
                    'column': 25,
                    'line': 18
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_fail_target_population 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 10
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_target_population 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 10
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}
