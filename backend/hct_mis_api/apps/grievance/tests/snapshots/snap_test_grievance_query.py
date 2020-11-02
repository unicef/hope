# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQuery::test_grievance_query_all 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2020-03-12T00:00:00',
                        'description': 'Just random description',
                        'language': 'Polish',
                        'status': 1
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2020-07-12T00:00:00',
                        'description': 'Just random description',
                        'language': 'English',
                        'status': 4
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2020-08-22T00:00:00',
                        'description': 'Just random description',
                        'language': 'Polish, English',
                        'status': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_admin2 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2020-03-12T00:00:00',
                        'description': 'Just random description',
                        'language': 'Polish',
                        'status': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_status 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2020-08-22T00:00:00',
                        'description': 'Just random description',
                        'language': 'Polish, English',
                        'status': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_query_single 1'] = {
    'data': {
        'grievanceTicket': {
            'admin': 'City Example',
            'category': 7,
            'consent': True,
            'createdAt': '2020-08-22T00:00:00',
            'description': 'Just random description',
            'language': 'Polish, English',
            'status': 3
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_created_at 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 5,
                        'consent': True,
                        'createdAt': '2020-07-12T00:00:00',
                        'description': 'Just random description',
                        'language': 'English',
                        'status': 4
                    }
                },
                {
                    'node': {
                        'admin': 'City Example',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2020-08-22T00:00:00',
                        'description': 'Just random description',
                        'language': 'Polish, English',
                        'status': 3
                    }
                }
            ]
        }
    }
}
