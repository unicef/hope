# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_with_household_and_individual_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 7,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'positiveFeedbackTicketDetails': {
                        'household': None,
                        'individual': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 11
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'positiveFeedbackTicketDetails',
                'household'
            ]
        },
        {
            'locations': [
                {
                    'column': 13,
                    'line': 14
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'positiveFeedbackTicketDetails',
                'individual'
            ]
        }
    ]
}

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_with_household_and_individual_extras_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_with_household_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 7,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'positiveFeedbackTicketDetails': {
                        'household': None,
                        'individual': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 11
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'positiveFeedbackTicketDetails',
                'household'
            ]
        }
    ]
}

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_with_household_extras_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_with_individual_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 7,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'positiveFeedbackTicketDetails': {
                        'household': None,
                        'individual': None
                    }
                }
            ]
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 14
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'createGrievanceTicket',
                'grievanceTickets',
                0,
                'positiveFeedbackTicketDetails',
                'individual'
            ]
        }
    ]
}

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_with_individual_extras_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_without_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 7,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'positiveFeedbackTicketDetails': {
                        'household': None,
                        'individual': None
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreatePositiveFeedbackTicketQuery::test_create_positive_feedback_ticket_without_extras_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}
