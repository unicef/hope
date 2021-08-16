# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_and_individual_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'negativeFeedbackTicketDetails': {
                    'household': {
                        'size': 1
                    },
                    'individual': {
                        'fullName': 'John Doe'
                    }
                }
            }
        }
    }
}

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_and_individual_extras_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'negativeFeedbackTicketDetails': {
                    'household': {
                        'size': 1
                    },
                    'individual': None
                }
            }
        }
    }
}

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_household_extras_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_individual_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'negativeFeedbackTicketDetails': {
                    'household': None,
                    'individual': {
                        'fullName': 'John Doe'
                    }
                }
            }
        }
    }
}

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_with_individual_extras_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_without_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'negativeFeedbackTicketDetails': {
                    'household': None,
                    'individual': None
                }
            }
        }
    }
}

snapshots['TestGrievanceUpdateNegativeFeedbackTicketQuery::test_create_negative_feedback_ticket_without_extras_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}
