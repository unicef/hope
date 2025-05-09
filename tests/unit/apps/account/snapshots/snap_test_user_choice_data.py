# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["RoleAssignmentsTest::test_user_choice_data 1"] = {
    "data": {
        "userPartnerChoices": [
            {"name": "Partner Without Role"},
            {"name": "Partner with BA access"},
            {"name": "UNHCR"},
            {"name": "UNICEF HQ"},
            {"name": "UNICEF Partner for afghanistan"},
            {"name": "WFP"},
        ]
    }
}
