# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestExportPDFPaymentPlanSummary::test_export_pdf_payment_plan_summary_mutation 1"] = {
    "data": {"exportPdfPaymentPlanSummary": {"paymentPlan": {"status": "ACCEPTED"}}}
}
