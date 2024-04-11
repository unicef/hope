# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUpdateProgram::test_update_active_program_with_dct 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'The Data Collection Type for this programme cannot be edited.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_draft_not_empty_program_with_dct 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'DataCollectingType can be updated only for Program without any households',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_authenticated_0_with_permissions 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'dataCollectingType': {
                    'code': 'partial_individuals',
                    'label': 'Partial'
                },
                'name': 'updated name',
                'partnerAccess': 'NONE_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'partnerName': 'UNICEF'
                    }
                ],
                'status': 'ACTIVE'
            }
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_authenticated_1_with_partial_permissions 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_authenticated_2_without_permissions 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_not_authenticated 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_of_other_partner_raise_error 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['Please assign access to your partner before saving the programme.']",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_partners_0_valid 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'dataCollectingType': {
                    'code': 'partial_individuals',
                    'label': 'Partial'
                },
                'name': 'updated name',
                'partnerAccess': 'SELECTED_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'partnerName': 'UNICEF'
                    },
                    {
                        'areas': [
                            {
                                'name': 'Area1'
                            },
                            {
                                'name': 'Area2'
                            }
                        ],
                        'partnerName': 'WFP'
                    },
                    {
                        'areas': [
                            {
                                'name': 'Area1'
                            },
                            {
                                'name': 'Area2'
                            }
                        ],
                        'partnerName': 'Partner to be added'
                    }
                ],
                'status': 'DRAFT'
            }
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_partners_1_invalid_all_partner_access 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['You cannot specify partners for the chosen access type']",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_partners_2_invalid_none_partner_access 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['You cannot specify partners for the chosen access type']",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_partners_all_partners_access 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'dataCollectingType': {
                    'code': 'partial_individuals',
                    'label': 'Partial'
                },
                'name': 'updated name',
                'partnerAccess': 'ALL_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'partnerName': 'UNICEF'
                    },
                    {
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'partnerName': 'Other Partner'
                    }
                ],
                'status': 'DRAFT'
            }
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_partners_invalid_access_type_from_object 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['You cannot specify partners for the chosen access type']",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_when_finished 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['You cannot change finished program']",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_dct_from_other_ba 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "This Data Collection Type is not assigned to the Program's Business Area",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_deprecated_dct 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Avoid using the deprecated DataCollectingType in Program',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_duplicated_programme_code_among_the_same_business_area 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Programme code is already used.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_inactive_dct 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Only active DataCollectingType can be used in Program',
            'path': [
                'updateProgram'
            ]
        }
    ]
}
