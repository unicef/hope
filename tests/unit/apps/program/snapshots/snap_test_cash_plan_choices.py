# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["TestCashPlanChoices::test_status_choices_query 1"] = {
    "data": {
        "cashPlanStatusChoices": [
            {"name": "Active", "value": "ACTIVE"},
            {"name": "Draft", "value": "DRAFT"},
            {"name": "Finished", "value": "FINISHED"},
        ]
    }
}
