# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_and_individual_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 5,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'negativeFeedbackTicketDetails': {
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
                'negativeFeedbackTicketDetails',
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
                'negativeFeedbackTicketDetails',
                'individual'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_and_individual_extras_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 5,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'negativeFeedbackTicketDetails': {
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
                'negativeFeedbackTicketDetails',
                'household'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_extras_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_individual_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 5,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'negativeFeedbackTicketDetails': {
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
                'negativeFeedbackTicketDetails',
                'individual'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_individual_extras_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_without_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 5,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'negativeFeedbackTicketDetails': {
                        'household': None,
                        'individual': None
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_without_extras_1_without_permission 1'] = {
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
