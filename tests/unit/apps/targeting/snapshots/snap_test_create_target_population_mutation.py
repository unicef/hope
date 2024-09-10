# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_0_with_permission 1'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': False,
                'hasEmptyIdsCriteria': True,
                'name': 'Example name 5',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': '',
                    'individualIds': '',
                    'rules': [
                        {
                            'filters': [
                                {
                                    'arguments': [
                                        3
                                    ],
                                    'comparisonMethod': 'EQUALS',
                                    'fieldName': 'size',
                                    'flexFieldClassification': 'NOT_FLEX_FIELD'
                                }
                            ],
                            'individualsFiltersBlocks': [
                            ]
                        }
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_1_without_permission 1'] = {
    'data': {
        'createTargetPopulation': None
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
                'createTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 1'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': True,
                'hasEmptyIdsCriteria': False,
                'name': 'Test name 1',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': 'HH-1',
                    'individualIds': '',
                    'rules': [
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 2'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': True,
                'hasEmptyIdsCriteria': False,
                'name': 'Test name 2',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': 'HH-1, HH-2, HH-3',
                    'individualIds': 'IND-33',
                    'rules': [
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 3'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': True,
                'hasEmptyIdsCriteria': False,
                'name': 'Test name 3',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': 'HH-1',
                    'individualIds': 'IND-33',
                    'rules': [
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 4'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': True,
                'hasEmptyIdsCriteria': False,
                'name': 'Test name 4',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': '',
                    'individualIds': 'IND-33',
                    'rules': [
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 5'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': True,
                'hasEmptyIdsCriteria': False,
                'name': 'Test name 5',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': '',
                    'individualIds': 'IND-33',
                    'rules': [
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 6'] = {
    'data': {
        'createTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['The given individuals do not exist in the current program']",
            'path': [
                'createTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 7'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': True,
                'hasEmptyIdsCriteria': False,
                'name': 'Test name 7',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': 'HH-1',
                    'individualIds': '',
                    'rules': [
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 8'] = {
    'data': {
        'createTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['The given households do not exist in the current program']",
            'path': [
                'createTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_target_by_id 9'] = {
    'data': {
        'createTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['There should be at least 1 rule in target criteria']",
            'path': [
                'createTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_with_comparison_method_contains_0_with_permission 1'] = {
    'data': {
        'createTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['SELECT_MANY expects at least 1 argument']",
            'path': [
                'createTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_with_comparison_method_contains_1_without_permission 1'] = {
    'data': {
        'createTargetPopulation': None
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
                'createTargetPopulation'
            ]
        }
    ]
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_with_flex_field 1'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': False,
                'hasEmptyIdsCriteria': True,
                'name': 'Example name 5',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': '',
                    'individualIds': '',
                    'rules': [
                        {
                            'filters': [
                            ],
                            'individualsFiltersBlocks': [
                                {
                                    'individualBlockFilters': [
                                        {
                                            'arguments': [
                                                'Average'
                                            ],
                                            'comparisonMethod': 'CONTAINS',
                                            'fieldName': 'flex_field_1',
                                            'flexFieldClassification': 'FLEX_FIELD_BASIC',
                                            'roundNumber': None
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}

snapshots['TestCreateTargetPopulationMutation::test_create_mutation_with_pdu_flex_field 1'] = {
    'data': {
        'createTargetPopulation': {
            'targetPopulation': {
                'hasEmptyCriteria': False,
                'hasEmptyIdsCriteria': True,
                'name': 'Example name 5',
                'programCycle': {
                    'status': 'ACTIVE'
                },
                'status': 'OPEN',
                'targetingCriteria': {
                    'householdIds': '',
                    'individualIds': '',
                    'rules': [
                        {
                            'filters': [
                            ],
                            'individualsFiltersBlocks': [
                                {
                                    'individualBlockFilters': [
                                        {
                                            'arguments': [
                                                '2',
                                                '3.5'
                                            ],
                                            'comparisonMethod': 'RANGE',
                                            'fieldName': 'pdu_field_1',
                                            'flexFieldClassification': 'FLEX_FIELD_PDU',
                                            'roundNumber': 1
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                'totalHouseholdsCount': None,
                'totalIndividualsCount': None
            }
        }
    }
}
