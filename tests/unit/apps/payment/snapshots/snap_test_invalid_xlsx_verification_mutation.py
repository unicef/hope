# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestXlsxVerificationMarkAsInvalid::test_export_xlsx_payment_verification_plan_0_with_permission_was_downloaded_false 1'] = {
    'data': {
        'invalidPaymentVerificationPlan': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'You can mark invalid if xlsx file was downloaded or imported',
            'path': [
                'invalidPaymentVerificationPlan'
            ]
        }
    ]
}

snapshots['TestXlsxVerificationMarkAsInvalid::test_export_xlsx_payment_verification_plan_1_with_permission_was_downloaded_true 1'] = {
    'data': {
        'invalidPaymentVerificationPlan': {
            'paymentPlan': {
                'verificationPlans': {
                    'edges': [
                        {
                            'node': {
                                'status': 'INVALID',
                                'xlsxFileExporting': False,
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

snapshots['TestXlsxVerificationMarkAsInvalid::test_export_xlsx_payment_verification_plan_2_without_permission 1'] = {
    'data': {
        'invalidPaymentVerificationPlan': None
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
                'invalidPaymentVerificationPlan'
            ]
        }
    ]
}
