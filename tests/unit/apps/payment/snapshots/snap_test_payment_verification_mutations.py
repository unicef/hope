# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestPaymentVerificationMutations::test_edit_payment_verification_plan_mutation 1"] = {
    "data": {"editPaymentVerificationPlan": {"paymentPlan": {"status": "FINISHED"}}}
}
