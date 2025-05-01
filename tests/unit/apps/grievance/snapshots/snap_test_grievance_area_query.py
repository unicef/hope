# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestGrievanceAreaQuery::test_one_admin2_is_filtered_0_with_permission 1"] = {
    "data": {
        "allGrievanceTicket": {"edges": [{"node": {"description": "doshi"}}, {"node": {"description": "no_admin"}}]}
    }
}

snapshots["TestGrievanceAreaQuery::test_one_admin2_is_filtered_1_without_permission 1"] = {
    "data": {"allGrievanceTicket": None},
    "errors": [
        {"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allGrievanceTicket"]}
    ],
}
