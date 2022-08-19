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
                        'category': 7,
                        'consent': True,
                        'description': 'grievance_ticket_1',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-0000001',
                        'urgency': 2
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
                        'category': 3,
                        'consent': True,
                        'description': 'grievance_ticket_2',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-0000002',
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
                        'category': 7,
                        'consent': True,
                        'description': 'grievance_ticket_1',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-0000001',
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
                        'category': 7,
                        'consent': True,
                        'description': 'grievance_ticket_1',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-0000001',
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
                        'category': 5,
                        'consent': True,
                        'description': 'grievance_ticket_3',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-0000003',
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
                        'category': 3,
                        'consent': True,
                        'description': 'grievance_ticket_2',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-0000002',
                        'urgency': 3
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
                        'category': 3,
                        'consent': True,
                        'description': 'grievance_ticket_2',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-0000002',
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
                {
                    'node': {
                        'category': 5,
                        'consent': True,
                        'description': 'grievance_ticket_3',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-0000003',
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
                        'category': 7,
                        'consent': True,
                        'description': 'grievance_ticket_1',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-0000001',
                        'urgency': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_multiple_statuses 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'category': 3,
                        'consent': True,
                        'description': 'grievance_ticket_2',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-0000002',
                        'urgency': 3
                    }
                },
                {
                    'node': {
                        'category': 5,
                        'consent': True,
                        'description': 'grievance_ticket_3',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-0000003',
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
                        'category': 5,
                        'consent': True,
                        'description': 'grievance_ticket_3',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-0000003',
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
                        'category': 3,
                        'consent': True,
                        'description': 'grievance_ticket_2',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': 12,
                        'language': 'Polish',
                        'priority': 2,
                        'status': 3,
                        'unicefId': 'GRV-0000002',
                        'urgency': 3
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
                        'category': 7,
                        'consent': True,
                        'description': 'grievance_ticket_1',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-0000001',
                        'urgency': 2
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
                        'category': 7,
                        'consent': True,
                        'description': 'grievance_ticket_1',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-0000001',
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
                        'category': 5,
                        'consent': True,
                        'description': 'grievance_ticket_3',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-0000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_grievance_type 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'category': 5,
                        'consent': True,
                        'description': 'grievance_ticket_3',
                        'householdUnicefId': 'HH-20-0000.0003',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 3,
                        'status': 4,
                        'unicefId': 'GRV-0000003',
                        'urgency': 1
                    }
                }
            ]
        }
    }
}
