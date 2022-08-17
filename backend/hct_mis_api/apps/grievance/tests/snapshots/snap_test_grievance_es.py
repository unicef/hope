# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_admin 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
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
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.505301',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0OTM0MDc3NS1iNzg2LTRhMzUtYTU3Ni01N2JiNjJhMzllYTM=',
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_category 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.505301',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0OTM0MDc3NS1iNzg2LTRhMzUtYTU3Ni01N2JiNjJhMzllYTM=',
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_max_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.505301',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0OTM0MDc3NS1iNzg2LTRhMzUtYTU3Ni01N2JiNjJhMzllYTM=',
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_min_and_max_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.505301',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0OTM0MDc3NS1iNzg2LTRhMzUtYTU3Ni01N2JiNjJhMzllYTM=',
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_min_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.505301',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0OTM0MDc3NS1iNzg2LTRhMzUtYTU3Ni01N2JiNjJhMzllYTM=',
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_priority 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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
    'errors': [
        {
            'locations': [
                {
                    'column': 31,
                    'line': 2
                },
                {
                    'column': 102,
                    'line': 3
                }
            ],
            'message': 'Variable "registrationDataImport" of type "String" used in position expecting type "ID".'
        }
    ]
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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
                        'createdAt': '2022-08-17T17:57:21.496398',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3YzkxMTk0ZS0yODA5LTRlZmUtYWE2YS1hNTIyYTI4NTIxYzk=',
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
                        'createdAt': '2022-08-17T17:57:21.511597',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ZjhmNzIzOC0yNzc0LTQwOGYtOWE2NS0wMDdmZmIzNGM0MjA=',
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
