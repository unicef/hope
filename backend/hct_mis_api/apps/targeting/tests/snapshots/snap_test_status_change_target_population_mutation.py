# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestApproveTargetPopulationMutation::test_approve_fail_target_population 1'] = {
    'data': {
        'lockTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only Target Population with status OPEN can be approved']",
            'path': [
                'lockTargetPopulation'
            ]
        }
    ]
}

snapshots['TestApproveTargetPopulationMutation::test_approve_target_population_0_with_permission 1'] = {
    'data': {
        'lockTargetPopulation': {
            'targetPopulation': {
                'householdList': {
                    'totalCount': 2
                },
                'status': 'LOCKED'
            }
        }
    }
}

snapshots['TestApproveTargetPopulationMutation::test_approve_target_population_1_without_permission 1'] = {
    'data': {
        'lockTargetPopulation': None
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
                'lockTargetPopulation'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_fail_target_population 1'] = {
    'data': {
        'finalizeTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only locked Target Population with status can be finalized']",
            'path': [
                'finalizeTargetPopulation'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_0_with_permission 1'] = {
    'data': {
        'finalizeTargetPopulation': {
            'targetPopulation': {
                'householdList': {
                    'totalCount': 2
                },
                'households': {
                    'totalCount': 2
                },
                'status': 'PROCESSING'
            }
        }
    }
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_1_without_permission 1'] = {
    'data': {
        'finalizeTargetPopulation': None
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
                'finalizeTargetPopulation'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_with_final_criteria 1'] = {
    'data': {
        'finalizeTargetPopulation': {
            'targetPopulation': {
                'householdList': {
                    'totalCount': 2
                },
                'households': {
                    'totalCount': 2
                },
                'status': 'PROCESSING'
            }
        }
    }
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_fail_target_population 1'] = {
    'data': {
        'unlockTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only locked Target Population with status can be unlocked']",
            'path': [
                'unlockTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_target_population_0_with_permission 1'] = {
    'data': {
        'unlockTargetPopulation': {
            'targetPopulation': {
                'households': {
                    'totalCount': 2
                },
                'status': 'OPEN'
            }
        }
    }
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_target_population_1_without_permission 1'] = {
    'data': {
        'unlockTargetPopulation': None
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
                'unlockTargetPopulation'
            ]
        }
    ]
}
