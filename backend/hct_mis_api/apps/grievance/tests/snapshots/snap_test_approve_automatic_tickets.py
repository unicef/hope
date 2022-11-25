# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_0_with_permission 1'] = {
    'data': {
        'approveNeedsAdjudication': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyYjQxOWNlMy0zMjk3LTQ3ZWUtYTQ3Zi00MzQ0MmFiYWM3M2U=',
                'needsAdjudicationTicketDetails': {
                    'selectedIndividual': None
                }
            }
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 13
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'approveNeedsAdjudication',
                'grievanceTicket',
                'needsAdjudicationTicketDetails',
                'selectedIndividual'
            ]
        }
    ]
}
