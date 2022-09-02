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
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
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

snapshots['TestTargetPopulationQuery::test_simple_target_query_2_0_with_permission 1'] = {
    'data': {
        'targetPopulation': {
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
                                'isFlexField': False
                            }
                        ]
                    }
                ]
            },
            'totalHouseholdsCount': 1,
            'totalIndividualsCount': 2
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
