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
                        3.0,
                        2.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'Positive Feedback',
                'Needs Adjudication',
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
                        3.0,
                        2.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'Positive Feedback',
                'Needs Adjudication',
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
                        'categoryName': 'Positive Feedback',
                        'count': 3
                    },
                    {
                        'categoryName': 'Needs Adjudication',
                        'count': 2
                    },
                    {
                        'categoryName': 'Negative Feedback',
                        'count': 1
                    }
                ],
                'count': 6,
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
                        'categoryName': 'Positive Feedback',
                        'count': 3
                    },
                    {
                        'categoryName': 'Needs Adjudication',
                        'count': 2
                    },
                    {
                        'categoryName': 'Negative Feedback',
                        'count': 1
                    }
                ],
                'count': 6,
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
                        3.0,
                        1.0,
                        1.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'Closed',
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
                        3.0,
                        1.0,
                        1.0,
                        1.0
                    ]
                }
            ],
            'labels': [
                'Closed',
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
            'closedSystemGeneratedCount': 2,
            'closedUserGeneratedCount': 1,
            'systemGeneratedAvgResolution': 0.0,
            'systemGeneratedCount': 2,
            'userGeneratedAvgResolution': -2.5,
            'userGeneratedCount': 4
        }
    }
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_type_1_without_permission 1'] = {
    'data': {
        'ticketsByType': {
            'closedSystemGeneratedCount': 2,
            'closedUserGeneratedCount': 1,
            'systemGeneratedAvgResolution': 0.0,
            'systemGeneratedCount': 2,
            'userGeneratedAvgResolution': -2.5,
            'userGeneratedCount': 4
        }
    }
}
