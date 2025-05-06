# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestImportedHouseholdQuery::test_imported_household_query_0_detail_id 1"] = {
    "data": {
        "household": {
            "country": "Afghanistan",
            "importId": "HH-123 (Detail id test123)",
            "individuals": {
                "edges": [
                    {
                        "node": {
                            "documents": {"edges": [{"node": {"country": "Afghanistan", "photo": None}}]},
                            "importId": "IND-123 (Detail ID test123)",
                            "phoneNo": "+48123123213",
                            "phoneNoAlternative": "+48123123213",
                            "phoneNoAlternativeValid": True,
                            "phoneNoValid": True,
                            "preferredLanguage": "en",
                        }
                    }
                ]
            },
        }
    }
}

snapshots["TestImportedHouseholdQuery::test_imported_household_query_1_enumerator_rec_id 1"] = {
    "data": {
        "household": {
            "country": "Afghanistan",
            "importId": "HH-123 (Enumerator ID 123)",
            "individuals": {
                "edges": [
                    {
                        "node": {
                            "documents": {"edges": [{"node": {"country": "Afghanistan", "photo": None}}]},
                            "importId": "IND-123 (Detail ID test123)",
                            "phoneNo": "+48123123213",
                            "phoneNoAlternative": "+48123123213",
                            "phoneNoAlternativeValid": True,
                            "phoneNoValid": True,
                            "preferredLanguage": "en",
                        }
                    }
                ]
            },
        }
    }
}

snapshots["TestImportedHouseholdQuery::test_imported_household_query_all_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 1}},
                {"node": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 2}},
                {"node": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 3}},
                {"node": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 4}},
                {"node": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 5}},
                {"node": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 11}},
                {"node": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 14}},
            ]
        }
    }
}

snapshots["TestImportedHouseholdQuery::test_imported_household_query_all_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots["TestImportedHouseholdQuery::test_imported_household_query_single_0_with_permission 1"] = {
    "data": {"household": {"address": "Lorem Ipsum", "countryOrigin": "Poland", "size": 2}}
}

snapshots["TestImportedHouseholdQuery::test_imported_household_query_single_1_without_permission 1"] = {
    "data": {"household": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["household"]}],
}
