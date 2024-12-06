# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUpdateProgram::test_finish_active_program_with_not_finished_program_cycle_or_end_date 1'] = {
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
            'message': 'Cannot finish programme with active cycles',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_finish_active_program_with_not_finished_program_cycle_or_end_date 2'] = {
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
            'message': 'Cannot finish programme without end date',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_finish_active_program_with_not_finished_program_cycle_or_end_date 3'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'initial name',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Removed"}',
                        'name': 'pdu_field_to_be_removed',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 To Be Removed',
                                'Round 2 To Be Removed',
                                'Round 3 To Be Removed'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Updated"}',
                        'name': 'pdu_field_to_be_updated',
                        'pduData': {
                            'numberOfRounds': 2,
                            'roundsNames': [
                                'Round 1 To Be Updated',
                                'Round 2 To Be Updated'
                            ],
                            'subtype': 'STRING'
                        }
                    }
                ],
                'status': 'FINISHED'
            },
            'validationErrors': None
        }
    }
}

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
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'partial_individuals',
                    'label': 'Partial'
                },
                'name': 'updated name',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Removed"}',
                        'name': 'pdu_field_to_be_removed',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 To Be Removed',
                                'Round 2 To Be Removed',
                                'Round 3 To Be Removed'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Updated"}',
                        'name': 'pdu_field_to_be_updated',
                        'pduData': {
                            'numberOfRounds': 2,
                            'roundsNames': [
                                'Round 1 To Be Updated',
                                'Round 2 To Be Updated'
                            ],
                            'subtype': 'STRING'
                        }
                    }
                ],
                'status': 'ACTIVE'
            },
            'validationErrors': None
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

