# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestRefuseRdiMutation::test_refuse_registration_data_import_0_with_permission 1"] = {
    "data": {"refuseRegistrationDataImport": {"registrationDataImport": {"refuseReason": None, "status": "REFUSED"}}}
}

snapshots["TestRefuseRdiMutation::test_refuse_registration_data_import_1_with_permission 1"] = {
    "data": {"refuseRegistrationDataImport": None},
    "errors": [
        {
            "locations": [{"column": 9, "line": 3}],
            "message": "Only In Review Registration Data Import can be refused",
            "path": ["refuseRegistrationDataImport"],
        }
    ],
}

snapshots["TestRefuseRdiMutation::test_refuse_registration_data_import_2_without_permission 1"] = {
    "data": {"refuseRegistrationDataImport": None},
    "errors": [
        {
            "locations": [{"column": 9, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["refuseRegistrationDataImport"],
        }
    ],
}

snapshots["TestRefuseRdiMutation::test_refuse_registration_data_import_with_reason 1"] = {
    "data": {
        "refuseRegistrationDataImport": {
            "registrationDataImport": {"refuseReason": "This is refuse reason", "status": "REFUSED"}
        }
    }
}
