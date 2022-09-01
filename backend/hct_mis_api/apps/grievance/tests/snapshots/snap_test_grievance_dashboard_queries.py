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
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 4
                }
            ],
            'message': 'Cannot query field "location" on type "ChartDetailedDatasetsNode".'
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 5
                }
            ],
            'message': 'Cannot query field "count" on type "ChartDetailedDatasetsNode".'
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 6
                }
            ],
            'message': 'Cannot query field "categories" on type "ChartDetailedDatasetsNode".'
        }
    ]
}

snapshots['TestGrievanceDashboardQuery::test_grievance_query_by_location_1_without_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 4
                }
            ],
            'message': 'Cannot query field "location" on type "ChartDetailedDatasetsNode".'
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 5
                }
            ],
            'message': 'Cannot query field "count" on type "ChartDetailedDatasetsNode".'
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 6
                }
            ],
            'message': 'Cannot query field "categories" on type "ChartDetailedDatasetsNode".'
        }
    ]
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
            'userGeneratedAvgResolution': 11.75,
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
            'userGeneratedAvgResolution': 11.75,
            'userGeneratedCount': 4
        }
    }
}
