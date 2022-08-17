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
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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
                        'createdAt': '2022-08-17T18:26:33.089717',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo4MDZiZjQ4Yi03ZjUxLTQ1NmMtYWM3Ni1lZGFmN2JjZTY1YTk=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'createdAt': '2022-08-17T18:26:33.089717',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo4MDZiZjQ4Yi03ZjUxLTQ1NmMtYWM3Ni1lZGFmN2JjZTY1YTk=',
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
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_fsp 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 19
                }
            ],
            'message': 'Cannot query field "fsp" on type "GrievanceTicketNode".'
        }
    ]
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
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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
                        'createdAt': '2022-08-17T18:26:33.089717',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo4MDZiZjQ4Yi03ZjUxLTQ1NmMtYWM3Ni1lZGFmN2JjZTY1YTk=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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
                        'createdAt': '2022-08-17T18:26:33.089717',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo4MDZiZjQ4Yi03ZjUxLTQ1NmMtYWM3Ni1lZGFmN2JjZTY1YTk=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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
                        'createdAt': '2022-08-17T18:26:33.089717',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo4MDZiZjQ4Yi03ZjUxLTQ1NmMtYWM3Ni1lZGFmN2JjZTY1YTk=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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
                        'createdAt': '2022-08-17T18:26:33.089717',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo4MDZiZjQ4Yi03ZjUxLTQ1NmMtYWM3Ni1lZGFmN2JjZTY1YTk=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
                        'createdAt': '2022-08-17T18:26:33.080249',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTpjNGZiYzZkNS1kNjA2LTRiNTktYWFiNy0yMjRjMWY2M2EwZGY=',
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
                        'createdAt': '2022-08-17T18:26:33.098457',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0ODE1MWI2Zi04OGM2LTQ0ZmEtODc4YS0zNDAzZTYyZmNiMGY=',
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
