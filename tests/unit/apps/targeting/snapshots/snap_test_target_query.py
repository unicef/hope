# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestTargetPopulationQuery::test_all_targets_query_filter_by_cycle 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'name': 'target_population_residence_status',
                        'status': 'OPEN',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_all_targets_query_order_by_created_by 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'createdBy': {
                            'firstName': 'First',
                            'lastName': 'User'
                        },
                        'name': 'target_population_residence_status',
                        'status': 'OPEN',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'createdBy': {
                            'firstName': 'PDU',
                            'lastName': 'User'
                        },
                        'name': 'target_population_with_pdu_filter',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 3
                    }
                },
                {
                    'node': {
                        'createdBy': {
                            'firstName': 'Second',
                            'lastName': 'User'
                        },
                        'name': 'target_population_size_1_approved',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 2,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'createdBy': {
                            'firstName': 'Test',
                            'lastName': 'User'
                        },
                        'name': 'target_population_size_2',
                        'status': 'OPEN',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'createdBy': {
                            'firstName': 'Third',
                            'lastName': 'User'
                        },
                        'name': 'target_population_with_individual_filter',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_all_targets_query_0_with_permission 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'name': 'target_population_size_2',
                        'status': 'OPEN',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'name': 'target_population_residence_status',
                        'status': 'OPEN',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'name': 'target_population_size_1_approved',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 2,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'name': 'target_population_with_pdu_filter',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 3
                    }
                },
                {
                    'node': {
                        'name': 'target_population_with_individual_filter',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_all_targets_query_1_without_permission 1'] = {
    'data': {
        'allTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allTargetPopulation'
            ]
        }
    ]
}

snapshots['TestTargetPopulationQuery::test_simple_all_targets_query_2_with_permission_filter_totalHouseholdsCountMin 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'name': 'target_population_size_2',
                        'status': 'OPEN',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'name': 'target_population_residence_status',
                        'status': 'OPEN',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'name': 'target_population_size_1_approved',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 2,
                        'totalIndividualsCount': 2
                    }
                },
                {
                    'node': {
                        'name': 'target_population_with_pdu_filter',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 3
                    }
                },
                {
                    'node': {
                        'name': 'target_population_with_individual_filter',
                        'status': 'LOCKED',
                        'totalHouseholdsCount': 1,
                        'totalIndividualsCount': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
            'hasEmptyCriteria': False,
            'hasEmptyIdsCriteria': True,
            'name': 'target_population_size_1_approved',
            'status': 'LOCKED',
            'targetingCriteria': {
                'rules': [
                    {
                        'filters': [
                            {
                                'arguments': [
                                    1
                                ],
                                'comparisonMethod': 'EQUALS',
                                'fieldAttribute': {
                                    'labelEn': 'What is the Household size?',
                                    'type': 'INTEGER'
                                },
                                'fieldName': 'size',
                                'flexFieldClassification': 'NOT_FLEX_FIELD'
                            }
                        ],
                        'individualsFiltersBlocks': [
                        ]
                    }
                ]
            },
            'totalHouseholdsCount': 2,
            'totalIndividualsCount': 2
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_1_without_permission 1'] = {
    'data': {
        'targetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulation'
            ]
        }
    ]
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_individual_filter_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
            'hasEmptyCriteria': False,
            'hasEmptyIdsCriteria': True,
            'name': 'target_population_with_individual_filter',
            'status': 'LOCKED',
            'targetingCriteria': {
                'rules': [
                    {
                        'filters': [
                        ],
                        'individualsFiltersBlocks': [
                            {
                                'individualBlockFilters': [
                                    {
                                        'arguments': [
                                            'disabled'
                                        ],
                                        'comparisonMethod': 'EQUALS',
                                        'fieldAttribute': {
                                            'labelEn': 'Individual is disabled?',
                                            'type': 'SELECT_ONE'
                                        },
                                        'fieldName': 'disability',
                                        'flexFieldClassification': 'NOT_FLEX_FIELD',
                                        'roundNumber': None
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            'totalHouseholdsCount': 1,
            'totalIndividualsCount': 3
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_individual_filter_1_without_permission 1'] = {
    'data': {
        'targetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulation'
            ]
        }
    ]
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_next_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
            'hasEmptyCriteria': False,
            'hasEmptyIdsCriteria': True,
            'name': 'target_population_residence_status',
            'status': 'OPEN',
            'targetingCriteria': {
                'rules': [
                    {
                        'filters': [
                            {
                                'arguments': [
                                    'REFUGEE'
                                ],
                                'comparisonMethod': 'EQUALS',
                                'fieldAttribute': {
                                    'labelEn': 'Residence status',
                                    'type': 'SELECT_ONE'
                                },
                                'fieldName': 'residence_status',
                                'flexFieldClassification': 'NOT_FLEX_FIELD'
                            }
                        ],
                        'individualsFiltersBlocks': [
                        ]
                    }
                ]
            },
            'totalHouseholdsCount': 1,
            'totalIndividualsCount': 2
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_next_1_without_permission 1'] = {
    'data': {
        'targetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulation'
            ]
        }
    ]
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_pdu_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
            'hasEmptyCriteria': False,
            'hasEmptyIdsCriteria': True,
            'name': 'target_population_with_pdu_filter',
            'status': 'LOCKED',
            'targetingCriteria': {
                'rules': [
                    {
                        'filters': [
                        ],
                        'individualsFiltersBlocks': [
                            {
                                'individualBlockFilters': [
                                    {
                                        'arguments': [
                                            'some'
                                        ],
                                        'comparisonMethod': 'EQUALS',
                                        'fieldAttribute': {
                                            'labelEn': 'PDU Field STRING',
                                            'type': 'PDU'
                                        },
                                        'fieldName': 'pdu_field_string',
                                        'flexFieldClassification': 'FLEX_FIELD_PDU',
                                        'roundNumber': 1
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            'totalHouseholdsCount': 1,
            'totalIndividualsCount': 3
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_pdu_1_without_permission 1'] = {
    'data': {
        'targetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulation'
            ]
        }
    ]
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_pdu_for_sw_program_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
            'hasEmptyCriteria': False,
            'hasEmptyIdsCriteria': True,
            'name': 'target_population_with_pdu_filter_for_sw',
            'status': 'LOCKED',
            'targetingCriteria': {
                'rules': [
                    {
                        'filters': [
                            {
                                'arguments': [
                                    'Test'
                                ],
                                'comparisonMethod': 'EQUALS',
                                'fieldAttribute': {
                                    'labelEn': 'PDU Field STRING for SW',
                                    'type': 'PDU'
                                },
                                'fieldName': 'pdu_field_string_for_sw',
                                'flexFieldClassification': 'FLEX_FIELD_PDU'
                            }
                        ],
                        'individualsFiltersBlocks': [
                        ]
                    }
                ]
            },
            'totalHouseholdsCount': 0,
            'totalIndividualsCount': 0
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_pdu_for_sw_program_1_without_permission 1'] = {
    'data': {
        'targetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulation'
            ]
        }
    ]
}
