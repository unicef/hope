# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_admin 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.052676',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyMDFkNTBmNy00OWIxLTQzOTYtYTc0OS1hZmRiMDQ3ODg3NTE=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-000001',
                        'urgency': 2
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.063051',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTplM2M0NjU0NS1hOTUyLTRlY2YtYjQyYy00MjU1NTk1ZTAxNmU=',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-000002',
                        'urgency': 3
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.069852',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozOGIzNzExMy0wNDNiLTQxMTctYmVlZi1iN2M1NTUzNmMyY2Q=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_assigned_to 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.063051',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTplM2M0NjU0NS1hOTUyLTRlY2YtYjQyYy00MjU1NTk1ZTAxNmU=',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-000002',
                        'urgency': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_category 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.052676',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyMDFkNTBmNy00OWIxLTQzOTYtYTc0OS1hZmRiMDQ3ODg3NTE=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-000001',
                        'urgency': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_head_of_household_last_name 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.052676',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyMDFkNTBmNy00OWIxLTQzOTYtYTc0OS1hZmRiMDQ3ODg3NTE=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-000001',
                        'urgency': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_household_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.069852',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozOGIzNzExMy0wNDNiLTQxMTctYmVlZi1iN2M1NTUzNmMyY2Q=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_issue_type 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_max_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.063051',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTplM2M0NjU0NS1hOTUyLTRlY2YtYjQyYy00MjU1NTk1ZTAxNmU=',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-000002',
                        'urgency': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_min_and_max_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_min_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_priority 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.069852',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozOGIzNzExMy0wNDNiLTQxMTctYmVlZi1iN2M1NTUzNmMyY2Q=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_registration_data_import 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.052676',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyMDFkNTBmNy00OWIxLTQzOTYtYTc0OS1hZmRiMDQ3ODg3NTE=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-000001',
                        'urgency': 2
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.063051',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTplM2M0NjU0NS1hOTUyLTRlY2YtYjQyYy00MjU1NTk1ZTAxNmU=',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-000002',
                        'urgency': 3
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.069852',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozOGIzNzExMy0wNDNiLTQxMTctYmVlZi1iN2M1NTUzNmMyY2Q=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_status 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.069852',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozOGIzNzExMy0wNDNiLTQxMTctYmVlZi1iN2M1NTUzNmMyY2Q=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.052676',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyMDFkNTBmNy00OWIxLTQzOTYtYTc0OS1hZmRiMDQ3ODg3NTE=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-000001',
                        'urgency': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_urgency 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T19:28:02.069852',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTozOGIzNzExMy0wNDNiLTQxMTctYmVlZi1iN2M1NTUzNmMyY2Q=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}
