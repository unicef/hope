# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestApproveTargetPopulationMutation::test_approve_fail_target_population 1'] = {
    'data': None,
    'errors': [
        {
            'message': 'cannot unpack non-iterable NoneType object'
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
    'data': None,
    'errors': [
        {
            'message': 'cannot unpack non-iterable NoneType object'
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
                                'familySize': 2,
                                'residenceStatus': 'CITIZEN'
                            }
                        },
                        {
                            'node': {
                                'familySize': 1,
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
    'data': None,
    'errors': [
        {
            'message': 'cannot unpack non-iterable NoneType object'
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