snapshots['TestUpdateProgram::test_update_program_beneficiary_group 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Other Group'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'initial name',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Removed"}',
                        'name': 'pdu_field_to_be_removed',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 To Be Removed',
                                'Round 2 To Be Removed',
                                'Round 3 To Be Removed'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Updated"}',
                        'name': 'pdu_field_to_be_updated',
                        'pduData': {
                            'numberOfRounds': 2,
                            'roundsNames': [
                                'Round 1 To Be Updated',
                                'Round 2 To Be Updated'
                            ],
                            'subtype': 'STRING'
                        }
                    }
                ],
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_beneficiary_group_when_imported_population 1'] = {
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
            'message': '["You cannot update a program\'s Beneficiary Group if it has imported population."]',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_end_date_validation 1'] = {
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
            'message': 'End date cannot be before start date.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_end_date_validation 2'] = {
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
            'message': 'End date must be equal or after the latest cycle.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_end_date_validation 3'] = {
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
            'message': 'Start date must be equal or before the earliest cycle.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_incompatible_beneficiary_group 1'] = {
    'data': {
        'updateProgram': {
            'program': None,
            'validationErrors': {
                '__all__': [
                    'Selected combination of data collecting type and beneficiary group is invalid.'
                ]
            }
        }
    }
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

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields 1'] = {
    'data': {
        'program': {
            'name': 'initial name',
            'pduFields': [
                {
                    'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                    'name': 'pdu_field_to_be_preserved',
                    'pduData': {
                        'numberOfRounds': 1,
                        'roundsNames': [
                            'Round To Be Preserved'
                        ],
                        'subtype': 'DATE'
                    }
                },
                {
                    'label': '{"English(EN)": "PDU Field To Be Removed"}',
                    'name': 'pdu_field_to_be_removed',
                    'pduData': {
                        'numberOfRounds': 3,
                        'roundsNames': [
                            'Round 1 To Be Removed',
                            'Round 2 To Be Removed',
                            'Round 3 To Be Removed'
                        ],
                        'subtype': 'DECIMAL'
                    }
                },
                {
                    'label': '{"English(EN)": "PDU Field To Be Updated"}',
                    'name': 'pdu_field_to_be_updated',
                    'pduData': {
                        'numberOfRounds': 2,
                        'roundsNames': [
                            'Round 1 To Be Updated',
                            'Round 2 To Be Updated'
                        ],
                        'subtype': 'STRING'
                    }
                }
            ]
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields 2'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'Program with Updated PDU Fields',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field - New"}',
                        'name': 'pdu_field_new',
                        'pduData': {
                            'numberOfRounds': 4,
                            'roundsNames': [
                                'Round 1A',
                                'Round 2B',
                                'Round 3C',
                                'Round 4D'
                            ],
                            'subtype': 'BOOL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field - Updated"}',
                        'name': 'pdu_field_updated',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 Updated',
                                'Round 2 Updated',
                                'Round 3 Updated'
                            ],
                            'subtype': 'BOOL'
                        }
                    }
                ],
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields 3'] = {
    'data': {
        'program': {
            'name': 'Program with Updated PDU Fields',
            'pduFields': [
                {
                    'label': '{"English(EN)": "PDU Field - New"}',
                    'name': 'pdu_field_new',
                    'pduData': {
                        'numberOfRounds': 4,
                        'roundsNames': [
                            'Round 1A',
                            'Round 2B',
                            'Round 3C',
                            'Round 4D'
                        ],
                        'subtype': 'BOOL'
                    }
                },
                {
                    'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                    'name': 'pdu_field_to_be_preserved',
                    'pduData': {
                        'numberOfRounds': 1,
                        'roundsNames': [
                            'Round To Be Preserved'
                        ],
                        'subtype': 'DATE'
                    }
                },
                {
                    'label': '{"English(EN)": "PDU Field - Updated"}',
                    'name': 'pdu_field_updated',
                    'pduData': {
                        'numberOfRounds': 3,
                        'roundsNames': [
                            'Round 1 Updated',
                            'Round 2 Updated',
                            'Round 3 Updated'
                        ],
                        'subtype': 'BOOL'
                    }
                }
            ]
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_duplicated_field_names_in_input 1'] = {
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
            'message': 'Time Series Field names must be unique.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_existing_field_name_for_new_field 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'Program with Updated PDU Fields',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field 1"}',
                        'name': 'pdu_field_1',
                        'pduData': {
                            'numberOfRounds': 4,
                            'roundsNames': [
                                'Round 1A',
                                'Round 2B',
                                'Round 3C',
                                'Round 4D'
                            ],
                            'subtype': 'BOOL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field - Updated"}',
                        'name': 'pdu_field_updated',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 Updated',
                                'Round 2 Updated',
                                'Round 3 Updated'
                            ],
                            'subtype': 'BOOL'
                        }
                    }
                ],
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_existing_field_name_for_updated_field 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'Program with Updated PDU Fields',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field 1"}',
                        'name': 'pdu_field_1',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 Updated',
                                'Round 2 Updated',
                                'Round 3 Updated'
                            ],
                            'subtype': 'BOOL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field - New"}',
                        'name': 'pdu_field_new',
                        'pduData': {
                            'numberOfRounds': 4,
                            'roundsNames': [
                                'Round 1A',
                                'Round 2B',
                                'Round 3C',
                                'Round 4D'
                            ],
                            'subtype': 'BOOL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    }
                ],
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_invalid_data 1'] = {
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
            'message': 'Number of rounds does not match the number of round names',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_program_has_RDI 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'Program with Updated PDU Fields',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Removed"}',
                        'name': 'pdu_field_to_be_removed',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 To Be Removed',
                                'Round 2 To Be Removed',
                                'Round 3 To Be Removed'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Updated"}',
                        'name': 'pdu_field_to_be_updated',
                        'pduData': {
                            'numberOfRounds': 4,
                            'roundsNames': [
                                'Round 1 To Be Updated',
                                'Round 2 To Be Updated',
                                'Round 3 New',
                                'Round 4 New'
                            ],
                            'subtype': 'STRING'
                        }
                    }
                ],
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_program_has_RDI_invalid_data_changed_existing_rounds_names 1'] = {
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
            'message': 'It is not possible to change the names of existing rounds for a Program with RDI or TP',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_program_has_RDI_invalid_data_decrease_rounds 1'] = {
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
            'message': 'It is not possible to decrease the number of rounds for a Program with RDI or TP',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_program_has_RDI_new_field 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'Program with Updated PDU Fields',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Removed"}',
                        'name': 'pdu_field_to_be_removed',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 To Be Removed',
                                'Round 2 To Be Removed',
                                'Round 3 To Be Removed'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Updated"}',
                        'name': 'pdu_field_to_be_updated',
                        'pduData': {
                            'numberOfRounds': 2,
                            'roundsNames': [
                                'Round 1 To Be Updated',
                                'Round 2 To Be Updated'
                            ],
                            'subtype': 'STRING'
                        }
                    }
                ],
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestUpdateProgram::test_update_program_with_pdu_fields_program_has_RDI_update_pdu_field 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'beneficiaryGroup': {
                    'name': 'Household'
                },
                'dataCollectingType': {
                    'code': 'full_collection',
                    'label': 'Full'
                },
                'name': 'Program with Updated PDU Fields',
                'pduFields': [
                    {
                        'label': '{"English(EN)": "PDU Field To Be Preserved"}',
                        'name': 'pdu_field_to_be_preserved',
                        'pduData': {
                            'numberOfRounds': 1,
                            'roundsNames': [
                                'Round To Be Preserved'
                            ],
                            'subtype': 'DATE'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Removed"}',
                        'name': 'pdu_field_to_be_removed',
                        'pduData': {
                            'numberOfRounds': 3,
                            'roundsNames': [
                                'Round 1 To Be Removed',
                                'Round 2 To Be Removed',
                                'Round 3 To Be Removed'
                            ],
                            'subtype': 'DECIMAL'
                        }
                    },
                    {
                        'label': '{"English(EN)": "PDU Field To Be Updated"}',
                        'name': 'pdu_field_to_be_updated',
                        'pduData': {
                            'numberOfRounds': 2,
                            'roundsNames': [
                                'Round 1 To Be Updated',
                                'Round 2 To Be Updated'
                            ],
                            'subtype': 'STRING'
                        }
                    }
                ],
                'status': 'DRAFT'
            },
            'validationErrors': None
        }
    }
}
