# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQuery::test_grievance_query_sort_by_linked_tickets_ascending_0_with_permission 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'description': '1'
                    }
                },
                {
                    'node': {
                        'description': '2'
                    }
                },
                {
                    'node': {
                        'description': '3'
                    }
                },
                {
                    'node': {
                        'description': '4'
                    }
                },
                {
                    'node': {
                        'description': '5'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_query_sort_by_linked_tickets_ascending_1_without_permission 1'] = {
    'data': {
        'allGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceQuery::test_grievance_query_sort_by_linked_tickets_descending_0_with_permission 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'description': '5'
                    }
                },
                {
                    'node': {
                        'description': '4'
                    }
                },
                {
                    'node': {
                        'description': '3'
                    }
                },
                {
                    'node': {
                        'description': '2'
                    }
                },
                {
                    'node': {
                        'description': '1'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_query_sort_by_linked_tickets_descending_1_without_permission 1'] = {
    'data': {
        'allGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allGrievanceTicket'
            ]
        }
    ]
}
