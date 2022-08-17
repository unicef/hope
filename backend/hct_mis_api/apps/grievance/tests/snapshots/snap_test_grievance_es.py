# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_head_of_household_last_name 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T16:28:00.446719',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyMWJmNDlkZi0yNjg2LTQwZGUtOTJiNi05NTgzMTFiNGQ1Mzc=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_household_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T16:28:00.468370',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpiNGIxMWUzMi03Yzg1LTQxNzQtYTRhZS1kODAyMzYyMWI4MmU=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 4,
                        'unicefId': 'GRV-000003'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T16:19:52.506299',
                        'description': 'Just random description',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxZTgyZjA3NS1hYjk4LTRiNzAtYjg3NC1kYmNlNWU1YmE1N2M=',
                        'language': 'Polish',
                        'status': 1
                    }
                }
            ]
        }
    }
}
