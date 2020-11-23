# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_add_individual 1'] = {
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

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_update_household 1'] = {
    'data': {
        'approveHouseholdDataChange': {
            'grievanceTicket': {
                'householdDataUpdateTicketDetails': {
                    'householdData': {
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

snapshots['TestGrievanceApproveDataChangeMutation::test_approve_update_individual 1'] = {
    'data': {
        'approveIndividualDataChange': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTphY2Q1N2FhMS1lZmQ4LTRjODEtYWMxOS1iOGNhYmViZTgwODk=',
                'individualDataUpdateTicketDetails': {
                    'individualData': {
                        'family_name': {
                            'approve_status': True,
                            'value': 'Example'
                        },
                        'full_name': {
                            'approve_status': True,
                            'value': 'Test Example'
                        },
                        'given_name': {
                            'approve_status': True,
                            'value': 'Test'
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
