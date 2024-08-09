# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateProgram::test_create_program_authenticated_0_with_permission 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': 'partial_individuals',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True,
                    'label': 'Partial'
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'isSocialWorkerProgram': False,
                'name': 'Test',
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
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_authenticated_1_without_permission 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_authenticated_2_with_permission_but_invalid_dates 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Start date cannot be greater than the end date.',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_not_authenticated 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_dct_from_other_ba 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_deprecated_dct 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_inactive_dct 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_partners_0_valid 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': 'partial_individuals',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True,
                    'label': 'Partial'
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'isSocialWorkerProgram': False,
                'name': 'Test',
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
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_with_partners_1_invalid_all_partner_access 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_partners_2_invalid_none_partner_access 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_partners_all_partners_access 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': 'partial_individuals',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True,
                    'label': 'Partial'
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'isSocialWorkerProgram': False,
                'name': 'Test',
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
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_with_partners_none_partners_access 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': 'partial_individuals',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True,
                    'label': 'Partial'
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'isSocialWorkerProgram': False,
                'name': 'Test',
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
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_with_pdu_fields 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': 'partial_individuals',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True,
                    'label': 'Partial'
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'isSocialWorkerProgram': False,
                'name': 'Test',
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
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_with_pdu_fields_duplicated_field_names_in_input 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_pdu_fields_existing_field_name_in_different_program 1'] = {
    'data': {
        'createProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000',
                'cashPlus': True,
                'dataCollectingType': {
                    'active': True,
                    'code': 'partial_individuals',
                    'description': 'Partial individuals collected',
                    'individualFiltersAvailable': True,
                    'label': 'Partial'
                },
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'isSocialWorkerProgram': False,
                'name': 'Test',
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
                'startDate': '2019-12-20',
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCreateProgram::test_create_program_with_pdu_fields_invalid_data 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_programme_code_greater_than_4_chars 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Programme code should be exactly 4 characters long and may only contain letters, digits and characters: - . /',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_programme_code_less_than_4_chars 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Programme code should be exactly 4 characters long and may only contain letters, digits and characters: - . /',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_with_programme_code_not_within_allowed_characters 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Programme code should be exactly 4 characters long and may only contain letters, digits and characters: - . /',
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_create_program_without_dct 1'] = {
    'data': {
        'createProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['DataCollectingType is required for creating new Program']",
            'path': [
                'createProgram'
            ]
        }
    ]
}

snapshots['TestCreateProgram::test_programme_code_should_be_unique_among_the_same_business_area 1'] = {
    'data': {
        'createProgram': None
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
                'createProgram'
            ]
        }
    ]
}
