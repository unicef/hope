# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["UserRolesTest::test_user_choice_data 1"] = {
    "data": {
        "userPartnerChoices": [
            {"name": "Partner with BA access"},
            {"name": "UNHCR"},
            {"name": "UNICEF"},
            {"name": "WFP"},
        ]
    }
}
