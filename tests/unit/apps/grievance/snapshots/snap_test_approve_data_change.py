# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_add_individual_0_with_permission 1'] = {
    'data': {
        'approveAddIndividual': {
            'grievanceTicket': {
                'addIndividualTicketDetails': {
                    'approveStatus': True
                },
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0M2M1OWVkYS02NjY0LTQxZDYtOTMzOS0wNWVmY2IxMWRhODI='
            }
        }
    }
}

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_add_individual_1_without_permission 1'] = {
    'data': {
        'approveAddIndividual': None
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
                'approveAddIndividual'
            ]
        }
    ]
}

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_update_household_0_with_permission 1'] = {
    'data': {
        'approveHouseholdDataChange': {
            'grievanceTicket': {
                'householdDataUpdateTicketDetails': {
                    'householdData': {
                        'flex_fields': {
                        },
                        'size': {
                            'approve_status': False,
                            'value': 19
                        },
                        'village': {
                            'approve_status': True,
                            'value': 'Test Village'
                        }
                    }
                },
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo3MmVlN2Q5OC02MTA4LTRlZjAtODViZC0yZWYyMGUxZDU0MTA='
            }
        }
    }
}

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_update_household_1_without_permission 1'] = {
    'data': {
        'approveHouseholdDataChange': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'approveHouseholdDataChange'
            ]
        }
    ]
}

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_update_individual_0_with_permission 1'] = {
    'data': {
        'approveIndividualDataChange': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTphY2Q1N2FhMS1lZmQ4LTRjODEtYWMxOS1iOGNhYmViZTgwODk=',
                'individualDataUpdateTicketDetails': {
                    'individualData': {
                        'birth_date': {
                            'approve_status': False,
                            'value': '1980-02-01'
                        },
                        'documents': [
                            {
                                'approve_status': True,
                                'value': {
                                    'country': 'POL',
                                    'number': '999-888-777',
                                    'type': 'NATIONAL_ID'
                                }
                            }
                        ],
                        'documents_to_edit': [
                            {
                                'approve_status': True,
                                'previous_value': {
                                    'country': 'POL',
                                    'id': 'RG9jdW1lbnROb2RlOmRmMWNlNmU4LTI4NjQtNGMzZi04MDNkLTE5ZWM2ZjRjNDdmMw==',
                                    'number': '789-789-645',
                                    'photo': '',
                                    'type': 'NATIONAL_ID'
                                },
                                'value': {
                                    'country': None,
                                    'id': 'RG9jdW1lbnROb2RlOmRmMWNlNmU4LTI4NjQtNGMzZi04MDNkLTE5ZWM2ZjRjNDdmMw==',
                                    'number': '999-888-666',
                                    'photo': '',
                                    'type': None
                                }
                            }
                        ],
                        'documents_to_remove': [
                            {
                                'approve_status': True,
                                'value': 'RG9jdW1lbnROb2RlOmRmMWNlNmU4LTI4NjQtNGMzZi04MDNkLTE5ZWM2ZjRjNDdmMw=='
                            },
                            {
                                'approve_status': False,
                                'value': 'RG9jdW1lbnROb2RlOjhhZDVlM2I4LTRjNGQtNGMxMC04NzU2LTExOGQ4NjA5NWRkMA=='
                            }
                        ],
                        'family_name': {
                            'approve_status': True,
                            'value': 'Example'
                        },
                        'flex_fields': {
                        },
                        'full_name': {
                            'approve_status': True,
                            'value': 'Test Example'
                        },
                        'given_name': {
                            'approve_status': True,
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
                }
            }
        }
    }
}

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_update_individual_1_without_permission 1'] = {
    'data': {
        'approveIndividualDataChange': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 16
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'approveIndividualDataChange'
            ]
        }
    ]
}
