# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceCreateDataChangeMutation::test_create_payment_channel_for_individual_0_with_permission 1'] = {
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
                            'documents': [
                            ],
                            'documents_to_edit': [
                            ],
                            'documents_to_remove': [
                            ],
                            'flex_fields': {
                            },
                            'identities': [
                            ],
                            'identities_to_edit': [
                            ],
                            'identities_to_remove': [
                            ],
                            'payment_channels': [
                                {
                                    'approve_status': False,
                                    'value': {
                                        'bank_account_number': '2356789789789789',
                                        'bank_name': 'privatbank',
                                        'type': 'BANK_TRANSFER'
                                    }
                                }
                            ],
                            'payment_channels_to_edit': [
                            ],
                            'payment_channels_to_remove': [
                            ],
                            'previous_documents': {
                            },
                            'previous_identities': {
                            },
                            'previous_payment_channels': {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_create_payment_channel_for_individual_1_without_permission 1'] = {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_edit_payment_channel_for_individual_0_with_permission 1'] = {
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
                            'documents': [
                            ],
                            'documents_to_edit': [
                            ],
                            'documents_to_remove': [
                            ],
                            'flex_fields': {
                            },
                            'identities': [
                            ],
                            'identities_to_edit': [
                            ],
                            'identities_to_remove': [
                            ],
                            'payment_channels': [
                            ],
                            'payment_channels_to_edit': [
                                {
                                    'approve_status': False,
                                    'previous_value': {
                                        'bank_account_number': '2356789789789789',
                                        'bank_name': 'privatbank',
                                        'id': 'QmFua0FjY291bnRJbmZvTm9kZTo0MTNiMmEwNy00YmMxLTQzYTctODBlNi05MWFiYjQ4NmFhOWQ=',
                                        'individual': 'SW5kaXZpZHVhbE5vZGU6YjZmZmIyMjctYTJkZC00MTAzLWJlNDYtMGM5ZWJlOWYwMDFh',
                                        'type': 'BANK_TRANSFER'
                                    },
                                    'value': {
                                        'bank_account_number': '1111222233334444',
                                        'bank_name': 'privatbank',
                                        'id': 'QmFua0FjY291bnRJbmZvTm9kZTo0MTNiMmEwNy00YmMxLTQzYTctODBlNi05MWFiYjQ4NmFhOWQ=',
                                        'individual': 'SW5kaXZpZHVhbE5vZGU6YjZmZmIyMjctYTJkZC00MTAzLWJlNDYtMGM5ZWJlOWYwMDFh',
                                        'type': 'BANK_TRANSFER'
                                    }
                                }
                            ],
                            'payment_channels_to_remove': [
                            ],
                            'previous_documents': {
                            },
                            'previous_identities': {
                            },
                            'previous_payment_channels': {
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

snapshots['TestGrievanceCreateDataChangeMutation::test_edit_payment_channel_for_individual_1_without_permission 1'] = {
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
                                {
                                    'country': 'POL',
                                    'number': '123-123-UX-321',
                                    'photo': '/api/uploads/test_file_name.jpg',
                                    'photoraw': 'test_file_name.jpg',
                                    'type': 'NATIONAL_ID'
                                }
                            ],
                            'estimated_birth_date': False,
                            'family_name': 'Romaniak',
                            'flex_fields': {
                            },
                            'full_name': 'Test Test',
                            'given_name': 'Test',
                            'identities': [
                                {
                                    'agency': 'UNHCR',
                                    'country': 'POL',
                                    'number': '2222'
                                }
                            ],
                            'marital_status': 'SINGLE',
                            'payment_channels': [
                                {
                                    'bank_account_number': '2356789789789789',
                                    'bank_name': 'privatbank',
                                    'type': 'BANK_TRANSFER'
                                }
                            ],
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

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_delete_household_data_change_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'addIndividualTicketDetails': None,
                    'category': 2,
                    'description': 'Test',
                    'householdDataUpdateTicketDetails': None,
                    'individualDataUpdateTicketDetails': None,
                    'issueType': 17,
                    'sensitiveTicketDetails': None
                }
            ]
        }
    }
}

snapshots['TestGrievanceCreateDataChangeMutation::test_grievance_delete_household_data_change_1_without_permission 1'] = {
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
                            'disability': {
                                'approve_status': False,
                                'previous_value': 'not disabled',
                                'value': 'disabled'
                            },
                            'documents': [
                                {
                                    'approve_status': False,
                                    'value': {
                                        'country': 'POL',
                                        'number': '321-321-XU-987',
                                        'photo': '/api/uploads/test_file_name.jpg',
                                        'photoraw': 'test_file_name.jpg',
                                        'type': 'NATIONAL_PASSPORT'
                                    }
                                }
                            ],
                            'documents_to_edit': [
                                {
                                    'approve_status': False,
                                    'previous_value': {
                                        'country': 'POL',
                                        'id': 'RG9jdW1lbnROb2RlOmQzNjdlNDMxLWI4MDctNGMxZi1hODExLWVmMmUwZDIxN2NjNA==',
                                        'number': '789-789-645',
                                        'photo': '',
                                        'photoraw': '',
                                        'type': 'NATIONAL_ID'
                                    },
                                    'value': {
                                        'country': 'POL',
                                        'id': 'RG9jdW1lbnROb2RlOmQzNjdlNDMxLWI4MDctNGMxZi1hODExLWVmMmUwZDIxN2NjNA==',
                                        'number': '321-321-XU-123',
                                        'photo': '/api/uploads/test_file_name.jpg',
                                        'photoraw': 'test_file_name.jpg',
                                        'type': 'NATIONAL_ID'
                                    }
                                }
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
                                {
                                    'approve_status': False,
                                    'value': {
                                        'agency': 'UNHCR',
                                        'country': 'POL',
                                        'number': '2222'
                                    }
                                }
                            ],
                            'identities_to_edit': [
                                {
                                    'approve_status': False,
                                    'previous_value': {
                                        'agency': 'UNHCR',
                                        'country': 'POL',
                                        'id': 'SW5kaXZpZHVhbElkZW50aXR5Tm9kZTox',
                                        'individual': 'SW5kaXZpZHVhbE5vZGU6YjZmZmIyMjctYTJkZC00MTAzLWJlNDYtMGM5ZWJlOWYwMDFh',
                                        'number': '1111'
                                    },
                                    'value': {
                                        'agency': 'UNHCR',
                                        'country': 'POL',
                                        'id': 'SW5kaXZpZHVhbElkZW50aXR5Tm9kZTox',
                                        'individual': 'SW5kaXZpZHVhbE5vZGU6YjZmZmIyMjctYTJkZC00MTAzLWJlNDYtMGM5ZWJlOWYwMDFh',
                                        'number': '3333'
                                    }
                                }
                            ],
                            'identities_to_remove': [
                            ],
                            'marital_status': {
                                'approve_status': False,
                                'previous_value': 'WIDOWED',
                                'value': 'SINGLE'
                            },
                            'payment_channels': [
                            ],
                            'payment_channels_to_edit': [
                            ],
                            'payment_channels_to_remove': [
                            ],
                            'previous_documents': {
                            },
                            'previous_identities': {
                            },
                            'previous_payment_channels': {
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
