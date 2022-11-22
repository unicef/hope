# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_with_household_and_individual_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'referralTicketDetails': {
                    'household': None,
                    'individual': None
                }
            }
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 8
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'updateGrievanceTicket',
                'grievanceTicket',
                'referralTicketDetails',
                'household'
            ]
        },
        {
            'locations': [
                {
                    'column': 17,
                    'line': 11
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'updateGrievanceTicket',
                'grievanceTicket',
                'referralTicketDetails',
                'individual'
            ]
        }
    ]
}

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_with_household_and_individual_extras_1_without_permission 1'] = {
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

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_with_household_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'referralTicketDetails': {
                    'household': None,
                    'individual': None
                }
            }
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 8
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'updateGrievanceTicket',
                'grievanceTicket',
                'referralTicketDetails',
                'household'
            ]
        }
    ]
}

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_with_household_extras_1_without_permission 1'] = {
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

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_with_individual_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'referralTicketDetails': {
                    'household': None,
                    'individual': None
                }
            }
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 11
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'updateGrievanceTicket',
                'grievanceTicket',
                'referralTicketDetails',
                'individual'
            ]
        }
    ]
}

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_with_individual_extras_1_without_permission 1'] = {
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

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_without_extras_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'referralTicketDetails': {
                    'household': None,
                    'individual': None
                }
            }
        }
    }
}

snapshots['TestGrievanceUpdateReferralTicketQuery::test_update_referral_ticket_without_extras_1_without_permission 1'] = {
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
