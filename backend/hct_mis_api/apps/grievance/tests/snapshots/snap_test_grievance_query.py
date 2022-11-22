# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_admin2 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 31,
                    'line': 2
                }
            ],
            'message': "Variable '$admin' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_assigned_to_correct_user 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2020-03-12T00:00:00+00:00',
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
                        'createdAt': '2020-07-12T00:00:00+00:00',
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
                        'createdAt': '2020-08-22T00:00:00+00:00',
                        'description': 'Just random description',
                        'language': 'Polish, English',
                        'status': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_assigned_to_incorrect_user 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_category_0_category_positive_feedback 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 31,
                    'line': 2
                },
                {
                    'column': 88,
                    'line': 3
                }
            ],
            'message': "Variable '$category' of type 'String' used in position expecting type 'Int'."
        }
    ]
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_category_1_category_negative_feedback 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 31,
                    'line': 2
                },
                {
                    'column': 88,
                    'line': 3
                }
            ],
            'message': "Variable '$category' of type 'String' used in position expecting type 'Int'."
        }
    ]
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
                        'createdAt': '2020-07-12T00:00:00+00:00',
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
                        'createdAt': '2020-08-22T00:00:00+00:00',
                        'description': 'Just random description',
                        'language': 'Polish, English',
                        'status': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_score 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 31,
                    'line': 2
                }
            ],
            'message': "Variable '$scoreMin' got invalid value 100; String cannot represent a non string value: 100"
        },
        {
            'locations': [
                {
                    'column': 50,
                    'line': 2
                }
            ],
            'message': "Variable '$scoreMax' got invalid value 200; String cannot represent a non string value: 200"
        }
    ]
}

snapshots['TestGrievanceQuery::test_grievance_list_filtered_by_score 2'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 31,
                    'line': 2
                }
            ],
            'message': "Variable '$scoreMin' got invalid value 900; String cannot represent a non string value: 900"
        },
        {
            'locations': [
                {
                    'column': 50,
                    'line': 2
                }
            ],
            'message': "Variable '$scoreMax' got invalid value 999; String cannot represent a non string value: 999"
        }
    ]
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
                        'createdAt': '2020-08-22T00:00:00+00:00',
                        'description': 'Just random description',
                        'language': 'Polish, English',
                        'status': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_query_all_0_with_permission 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2020-03-12T00:00:00+00:00',
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
                        'createdAt': '2020-07-12T00:00:00+00:00',
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
                        'createdAt': '2020-08-22T00:00:00+00:00',
                        'description': 'Just random description',
                        'language': 'Polish, English',
                        'status': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_query_all_1_without_permission 1'] = {
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

snapshots['TestGrievanceQuery::test_grievance_query_single_0_with_permission 1'] = {
    'data': {
        'grievanceTicket': {
            'admin': 'City Example',
            'category': 7,
            'consent': True,
            'createdAt': '2020-08-22T00:00:00+00:00',
            'description': 'Just random description',
            'language': 'Polish, English',
            'status': 3
        }
    }
}

snapshots['TestGrievanceQuery::test_grievance_query_single_1_without_permission 1'] = {
    'data': {
        'grievanceTicket': None
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
                'grievanceTicket'
            ]
        }
    ]
}
