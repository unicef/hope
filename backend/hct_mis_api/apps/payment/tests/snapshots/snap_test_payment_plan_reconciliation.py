# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPaymentPlanReconciliation::test_follow_up_pp_entitlements_cannot_be_changed_with_file_import 1'] = {
    'data': {
        'importXlsxPaymentPlanPaymentList': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 65,
                    'line': 2
                }
            ],
            'message': 'Entitlements of follow-up payment plan cannot be changed',
            'path': [
                'importXlsxPaymentPlanPaymentList'
            ]
        }
    ]
}

snapshots['TestPaymentPlanReconciliation::test_follow_up_pp_entitlements_cannot_be_changed_with_steficon_rule 1'] = {
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
            'message': 'Entitlements of follow-up payment plan cannot be changed',
            'path': [
                'setSteficonRuleOnPaymentPlanPaymentList'
            ]
        }
    ]
}
