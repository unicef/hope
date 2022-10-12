# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_and_individual_extras_0_with_permission 1'] = {
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
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
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
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
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
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
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
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
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
