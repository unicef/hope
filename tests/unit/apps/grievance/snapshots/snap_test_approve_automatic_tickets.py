# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceApproveAutomaticMutation::test_approve_needs_adjudication_0_with_permission 1'] = {
    'data': {
        'approveNeedsAdjudication': {
            'grievanceTicket': {
                'description': 'needs_adjudication_grievance_ticket',
                'needsAdjudicationTicketDetails': {
                    'selectedIndividual': {
                        'unicefId': 'IND-222-222'
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
                'description': 'needs_adjudication_grievance_ticket',
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
                'description': 'needs_adjudication_grievance_ticket',
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
                'description': 'needs_adjudication_grievance_ticket',
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
                'description': 'needs_adjudication_grievance_ticket',
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
                'description': 'system_flagging_grievance_ticket',
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
