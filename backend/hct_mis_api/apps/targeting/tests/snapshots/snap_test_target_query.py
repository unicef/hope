# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestTargetPopulationQuery::test_simple_all_targets_query 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'candidateListTotalHouseholds': 1,
                        'candidateListTotalIndividuals': 2,
                        'finalListTotalHouseholds': None,
                        'finalListTotalIndividuals': None,
                        'name': 'target_population_family_size_2',
                        'status': 'DRAFT'
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
                        'candidateListTotalIndividuals': 1,
                        'finalListTotalHouseholds': 1,
                        'finalListTotalIndividuals': 1,
                        'name': 'target_population_family_size_1_approved',
                        'status': 'APPROVED'
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_all_targets_query_filter_finalListTotalHouseholdsMin 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'candidateListTotalHouseholds': 1,
                        'candidateListTotalIndividuals': 1,
                        'finalListTotalHouseholds': 1,
                        'finalListTotalIndividuals': 1,
                        'name': 'target_population_family_size_1_approved',
                        'status': 'APPROVED'
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query 1'] = {
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
                                'fieldName': 'family_size',
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
            'name': 'target_population_family_size_1_approved',
            'status': 'APPROVED'
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query_2 1'] = {
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
