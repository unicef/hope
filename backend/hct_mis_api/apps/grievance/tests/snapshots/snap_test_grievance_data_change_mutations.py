# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_create_individual_data_change 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'addIndividualTicketDetails': {
                        'household': {
                            'id': 'SG91c2Vob2xkTm9kZTowN2E5MDFlZC1kMmE1LTQyMmEtYjk2Mi0zNTcwZGExZDVkMDc='
                        },
                        'individualData': {
                            'birth_date': {
                                'approve_status': False,
                                'value': '1980-02-01'
                            },
                            'family_name': {
                                'approve_status': False,
                                'value': 'Romaniak'
                            },
                            'full_name': {
                                'approve_status': False,
                                'value': 'Test Test'
                            },
                            'given_name': {
                                'approve_status': False,
                                'value': 'Test'
                            },
                            'marital_status': {
                                'approve_status': False,
                                'value': 'SINGLE'
                            },
                            'sex': {
                                'approve_status': False,
                                'value': 'MALE'
                            }
                        }
                    },
                    'category': 2,
                    'description': 'Test',
                    'householdDataUpdateTicketDetails': None,
                    'individualDataUpdateTicketDetails': None,
                    'issueType': 16,
                    'sensitiveTicketDetails': None
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_delete_individual_data_change 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'addIndividualTicketDetails': None,
                    'category': 2,
                    'description': 'Test',
                    'householdDataUpdateTicketDetails': None,
                    'individualDataUpdateTicketDetails': None,
                    'issueType': 15,
                    'sensitiveTicketDetails': None
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_update_household_data_change 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'addIndividualTicketDetails': None,
                    'category': 2,
                    'description': 'Test',
                    'householdDataUpdateTicketDetails': {
                        'household': {
                            'id': 'SG91c2Vob2xkTm9kZTowN2E5MDFlZC1kMmE1LTQyMmEtYjk2Mi0zNTcwZGExZDVkMDc='
                        },
                        'householdData': {
                            'female_age_group_6_11_count': 14
                        }
                    },
                    'individualDataUpdateTicketDetails': None,
                    'issueType': 13,
                    'sensitiveTicketDetails': None
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_update_individual_data_change 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'addIndividualTicketDetails': None,
                    'category': 2,
                    'description': 'Test',
                    'householdDataUpdateTicketDetails': None,
                    'individualDataUpdateTicketDetails': {
                        'individual': {
                            'fullName': 'Benjamin Butler'
                        },
                        'individualData': {
                            'birth_date': '1980-02-01',
                            'full_name': 'Test Test',
                            'given_name': 'Test',
                            'marital_status': 'SINGLE',
                            'sex': 'MALE'
                        }
                    },
                    'issueType': 14,
                    'sensitiveTicketDetails': None
                }
            ]
        }
    }
}
