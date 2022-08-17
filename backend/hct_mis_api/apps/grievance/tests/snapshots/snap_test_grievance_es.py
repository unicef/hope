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
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.923372',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxNmZmYWI3Mi1iMWIzLTRjNzUtOWU4YS1lZTEzNjAyMGZkZmQ=',
                        'issueType': 12,
                        'language': 'Polish',
                        'status': 3,
                        'unicefId': 'GRV-000002'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_category 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_head_of_household_last_name 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_household_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_issue_type 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.923372',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxNmZmYWI3Mi1iMWIzLTRjNzUtOWU4YS1lZTEzNjAyMGZkZmQ=',
                        'issueType': 12,
                        'language': 'Polish',
                        'status': 3,
                        'unicefId': 'GRV-000002'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_max_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.923372',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxNmZmYWI3Mi1iMWIzLTRjNzUtOWU4YS1lZTEzNjAyMGZkZmQ=',
                        'issueType': 12,
                        'language': 'Polish',
                        'status': 3,
                        'unicefId': 'GRV-000002'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_min_and_max_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.923372',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxNmZmYWI3Mi1iMWIzLTRjNzUtOWU4YS1lZTEzNjAyMGZkZmQ=',
                        'issueType': 12,
                        'language': 'Polish',
                        'status': 3,
                        'unicefId': 'GRV-000002'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_min_date_range 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.923372',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxNmZmYWI3Mi1iMWIzLTRjNzUtOWU4YS1lZTEzNjAyMGZkZmQ=',
                        'issueType': 12,
                        'language': 'Polish',
                        'status': 3,
                        'unicefId': 'GRV-000002'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_priority 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.923372',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxNmZmYWI3Mi1iMWIzLTRjNzUtOWU4YS1lZTEzNjAyMGZkZmQ=',
                        'issueType': 12,
                        'language': 'Polish',
                        'status': 3,
                        'unicefId': 'GRV-000002'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_status 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_urgency 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.914162',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ODk4ZDU1NC05OGU3LTQxM2MtOTQyZC1lMjQ5ZGMxNGU0YTA=',
                        'issueType': None,
                        'language': 'Polish',
                        'status': 1,
                        'unicefId': 'GRV-000001'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 3,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.923372',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxNmZmYWI3Mi1iMWIzLTRjNzUtOWU4YS1lZTEzNjAyMGZkZmQ=',
                        'issueType': 12,
                        'language': 'Polish',
                        'status': 3,
                        'unicefId': 'GRV-000002'
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2022-08-17T17:40:20.930275',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo1NDBiZTJjMC00MGI2LTRiZjgtODQzYi0zOTg5YjA0Y2JjZDU=',
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
