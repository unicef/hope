# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestApproveTargetPopulationMutation::test_approve_fail_target_population 1'] = {
    'data': {
        'approveTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only Target Population with status DRAFT can be approved']",
            'path': [
                'approveTargetPopulation'
            ]
        }
    ]
}

snapshots['TestApproveTargetPopulationMutation::test_approve_target_population 1'] = {
    'data': {
        'approveTargetPopulation': {
            'targetPopulation': {
                'households': {
                    'edges': [
                        {
                            'node': None
                        },
                        {
                            'node': None
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'APPROVED'
            }
        }
    },
    'errors': [
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'approveTargetPopulation',
                'targetPopulation',
                'households',
                'edges',
                0,
                'node',
                'residenceStatus'
            ]
        },
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'approveTargetPopulation',
                'targetPopulation',
                'households',
                'edges',
                1,
                'node',
                'residenceStatus'
            ]
        }
    ]
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_fail_target_population 1'] = {
    'data': {
        'unapproveTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only Target Population with status APPROVED can be unapproved']",
            'path': [
                'unapproveTargetPopulation'
            ]
        }
    ]
}

snapshots['TestUnapproveTargetPopulationMutation::test_unapprove_target_population 1'] = {
    'data': {
        'unapproveTargetPopulation': {
            'targetPopulation': {
                'households': {
                    'edges': [
                        {
                            'node': None
                        },
                        {
                            'node': None
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'DRAFT'
            }
        }
    },
    'errors': [
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'unapproveTargetPopulation',
                'targetPopulation',
                'households',
                'edges',
                0,
                'node',
                'residenceStatus'
            ]
        },
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'unapproveTargetPopulation',
                'targetPopulation',
                'households',
                'edges',
                1,
                'node',
                'residenceStatus'
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
            'message': "['Only Target Population with status APPROVED can be finalized']",
            'path': [
                'finalizeTargetPopulation'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population 1'] = {
    'data': {
        'finalizeTargetPopulation': {
            'targetPopulation': {
                'finalList': {
                    'edges': [
                        {
                            'node': None
                        },
                        {
                            'node': None
                        }
                    ]
                },
                'households': {
                    'edges': [
                        {
                            'node': None
                        },
                        {
                            'node': None
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'FINALIZED'
            }
        }
    },
    'errors': [
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'finalizeTargetPopulation',
                'targetPopulation',
                'finalList',
                'edges',
                0,
                'node',
                'residenceStatus'
            ]
        },
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'finalizeTargetPopulation',
                'targetPopulation',
                'finalList',
                'edges',
                1,
                'node',
                'residenceStatus'
            ]
        },
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'finalizeTargetPopulation',
                'targetPopulation',
                'households',
                'edges',
                0,
                'node',
                'residenceStatus'
            ]
        },
        {
            'message': 'Expected a value of type "HouseholdResidenceStatus" but received: CITIZEN',
            'path': [
                'finalizeTargetPopulation',
                'targetPopulation',
                'households',
                'edges',
                1,
                'node',
                'residenceStatus'
            ]
        }
    ]
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_with_final_criteria 1'] = {
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
            'message': "'NoneType' object has no attribute 'status'",
            'path': [
                'finalizeTargetPopulation'
            ]
        }
    ]
}
