# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestXlsxVerificationExport::test_export_xlsx_cash_plan_payment_verification_0_with_permission 1'] = {
    'data': {
        'exportXlsxCashPlanVerification': {
            'cashPlan': {
                'verificationPlans': {
                    'edges': [
                        {
                            'node': {
                                'hasXlsxFile': False,
                                'status': 'ACTIVE',
                                'xlsxFileExporting': True,
                                'xlsxFileImported': False,
                                'xlsxFileWasDownloaded': False
                            }
                        }
                    ]
                }
            }
        }
    }
}

snapshots['TestXlsxVerificationExport::test_export_xlsx_cash_plan_payment_verification_1_without_permission 1'] = {
    'data': {
        'exportXlsxCashPlanVerification': None
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
                'exportXlsxCashPlanVerification'
            ]
        }
    ]
}
