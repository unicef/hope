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
                            'node': {
                                'familySize': 1,
                                'residenceStatus': 'CITIZEN'
                            }
                        },
                        {
                            'node': {
                                'familySize': 2,
                                'residenceStatus': 'CITIZEN'
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'APPROVED'
            }
        }
    }
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
                            'node': {
                                'familySize': 1,
                                'residenceStatus': 'CITIZEN'
                            }
                        },
                        {
                            'node': {
                                'familySize': 2,
                                'residenceStatus': 'CITIZEN'
                            }
                        }
                    ]
                },
                'households': {
                    'edges': [
                        {
                            'node': {
                                'familySize': 1,
                                'residenceStatus': 'CITIZEN'
                            }
                        },
                        {
                            'node': {
                                'familySize': 2,
                                'residenceStatus': 'CITIZEN'
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'FINALIZED'
            }
        }
    }
}

snapshots['TestFinalizeTargetPopulationMutation::test_finalize_target_population_with_final_criteria 1'] = {
    'data': {
        'finalizeTargetPopulation': {
            'targetPopulation': {
                'finalList': {
                    'edges': [
                        {
                            'node': {
                                'familySize': 2,
                                'residenceStatus': 'CITIZEN'
                            }
                        }
                    ]
                },
                'households': {
                    'edges': [
                        {
                            'node': {
                                'familySize': 1,
                                'residenceStatus': 'CITIZEN'
                            }
                        },
                        {
                            'node': {
                                'familySize': 2,
                                'residenceStatus': 'CITIZEN'
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'FINALIZED'
            }
        }
    }
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
                            'node': {
                                'familySize': 1,
                                'residenceStatus': 'CITIZEN'
                            }
                        },
                        {
                            'node': {
                                'familySize': 2,
                                'residenceStatus': 'CITIZEN'
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'DRAFT'
            }
        }
    }
}
