# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestTargetPopulationQuery::test_simple_all_targets_query_0_with_permission 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'candidateListTotalHouseholds': 1,
                        'candidateListTotalIndividuals': 1,
                        'finalListTotalHouseholds': 1,
                        'finalListTotalIndividuals': 1,
                        'name': 'target_population_size_1_approved',
                        'status': 'APPROVED'
                    }
                },
                {
                    'node': {
                        'candidateListTotalHouseholds': 1,
                        'candidateListTotalIndividuals': 2,
                        'finalListTotalHouseholds': None,
                        'finalListTotalIndividuals': None,
                        'name': 'target_population_residence_status',
                        'status': 'DRAFT'
                    }
                },
                {
                    'node': {
                        'candidateListTotalHouseholds': 1,
                        'candidateListTotalIndividuals': 2,
                        'finalListTotalHouseholds': None,
                        'finalListTotalIndividuals': None,
                        'name': 'target_population_size_2',
                        'status': 'DRAFT'
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

snapshots['TestTargetPopulationQuery::test_simple_all_targets_query_2_with_permission_filter_finalListTotalHouseholdsMin 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'candidateListTotalHouseholds': 1,
                        'candidateListTotalIndividuals': 1,
                        'finalListTotalHouseholds': 1,
                        'finalListTotalIndividuals': 1,
                        'name': 'target_population_size_1_approved',
                        'status': 'APPROVED'
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
            'candidateListTargetingCriteria': {
                'rules': [
                    {
                        'filters': [
                            {
                                'arguments': [
                                    1
                                ],
                                'comparisionMethod': 'EQUALS',
                                'fieldAttribute': {
                                    'labelEn': 'What is the household size?',
                                    'type': 'INTEGER'
                                },
                                'fieldName': 'size',
                                'isFlexField': False
                            }
                        ]
                    }
                ]
            },
            'candidateListTotalHouseholds': 1,
            'candidateListTotalIndividuals': 1,
            'finalListTargetingCriteria': None,
            'finalListTotalHouseholds': 1,
            'finalListTotalIndividuals': 1,
            'name': 'target_population_size_1_approved',
            'status': 'APPROVED'
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

snapshots['TestTargetPopulationQuery::test_simple_target_query_2_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
            'candidateListTargetingCriteria': {
                'rules': [
                    {
                        'filters': [
                            {
                                'arguments': [
                                    'REFUGEE'
                                ],
                                'comparisionMethod': 'EQUALS',
                                'fieldAttribute': {
                                    'labelEn': 'Residence status',
                                    'type': 'SELECT_ONE'
                                },
                                'fieldName': 'residence_status',
                                'isFlexField': False
                            }
                        ]
                    }
                ]
            },
            'candidateListTotalHouseholds': 1,
            'candidateListTotalIndividuals': 2,
            'finalListTargetingCriteria': None,
            'finalListTotalHouseholds': None,
            'finalListTotalIndividuals': None,
            'name': 'target_population_residence_status',
            'status': 'DRAFT'
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_2_1_without_permission 1'] = {
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
