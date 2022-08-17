# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_category 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:19:16.916821',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozNDRmNjUwZi04NjY0LTRmYTUtOWE2OC00MDZmNWZhMGIyODA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_head_of_household_last_name 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:19:16.916821',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozNDRmNjUwZi04NjY0LTRmYTUtOWE2OC00MDZmNWZhMGIyODA=',
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
                        'createdAt': '2022-08-17T17:19:16.932554',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1ZTM3YjU5Yi1hN2ZhLTRmMzMtYWI3Zi1kMTdlMjk2MGIxYzk=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_status 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:19:16.932554',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1ZTM3YjU5Yi1hN2ZhLTRmMzMtYWI3Zi1kMTdlMjk2MGIxYzk=',
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
                        'createdAt': '2022-08-17T17:19:16.916821',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozNDRmNjUwZi04NjY0LTRmYTUtOWE2OC00MDZmNWZhMGIyODA=',
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
