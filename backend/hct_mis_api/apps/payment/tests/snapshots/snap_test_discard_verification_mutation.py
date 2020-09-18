# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestDiscardVerificationMutation::test_discard_active 1'] = {
    'data': {
        'discardCashPlanPaymentVerification': {
            'cashPlan': {
                'id': 'Q2FzaFBsYW5Ob2RlOmQ5NTBiYTQ5LTc0OGUtNDBjNy05ZTI4LThhNTdkM2Y1MzFlZg=='
            }
        }
    }
}
