# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_0_without_permission 1'] = {
    'data': {
        'actionPaymentPlanMutation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'actionPaymentPlanMutation'
            ]
        }
    ]
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_1_not_possible_reject 1'] = {
    'data': {
        'actionPaymentPlanMutation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Not possible to create REJECT for Payment Plan within status OPEN',
            'path': [
                'actionPaymentPlanMutation'
            ]
        }
    ]
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_2_lock_approve_authorize_reject 1'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                    ],
                    'totalCount': 0
                },
                'status': 'LOCKED'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_2_lock_approve_authorize_reject 2'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                    ],
                                    'authorization': [
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': None,
                                'sentForFinanceReviewBy': None
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_APPROVAL'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_2_lock_approve_authorize_reject 3'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'lock_approve_authorize_reject, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': None,
                                'sentForFinanceReviewBy': None
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_APPROVAL'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_2_lock_approve_authorize_reject 4'] = {
    'data': {
        'actionPaymentPlanMutation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Not possible to create AUTHORIZE for Payment Plan within status IN_APPROVAL',
            'path': [
                'actionPaymentPlanMutation'
            ]
        }
    ]
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_2_lock_approve_authorize_reject 5'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'lock_approve_authorize_reject, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                        {
                                            'comment': 'lock_approve_authorize_reject, action: REJECT',
                                            'info': 'Rejected by Rachel Walker'
                                        }
                                    ]
                                },
                                'rejectedOn': 'IN_APPROVAL',
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': None,
                                'sentForFinanceReviewBy': None
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'LOCKED'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 1'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                    ],
                                    'authorization': [
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': None,
                                'sentForFinanceReviewBy': None
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_APPROVAL'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 2'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': None,
                                'sentForFinanceReviewBy': None
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_APPROVAL'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 3'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForFinanceReviewBy': None
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_AUTHORIZATION'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 4'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        }
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForFinanceReviewBy': None
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_AUTHORIZATION'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 5'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        }
                                    ],
                                    'financeReview': [
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForFinanceReviewBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                }
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_REVIEW'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 6'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        }
                                    ],
                                    'financeReview': [
                                        {
                                            'comment': 'all_steps, action: REVIEW',
                                            'info': 'Reviewed by Rachel Walker'
                                        }
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForFinanceReviewBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                }
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_REVIEW'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 7'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        }
                                    ],
                                    'financeReview': [
                                        {
                                            'comment': 'all_steps, action: REVIEW',
                                            'info': 'Reviewed by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: REVIEW',
                                            'info': 'Reviewed by Rachel Walker'
                                        }
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForFinanceReviewBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                }
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'IN_REVIEW'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_3_all_steps 8'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                        {
                            'node': {
                                'actions': {
                                    'approval': [
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: APPROVE',
                                            'info': 'Approved by Rachel Walker'
                                        }
                                    ],
                                    'authorization': [
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: AUTHORIZE',
                                            'info': 'Authorized by Rachel Walker'
                                        }
                                    ],
                                    'financeReview': [
                                        {
                                            'comment': 'all_steps, action: REVIEW',
                                            'info': 'Reviewed by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: REVIEW',
                                            'info': 'Reviewed by Rachel Walker'
                                        },
                                        {
                                            'comment': 'all_steps, action: REVIEW',
                                            'info': 'Reviewed by Rachel Walker'
                                        }
                                    ],
                                    'reject': [
                                    ]
                                },
                                'rejectedOn': None,
                                'sentForApprovalBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForAuthorizationBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                },
                                'sentForFinanceReviewBy': {
                                    'firstName': 'Rachel',
                                    'lastName': 'Walker'
                                }
                            }
                        }
                    ],
                    'totalCount': 1
                },
                'status': 'ACCEPTED'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_4_reject_if_accepted 1'] = {
    'data': {
        'actionPaymentPlanMutation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Not possible to create REJECT for Payment Plan within status ACCEPTED',
            'path': [
                'actionPaymentPlanMutation'
            ]
        }
    ]
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_5_lock_unlock 1'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                    ],
                    'totalCount': 0
                },
                'status': 'OPEN'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_5_lock_unlock 2'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                    ],
                    'totalCount': 0
                },
                'status': 'LOCKED'
            }
        }
    }
}

snapshots['TestActionPaymentPlanMutation::test_update_status_payment_plan_5_lock_unlock 3'] = {
    'data': {
        'actionPaymentPlanMutation': {
            'paymentPlan': {
                'approvalProcess': {
                    'edges': [
                    ],
                    'totalCount': 0
                },
                'status': 'OPEN'
            }
        }
    }
}
