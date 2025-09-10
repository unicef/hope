# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["TestRegistrationDataImportDatahubQuery::test_registration_data_import_datahub_query_single 1"] = {
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": 'Cannot query field "registrationDataImportDatahub" on type "Query".',
        }
    ]
}
