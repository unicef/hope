# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPaymentPlanReconciliation::test_follow_up_pp_entitlements_can_be_changed_with_steficon_rule 1'] = {
    'data': {
        'setSteficonRuleOnPaymentPlanPaymentList': {
            'paymentPlan': {
                'unicefId': 'PP-0060-23-00000001'
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
