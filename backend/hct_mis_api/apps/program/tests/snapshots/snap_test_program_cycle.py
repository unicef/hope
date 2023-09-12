# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestProgramCycle::test_create_program_cycle_0_without_permission_program_in_draft 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_1_with_permission_program_in_draft 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Create/Update Programme Cycle is possible only for Active Programme.',
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_2_with_permission_program_in_active_wrong_start_date 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Programme Cycle start date cannot be earlier than programme start date',
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_3_with_permission_program_in_active_wrong_end_date 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Programme Cycle end date cannot be earlier than programme end date',
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_4_with_permission_program_in_active_end_date_is_more_then_start_date 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Start date cannot be greater than the end date.',
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_when_cycles_overlapping 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Programme Cycles' timeframes must not overlap.",
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_when_cycles_overlapping 2'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Programme Cycles' timeframes must not overlap.",
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_when_cycles_overlapping 3'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Programme Cycles' timeframes must not overlap.",
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_when_cycles_overlapping 4'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Programme Cycles' timeframes must not overlap.",
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_when_cycles_without_end_date 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'All Programme Cycles should have end date for creation new one.',
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_with_the_same_name 1'] = {
    'data': {
        'createProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': "Programme Cycles' name should be unique.",
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_delete_program_cycle 1'] = {
    'data': {
        'deleteProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'deleteProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_delete_program_cycle 2'] = {
    'data': {
        'deleteProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Only Programme Cycle for Active Programme can be deleted.',
            'path': [
                'deleteProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_delete_program_cycle 3'] = {
    'data': {
        'deleteProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Only Draft Programme Cycle can be deleted.',
            'path': [
                'deleteProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_delete_program_cycle 4'] = {
    'data': {
        'deleteProgramCycle': {
            'program': {
                'cycles': {
                    'edges': [
                        {
                            'node': {
                                'endDate': '2020-01-02',
                                'name': 'Default Cycle 001',
                                'startDate': '2020-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-01-01',
                                'name': 'Cycle 002',
                                'startDate': '2021-01-01',
                                'status': 'DRAFT'
                            }
                        }
                    ],
                    'totalCount': 2
                }
            }
        }
    }
}

snapshots['TestProgramCycle::test_update_program_cycle 1'] = {
    'data': {
        'updateProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_update_program_cycle 2'] = {
    'data': {
        'updateProgramCycle': {
            'program': {
                'cycles': {
                    'edges': [
                        {
                            'node': {
                                'endDate': '2020-01-02',
                                'name': 'Default Cycle 001',
                                'startDate': '2020-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-01-01',
                                'name': 'Cycle 002',
                                'startDate': '2021-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': None,
                                'name': 'NEW NEW NAME 22',
                                'startDate': '2055-11-13',
                                'status': 'DRAFT'
                            }
                        }
                    ],
                    'totalCount': 3
                }
            }
        }
    }
}

snapshots['TestProgramCycle::test_update_program_cycle 3'] = {
    'data': {
        'updateProgramCycle': {
            'program': {
                'cycles': {
                    'edges': [
                        {
                            'node': {
                                'endDate': '2020-01-02',
                                'name': 'Default Cycle 001',
                                'startDate': '2020-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-01-01',
                                'name': 'Cycle 002',
                                'startDate': '2021-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2055-11-22',
                                'name': 'NEW NEW NAME 333',
                                'startDate': '2055-11-14',
                                'status': 'DRAFT'
                            }
                        }
                    ],
                    'totalCount': 3
                }
            }
        }
    }
}

snapshots['TestProgramCycle::test_update_program_cycle 4'] = {
    'data': {
        'updateProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Not possible leave the Programme Cycle name empty.',
            'path': [
                'updateProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_update_program_cycle 5'] = {
    'data': {
        'updateProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Not possible leave the Programme Cycle start date empty.',
            'path': [
                'updateProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_update_program_cycle 6'] = {
    'data': {
        'updateProgramCycle': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Not possible leave the Programme Cycle end date empty if it was empty upon starting the edit.',
            'path': [
                'updateProgramCycle'
            ]
        }
    ]
}
