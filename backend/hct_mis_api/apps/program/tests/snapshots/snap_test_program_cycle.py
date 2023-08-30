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
            'message': "Create/Update Program Cycle is possible only for Active Program., Program Cycles' timeframes mustn't overlap.",
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
            'message': "Program Cycle start date can't be earlier then Program start date",
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
            'message': "Program Cycle end date can't be later then Program end date",
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
            'message': "Program Cycles' timeframes mustn't overlap.",
            'path': [
                'createProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_create_program_cycle_when_cycles_overlapping 2'] = {
    'data': {
        'createProgramCycle': {
            'program': {
                'cycles': {
                    'edges': [
                        {
                            'node': {
                                'endDate': '2022-01-01',
                                'name': 'Default Cycle',
                                'startDate': '2021-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-11-27',
                                'name': 'Begin meet.',
                                'startDate': '2022-11-07',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2055-11-30',
                                'name': 'Test Name Program Cycle New 002',
                                'startDate': '2055-11-11',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2055-12-12',
                                'name': 'Cycle New 444',
                                'startDate': '2055-11-25',
                                'status': 'DRAFT'
                            }
                        }
                    ],
                    'totalCount': 4
                }
            }
        }
    }
}

snapshots['TestProgramCycle::test_create_program_cycle_when_cycles_without_end_date 1'] = {
    'data': {
        'createProgramCycle': {
            'program': {
                'cycles': {
                    'edges': [
                        {
                            'node': {
                                'endDate': '2022-01-01',
                                'name': 'Default Cycle',
                                'startDate': '2021-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-11-27',
                                'name': 'Begin meet.',
                                'startDate': '2022-11-07',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-12-12',
                                'name': 'Cycle New Name',
                                'startDate': '2022-11-25',
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
            'message': "Program Cycles' name should be unique.",
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
            'message': 'Only Program Cycle for Active Program can be deleted.',
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
            'message': 'Only Draft Program Cycle can be deleted.',
            'path': [
                'deleteProgramCycle'
            ]
        }
    ]
}

snapshots['TestProgramCycle::test_delete_program_cycle 4'] = {
    'data': {
        'deleteProgramCycle': {
            'ok': True
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
                                'endDate': '2022-01-01',
                                'name': 'Default Cycle',
                                'startDate': '2021-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-11-27',
                                'name': 'Begin meet.',
                                'startDate': '2022-11-07',
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
                                'endDate': '2022-01-01',
                                'name': 'Default Cycle',
                                'startDate': '2021-01-01',
                                'status': 'DRAFT'
                            }
                        },
                        {
                            'node': {
                                'endDate': '2022-11-27',
                                'name': 'Begin meet.',
                                'startDate': '2022-11-07',
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
