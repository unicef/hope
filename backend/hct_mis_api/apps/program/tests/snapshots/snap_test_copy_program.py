# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCopyProgram::test_copy_program_incompatible_collecting_type 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['The Data Collection Type must be compatible with the original Programme.']",
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_not_authenticated 1'] = {
    'data': {
        'copyProgram': None
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
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_with_existing_name 1'] = {
    'data': {
        'copyProgram': {
            'program': None,
            'validationErrors': {
                '__all__': [
                    'Program for name: initial name and business_area: afghanistan already exists.'
                ]
            }
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_partners_0_valid 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'SELECTED_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'New Partner'
                    },
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    },
                    {
                        'areaAccess': 'ADMIN_AREA',
                        'areas': [
                            {
                                'name': 'North Brianmouth'
                            },
                            {
                                'name': 'South Catherine'
                            }
                        ],
                        'name': 'WFP'
                    }
                ],
                'pduFields': [
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_partners_1_invalid_all_partner_access 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'You cannot specify partners for the chosen access type',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_with_partners_2_invalid_none_partner_access 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'You cannot specify partners for the chosen access type',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_with_partners_all_partners_access 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'ALL_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'Other Partner'
                    },
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    }
                ],
                'pduFields': [
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_partners_none_partners_access 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'NONE_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    }
                ],
                'pduFields': [
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_pdu_fields 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'NONE_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    }
                ],
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field 1"}',
                        'name': 'pdu_field_1',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1',
                                'Round 2',
                                'Round 3'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field 2"}',
                        'name': 'pdu_field_2',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round *'
                            ],
                            'subtype': 'STRING'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field 3"}',
                        'name': 'pdu_field_3',
                        'pduData': {
                            'numberOfRounds': 2,
                            'roundsNames': [
                                'Round A',
                                'Round B'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field 4"}',
                        'name': 'pdu_field_4',
                        'pduData': {
                            'numberOfRounds': 4,
                            'roundsNames': [
                                'Round 1A',
                                'Round 2B',
                                'Round 3C',
                                'Round 4D'
                            ],
                            'subtype': 'BOOLEAN'
                        }
                    }
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_pdu_fields_duplicated_field_names_in_input 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Time Series Field names must be unique.',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_with_pdu_fields_existing_field_name_in_different_program 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'NONE_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    }
                ],
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field 1"}',
                        'name': 'pdu_field_1',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1',
                                'Round 2',
                                'Round 3'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    }
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_pdu_fields_invalid_data 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Number of rounds does not match the number of round names',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_without_permissions 1'] = {
    'data': {
        'copyProgram': None
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
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_with_permissions 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'NONE_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    }
                ],
                'pduFields': [
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}
