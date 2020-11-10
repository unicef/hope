# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_extras 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_household 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_individual 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_without_payment_record 1'] = {
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

snapshots['TestGrievanceCreateComplaintTicketQuery::test_create_complaint_ticket_with_two_payment_records 1'] = {
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
