# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestFilterIndividualsByProgram::test_individual_query_all_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {"node": {"program": {"name": "Test program ONE"}}},
                {"node": {"program": {"name": "Test program ONE"}}},
                {"node": {"program": {"name": "Test program ONE"}}},
            ]
        }
    }
}

snapshots["TestFilterIndividualsByProgram::test_individual_query_all_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestFilterIndividualsByProgram::test_individual_query_filter_by_duplicates_only 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {"node": {"deduplicationGoldenRecordStatus": "UNIQUE", "program": {"name": "Test program ONE"}}},
                {"node": {"deduplicationGoldenRecordStatus": "UNIQUE", "program": {"name": "Test program ONE"}}},
                {"node": {"deduplicationGoldenRecordStatus": "UNIQUE", "program": {"name": "Test program ONE"}}},
                {"node": {"deduplicationGoldenRecordStatus": "UNIQUE", "program": {"name": "Test program ONE"}}},
                {"node": {"deduplicationGoldenRecordStatus": "UNIQUE", "program": {"name": "Test program ONE"}}},
                {"node": {"deduplicationGoldenRecordStatus": "UNIQUE", "program": {"name": "Test program ONE"}}},
                {"node": {"deduplicationGoldenRecordStatus": "UNIQUE", "program": {"name": "Test program ONE"}}},
            ]
        }
    }
}

snapshots["TestFilterIndividualsByProgram::test_individual_query_filter_by_duplicates_only 2"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {"node": {"deduplicationGoldenRecordStatus": "DUPLICATE", "program": {"name": "Test program ONE"}}}
            ]
        }
    }
}

snapshots["TestFilterIndividualsByProgram::test_individual_query_rdi_id 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "fullName": "TEST User",
                        "identities": {"edges": [], "totalCount": 0},
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}
