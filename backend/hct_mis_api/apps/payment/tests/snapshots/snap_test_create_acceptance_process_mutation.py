# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 1'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Acceptance_Process_Type must be one of Approval, Authorization, Finance Review or Reject',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 10'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    },
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            }
                        ],
                        'stage': 1
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 11'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Authorization step not finished yet for this stage',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 12'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    },
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            }
                        ],
                        'stage': 1
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 13'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    },
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            },
                            {
                                'comment': 'default comment for 1 and type FINANCE_REVIEW',
                                'info': 'Reviewed by Rachel Walker',
                                'stage': 1,
                                'type': 'FINANCE_REVIEW'
                            }
                        ],
                        'stage': 1
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 14'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    },
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            },
                            {
                                'comment': 'default comment for 1 and type FINANCE_REVIEW',
                                'info': 'Reviewed by Rachel Walker',
                                'stage': 1,
                                'type': 'FINANCE_REVIEW'
                            },
                            {
                                'comment': 'default comment for 1 and type FINANCE_REVIEW',
                                'info': 'Reviewed by Rachel Walker',
                                'stage': 1,
                                'type': 'FINANCE_REVIEW'
                            }
                        ],
                        'stage': 1
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 15'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    },
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            },
                            {
                                'comment': 'default comment for 1 and type AUTHORIZATION',
                                'info': 'Authorized by Rachel Walker',
                                'stage': 1,
                                'type': 'AUTHORIZATION'
                            },
                            {
                                'comment': 'default comment for 1 and type FINANCE_REVIEW',
                                'info': 'Reviewed by Rachel Walker',
                                'stage': 1,
                                'type': 'FINANCE_REVIEW'
                            },
                            {
                                'comment': 'default comment for 1 and type FINANCE_REVIEW',
                                'info': 'Reviewed by Rachel Walker',
                                'stage': 1,
                                'type': 'FINANCE_REVIEW'
                            },
                            {
                                'comment': 'default comment for 1 and type FINANCE_REVIEW',
                                'info': 'Reviewed by Rachel Walker',
                                'stage': 1,
                                'type': 'FINANCE_REVIEW'
                            }
                        ],
                        'stage': 1
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 16'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Finance Review step finished for this stage',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 17'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Previous stage in Acceptance Process is not rejected or stage not exists',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 18'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Previous stage in Acceptance Process is not rejected or stage not exists',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 2'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            }
                        ],
                        'stage': 0
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 3'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Approve step not finished yet for this stage',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 4'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Approve step not finished yet for this stage',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 5'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 6'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': 'Stage 0 is Rejected',
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 7'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    },
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            }
                        ],
                        'stage': 1
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 8'] = {
    'data': {
        'createAcceptanceProcess': {
            'acceptanceProcess': {
                'approvals': [
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 0 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 0,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 0 and type REJECT',
                                'info': 'Rejected by Rachel Walker',
                                'stage': 0,
                                'type': 'REJECT'
                            }
                        ],
                        'stage': 0
                    },
                    {
                        'objs': [
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            },
                            {
                                'comment': 'default comment for 1 and type APPROVAL',
                                'info': 'Approved by Rachel Walker',
                                'stage': 1,
                                'type': 'APPROVAL'
                            }
                        ],
                        'stage': 1
                    }
                ]
            }
        }
    }
}

snapshots['TestCreateAcceptanceProcessMutation::test_create_acceptance_process_0_without_permission 9'] = {
    'data': {
        'createAcceptanceProcess': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 3
                }
            ],
            'message': "Acceptance Process can't has more than 2 APPROVAL for this stage",
            'path': [
                'createAcceptanceProcess'
            ]
        }
    ]
}
