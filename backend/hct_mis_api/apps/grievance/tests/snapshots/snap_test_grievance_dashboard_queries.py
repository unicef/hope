# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_category_0_with_permission 1'] = {
    'data': {
        'ticketsByCategory': {
            'datasets': [
                {
                    'data': [
                        2.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'Positive Feedback',
                'Negative Feedback'
            ]
        }
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_category_1_without_permission 1'] = {
    'data': {
        'ticketsByCategory': {
            'datasets': [
                {
                    'data': [
                        2.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'Positive Feedback',
                'Negative Feedback'
            ]
        }
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_location_0_with_permission 1'] = {
    'data': {
        'ticketsByLocationAndCategory': [
            {
                'categories': [
                    {
                        'categoryName': 'Negative Feedback',
                        'count': 1
                    },
                    {
                        'categoryName': 'Positive Feedback',
                        'count': 1
                    }
                ],
                'count': 2,
                'location': 'City Example'
            },
            {
                'categories': [
                    {
                        'categoryName': 'Positive Feedback',
                        'count': 1
                    }
                ],
                'count': 1,
                'location': 'City Test'
            }
        ]
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_location_1_without_permission 1'] = {
    'data': {
        'ticketsByLocationAndCategory': [
            {
                'categories': [
                    {
                        'categoryName': 'Negative Feedback',
                        'count': 1
                    },
                    {
                        'categoryName': 'Positive Feedback',
                        'count': 1
                    }
                ],
                'count': 2,
                'location': 'City Example'
            },
            {
                'categories': [
                    {
                        'categoryName': 'Positive Feedback',
                        'count': 1
                    }
                ],
                'count': 1,
                'location': 'City Test'
            }
        ]
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_status_0_with_permission 1'] = {
    'data': {
        'ticketsByStatus': {
            'datasets': [
                {
                    'data': [
                        1.0,
                        1.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'In Progress',
                'New',
                'On Hold'
            ]
        }
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_status_1_without_permission 1'] = {
    'data': {
        'ticketsByStatus': {
            'datasets': [
                {
                    'data': [
                        1.0,
                        1.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'In Progress',
                'New',
                'On Hold'
            ]
        }
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_type_0_with_permission 1'] = {
    'data': {
        'ticketsByType': {
            'closedSystemGeneratedCount': 0,
            'closedUserGeneratedCount': 0,
            'systemGeneratedAvgResolution': None,
            'systemGeneratedCount': 0,
            'userGeneratedAvgResolution': -3.33333333333333,
            'userGeneratedCount': 3
        }
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_type_1_without_permission 1'] = {
    'data': {
        'ticketsByType': {
            'closedSystemGeneratedCount': 0,
            'closedUserGeneratedCount': 0,
            'systemGeneratedAvgResolution': None,
            'systemGeneratedCount': 0,
            'userGeneratedAvgResolution': -3.33333333333333,
            'userGeneratedCount': 3
        }
    }
}
