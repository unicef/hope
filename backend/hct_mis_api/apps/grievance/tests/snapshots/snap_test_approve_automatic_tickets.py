# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_system_flagging 1'] = {
    'data': {
        'approveSystemFlagging': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo0M2M1OWVkYS02NjY0LTQxZDYtOTMzOS0wNWVmY2IxMWRhODI=',
                'systemFlaggingTicketDetails': {
                    'approveStatus': False
                }
            }
        }
    }
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication 1'] = {
    'data': {
        'approveNeedsAdjudication': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyYjQxOWNlMy0zMjk3LTQ3ZWUtYTQ3Zi00MzQ0MmFiYWM3M2U=',
                'needsAdjudicationTicketDetails': {
                    'selectedIndividual': {
                        'id': 'SW5kaXZpZHVhbE5vZGU6OTRiMDlmZjItOWU2ZC00ZjM0LWE3MmMtYzMxOWUxZGI3MTE1'
                    }
                }
            }
        }
    }
}
