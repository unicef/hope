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
                        'candidateListTotalHouseholds': None,
                        'candidateListTotalIndividuals': None,
                        'createdAt': '2020-04-01T09:30:35.052491',
                        'createdBy': {
                            'firstName': 'Jacqueline',
                            'lastName': 'Davis'
                        },
                        'finalListTotalHouseholds': None,
                        'finalListTotalIndividuals': None,
                        'name': 'target_population_family_size_2',
                        'status': 'APPROVED',
                        'updatedAt': '2020-04-01T09:30:35.052500'
                    }
                },
                {
                    'node': {
                        'candidateListTotalHouseholds': None,
                        'candidateListTotalIndividuals': None,
                        'createdAt': '2020-04-01T09:30:35.062129',
                        'createdBy': {
                            'firstName': 'Jacqueline',
                            'lastName': 'Davis'
                        },
                        'finalListTotalHouseholds': None,
                        'finalListTotalIndividuals': None,
                        'name': 'target_population_residence_status',
                        'status': 'APPROVED',
                        'updatedAt': '2020-04-01T09:30:35.062147'
                    }
                },
                {
                    'node': {
                        'candidateListTotalHouseholds': 1,
                        'candidateListTotalIndividuals': 1,
                        'createdAt': '2020-04-01T09:30:35.068146',
                        'createdBy': {
                            'firstName': 'Jacqueline',
                            'lastName': 'Davis'
                        },
                        'finalListTotalHouseholds': 1,
                        'finalListTotalIndividuals': 1,
                        'name': 'target_population_family_size_1_finalized',
                        'status': 'FINALIZED',
                        'updatedAt': '2020-04-01T09:30:35.073141'
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_simple_target_query 1'] = {
    'data': {
        'targetPopulation': {
            'candidateListTargetingCriteria': None,
            'candidateListTotalHouseholds': 1,
            'candidateListTotalIndividuals': 1,
            'finalListTargetingCriteria': {
                'rules': [
                    {
                        'filters': [
                            {
                                'arguments': [
                                    1
                                ],
                                'comparisionMethod': 'EQUALS',
                                'fieldName': 'family_size',
                                'id': 'a875ac73-0fb5-4ee0-b35a-aa53c30a4661',
                                'isFlexField': False
                            }
                        ]
                    }
                ]
            },
            'finalListTotalHouseholds': 1,
            'finalListTotalIndividuals': 1,
            'id': 'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZDFlNzk4MGUtOGI1OC00ODg2LWE4YTEtNmE3MTY2NGM2Mzcz',
            'name': 'target_population_family_size_1_finalized',
            'status': 'FINALIZED'
        }
    }
}
