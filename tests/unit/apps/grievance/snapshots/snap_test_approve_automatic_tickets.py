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
                    'selectedIndividual': {
                        'id': 'SW5kaXZpZHVhbE5vZGU6OTRiMDlmZjItOWU2ZC00ZjM0LWE3MmMtYzMxOWUxZGI3MTE1'
                    }
                }
            }
        }
    }
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_1_without_permission 1'] = {
    'data': {
        'approveNeedsAdjudication': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'approveNeedsAdjudication'
            ]
        }
    ]
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_new_input_fields 1'] = {
    'data': {
        'approveNeedsAdjudication': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Only one option for duplicate or distinct or clear individuals is available',
            'path': [
                'approveNeedsAdjudication'
            ]
        }
    ]
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_new_input_fields 2'] = {
    'data': {
        'approveNeedsAdjudication': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': '["A user can not flag individuals when a ticket is not in the \'For Approval\' status"]',
            'path': [
                'approveNeedsAdjudication'
            ]
        }
    ]
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_new_input_fields 3'] = {
    'data': {
        'approveNeedsAdjudication': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyYjQxOWNlMy0zMjk3LTQ3ZWUtYTQ3Zi00MzQ0MmFiYWM3M2U=',
                'needsAdjudicationTicketDetails': {
                    'extraData': {
                        'dedupEngineSimilarityPair': None
                    },
                    'selectedDistinct': [
                    ],
                    'selectedDuplicates': [
                        {
                            'unicefId': 'IND-222-222'
                        }
                    ],
                    'selectedIndividual': None
                }
            }
        }
    }
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_new_input_fields 4'] = {
    'data': {
        'approveNeedsAdjudication': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyYjQxOWNlMy0zMjk3LTQ3ZWUtYTQ3Zi00MzQ0MmFiYWM3M2U=',
                'needsAdjudicationTicketDetails': {
                    'extraData': {
                        'dedupEngineSimilarityPair': None
                    },
                    'selectedDistinct': [
                        {
                            'unicefId': 'IND-123-123'
                        }
                    ],
                    'selectedDuplicates': [
                        {
                            'unicefId': 'IND-222-222'
                        }
                    ],
                    'selectedIndividual': None
                }
            }
        }
    }
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_new_input_fields 5'] = {
    'data': {
        'approveNeedsAdjudication': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyYjQxOWNlMy0zMjk3LTQ3ZWUtYTQ3Zi00MzQ0MmFiYWM3M2U=',
                'needsAdjudicationTicketDetails': {
                    'extraData': {
                        'dedupEngineSimilarityPair': None
                    },
                    'selectedDistinct': [
                    ],
                    'selectedDuplicates': [
                        {
                            'unicefId': 'IND-222-222'
                        }
                    ],
                    'selectedIndividual': None
                }
            }
        }
    }
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_should_allow_uncheck_selected_individual_0_with_permission 1'] = {
    'data': {
        'approveNeedsAdjudication': {
            'grievanceTicket': {
                'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToyYjQxOWNlMy0zMjk3LTQ3ZWUtYTQ3Zi00MzQ0MmFiYWM3M2U=',
                'needsAdjudicationTicketDetails': {
                    'selectedIndividual': None
                }
            }
        }
    }
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_should_allow_uncheck_selected_individual_1_without_permission 1'] = {
    'data': {
        'approveNeedsAdjudication': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'approveNeedsAdjudication'
            ]
        }
    ]
}

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_system_flagging_0_with_permission 1'] = {
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

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_system_flagging_1_without_permission 1'] = {
    'data': {
        'approveSystemFlagging': None
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
                'approveSystemFlagging'
            ]
        }
    ]
}
