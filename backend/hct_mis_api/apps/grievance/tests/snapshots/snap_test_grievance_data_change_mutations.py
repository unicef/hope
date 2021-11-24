# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_create_individual_data_change_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_delete_individual_data_change_0_with_permission 1'] = {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_delete_individual_data_change_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_update_household_data_change_0_with_permission 1'] = {
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
                            'country': {
                                'approve_status': False,
                                'previous_value': 'AFG',
                                'value': 'AFG'
                            },
                            'female_age_group_6_11_count': {
                                'approve_status': False,
                                'previous_value': 2,
                                'value': 14
                            },
                            'flex_fields': {
                            },
                            'size': {
                                'approve_status': False,
                                'previous_value': 3,
                                'value': 4
                            }
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_update_household_data_change_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_update_individual_data_change_0_with_permission 1'] = {
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
                            'birth_date': {
                                'approve_status': False,
                                'previous_value': '1943-07-30',
                                'value': '1980-02-01'
                            },
                            'documents': [
                            ],
                            'documents_to_edit': [
                            ],
                            'documents_to_remove': [
                            ],
                            'flex_fields': {
                            },
                            'full_name': {
                                'approve_status': False,
                                'previous_value': 'Benjamin Butler',
                                'value': 'Test Test'
                            },
                            'given_name': {
                                'approve_status': False,
                                'previous_value': 'Benjamin',
                                'value': 'Test'
                            },
                            'identities': [
                            ],
                            'identities_to_edit': [
                            ],
                            'identities_to_remove': [
                            ],
                            'marital_status': {
                                'approve_status': False,
                                'previous_value': 'WIDOWED',
                                'value': 'SINGLE'
                            },
                            'previous_documents': {
                            },
                            'previous_identities': {
                            },
                            'sex': {
                                'approve_status': False,
                                'previous_value': 'FEMALE',
                                'value': 'MALE'
                            }
                        }
                    },
                    'issueType': 14,
                    'sensitiveTicketDetails': None
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_update_individual_data_change_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_create_individual_data_change_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'addIndividualTicketDetails': {
                        'household': {
                            'id': 'SG91c2Vob2xkTm9kZTowN2E5MDFlZC1kMmE1LTQyMmEtYjk2Mi0zNTcwZGExZDVkMDc='
                        },
                        'individualData': {
                            'birth_date': '1980-02-01',
                            'documents': [
                            ],
                            'estimated_birth_date': False,
                            'family_name': 'Romaniak',
                            'flex_fields': {
                            },
                            'full_name': 'Test Test',
                            'given_name': 'Test',
                            'marital_status': 'SINGLE',
                            'relationship': 'UNKNOWN',
                            'role': 'NO_ROLE',
                            'sex': 'MALE'
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
