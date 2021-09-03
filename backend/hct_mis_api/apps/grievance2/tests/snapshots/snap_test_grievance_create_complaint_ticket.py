# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 4,
                    'complaintTicketDetails': {
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
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English'
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_with_two_payment_records_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 4,
                    'complaintTicketDetails': {
                        'household': {
                            'size': 1
                        },
                        'individual': {
                            'fullName': 'John Doe'
                        },
                        'paymentRecord': {
                            'fullName': 'John Doe second Individual'
                        }
                    },
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English'
                },
                {
                    'admin': 'City Test',
                    'category': 4,
                    'complaintTicketDetails': {
                        'household': {
                            'size': 1
                        },
                        'individual': {
                            'fullName': 'John Doe'
                        },
                        'paymentRecord': {
                            'fullName': 'John Doe second Individual'
                        }
                    },
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English'
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_with_two_payment_records_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_extras_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 4,
                    'complaintTicketDetails': {
                        'household': None,
                        'individual': None,
                        'paymentRecord': None
                    },
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English'
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_extras_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_household_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 4,
                    'complaintTicketDetails': {
                        'household': None,
                        'individual': {
                            'fullName': 'John Doe'
                        },
                        'paymentRecord': {
                            'fullName': 'John Doe'
                        }
                    },
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English'
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_household_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_individual_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 4,
                    'complaintTicketDetails': {
                        'household': {
                            'size': 1
                        },
                        'individual': None,
                        'paymentRecord': {
                            'fullName': 'John Doe'
                        }
                    },
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English'
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_individual_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_payment_record_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 4,
                    'complaintTicketDetails': {
                        'household': {
                            'size': 1
                        },
                        'individual': {
                            'fullName': 'John Doe'
                        },
                        'paymentRecord': None
                    },
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English'
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_payment_record_1_without_permission 1'] = {
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
