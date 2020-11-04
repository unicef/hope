# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': {
                            'size': 1
                        },
                        'individual': {
                            'fullName': 'John Doe'
                        },
                        'paymentRecord': {
                            'fullName': 'John Doe'
                        }
                    },
                    'status': 1
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_extras 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    },
                    'status': 1
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_household 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': None,
                        'individual': {
                            'fullName': 'John Doe'
                        },
                        'paymentRecord': {
                            'fullName': 'John Doe'
                        }
                    },
                    'status': 1
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_individual 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': {
                            'size': 1
                        },
                        'individual': None,
                        'paymentRecord': {
                            'fullName': 'John Doe'
                        }
                    },
                    'status': 1
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_payment_record 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 3,
                    'consent': True,
                    'description': 'Test Feedback',
                    'issueType': 12,
                    'language': 'Polish, English',
                    'sensitiveTicketDetails': {
                        'household': {
                            'size': 1
                        },
                        'individual': {
                            'fullName': 'John Doe'
                        },
                        'paymentRecord': None
                    },
                    'status': 1
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_without_issue_type 1'] = {
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
            'message': 'You have to provide issue_type in 3',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceCreateSensitiveTicketQuery::test_create_sensitive_ticket_wrong_extras 1'] = {
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
            'message': "You can't provide extras.category.grievance_complaint_ticket_extras in 3",
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}
