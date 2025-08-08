# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPaymentPlanReconciliation::test_apply_steficon_rule_with_wrong_payment_plan_status 1'] = {
    'data': {
        'setSteficonRuleOnPaymentPlanPaymentList': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': "You can run formula only for 'Locked', 'Error' or 'Completed' statuses.",
            'path': [
                'setSteficonRuleOnPaymentPlanPaymentList'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_apply_steficon_rule_with_wrong_payment_plan_status 2'] = {
    'data': {
        'setSteficonRuleOnPaymentPlanPaymentList': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Rule Engine run in progress',
            'path': [
                'setSteficonRuleOnPaymentPlanPaymentList'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_correct_message_displayed_when_file_is_protected 1'] = {
    'data': {
        'importXlsxPaymentPlanPaymentListPerFsp': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Wrong file type or password protected .zip file. Upload another file, or remove the password.',
            'path': [
                'importXlsxPaymentPlanPaymentListPerFsp'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_error_message_when_engine_rule_not_enabled_or_deprecated 1'] = {
    'data': {
        'setSteficonRuleOnPaymentPlanPaymentList': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'This engine rule is not enabled or is deprecated.',
            'path': [
                'setSteficonRuleOnPaymentPlanPaymentList'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_error_message_when_engine_rule_not_enabled_or_deprecated 2'] = {
    'data': {
        'setSteficonRuleOnPaymentPlanPaymentList': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'This engine rule is not enabled or is deprecated.',
            'path': [
                'setSteficonRuleOnPaymentPlanPaymentList'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_export_xlsx_per_fsp_error_msg 1'] = {
    'data': {
        'exportXlsxPaymentPlanPaymentListPerFsp': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans.',
            'path': [
                'exportXlsxPaymentPlanPaymentListPerFsp'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_export_xlsx_per_fsp_error_msg 2'] = {
    'data': {
        'exportXlsxPaymentPlanPaymentListPerFsp': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Export failed: The Payment List is empty.',
            'path': [
                'exportXlsxPaymentPlanPaymentListPerFsp'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_export_xlsx_per_fsp_error_msg 3'] = {
    'data': {
        'exportXlsxPaymentPlanPaymentListPerFsp': {
            'paymentPlan': {
                'canCreateXlsxWithFspAuthCode': True,
                'canRegenerateExportFilePerFsp': True,
                'hasPaymentListExportFile': True,
                'status': 'ACCEPTED'
            }
        }
    }
}

snapshots['TestPaymentPlanReconciliation::test_export_xlsx_per_fsp_with_auth_code 1'] = {
    'data': {
        'exportXlsxPaymentPlanPaymentListPerFsp': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'Export failed: There could be not Pending Payments and FSP communication channel should be set to API.',
            'path': [
                'exportXlsxPaymentPlanPaymentListPerFsp'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_export_xlsx_per_fsp_with_auth_code 2'] = {
    'data': {
        'exportXlsxPaymentPlanPaymentListPerFsp': {
            'paymentPlan': {
                'canCreateXlsxWithFspAuthCode': True,
                'canRegenerateExportFilePerFsp': True,
                'hasPaymentListExportFile': True,
                'status': 'FINISHED'
            }
        }
    }
}

snapshots['TestPaymentPlanReconciliation::test_follow_up_pp_entitlements_can_be_changed_with_steficon_rule 1'] = {
    'data': {
        'setSteficonRuleOnPaymentPlanPaymentList': {
            'paymentPlan': {
                'unicefId': 'PP-0060-23-00000002'
            }
        }
    }
}

snapshots['TestPaymentPlanReconciliation::test_follow_up_pp_entitlements_updated_with_file 1'] = {
    'data': {
        'importXlsxPaymentPlanPaymentList': {
            'errors': [
                {
                    'coordinates': 'A2',
                    'message': 'This payment id 714a72db-79e3-42d1-a9e8-a949aebbf1ae is not in Payment Plan Payment List',
                    'sheet': 'Payment Plan - Payment List'
                },
                {
                    'coordinates': 'A3',
                    'message': 'This payment id a15e9214-a0e0-4af5-8dbf-9657184e9e3a is not in Payment Plan Payment List',
                    'sheet': 'Payment Plan - Payment List'
                },
                {
                    'coordinates': None,
                    'message': "There aren't any updates in imported file, please add changes and try again",
                    'sheet': 'Payment Plan - Payment List'
                }
            ],
            'paymentPlan': None
        }
    }
}

snapshots['TestPaymentPlanReconciliation::test_import_with_wrong_payment_plan_status 1'] = {
    'data': {
        'importXlsxPaymentPlanPaymentListPerFsp': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 5,
                    'line': 3
                }
            ],
            'message': 'You can only import for ACCEPTED or FINISHED Payment Plan',
            'path': [
                'importXlsxPaymentPlanPaymentListPerFsp'
            ]
        }
    ]
}
