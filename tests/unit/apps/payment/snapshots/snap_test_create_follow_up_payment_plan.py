# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateFollowUpPaymentPlan::test_create_follow_up_pp_mutation 1'] = {
    'data': {
        'createFollowUpPaymentPlan': {
            'paymentPlan': {
                'canCreateFollowUp': False,
                'isFollowUp': True,
                'status': 'OPEN',
                'totalWithdrawnHouseholdsCount': 0
            }
        }
    }
}
