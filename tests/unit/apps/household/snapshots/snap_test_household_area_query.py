# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestHouseholdAreaQuery::test_household_admin_area_1_is_filtered_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "address_1", "countryOrigin": "Afghanistan", "size": 1}},
                {"node": {"address": "address_2", "countryOrigin": "Afghanistan", "size": 2}},
                {"node": {"address": "address_3", "countryOrigin": "Afghanistan", "size": 3}},
                {"node": {"address": "address_4", "countryOrigin": "Afghanistan", "size": 4}},
                {"node": {"address": "address_5", "countryOrigin": "Afghanistan", "size": 5}},
                {"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}},
            ]
        }
    }
}

snapshots["TestHouseholdAreaQuery::test_household_admin_area_1_is_filtered_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 5, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots["TestHouseholdAreaQuery::test_household_admin_area_2_and_admin_area_3_is_filtered_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "address_1", "countryOrigin": "Afghanistan", "size": 1}},
                {"node": {"address": "address_4", "countryOrigin": "Afghanistan", "size": 4}},
                {"node": {"address": "address_5", "countryOrigin": "Afghanistan", "size": 5}},
                {"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}},
            ]
        }
    }
}

snapshots["TestHouseholdAreaQuery::test_household_admin_area_2_and_admin_area_3_is_filtered_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 5, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots["TestHouseholdAreaQuery::test_household_admin_area_2_is_filtered_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "address_3", "countryOrigin": "Afghanistan", "size": 3}},
                {"node": {"address": "address_4", "countryOrigin": "Afghanistan", "size": 4}},
                {"node": {"address": "address_5", "countryOrigin": "Afghanistan", "size": 5}},
                {"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}},
            ]
        }
    }
}

snapshots["TestHouseholdAreaQuery::test_household_admin_area_2_is_filtered_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 5, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots["TestHouseholdAreaQuery::test_household_admin_area_3_is_filtered_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "address_5", "countryOrigin": "Afghanistan", "size": 5}},
                {"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}},
            ]
        }
    }
}

snapshots["TestHouseholdAreaQuery::test_household_admin_area_3_is_filtered_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 5, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots["TestHouseholdAreaQuery::test_household_many_admin_area_2_is_filtered_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "address_1", "countryOrigin": "Afghanistan", "size": 1}},
                {"node": {"address": "address_2", "countryOrigin": "Afghanistan", "size": 2}},
                {"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}},
            ]
        }
    }
}

snapshots["TestHouseholdAreaQuery::test_household_many_admin_area_2_is_filtered_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 5, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots["TestHouseholdAreaQuery::test_household_many_admin_area_3_is_filtered_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "address_4", "countryOrigin": "Afghanistan", "size": 4}},
                {"node": {"address": "address_5", "countryOrigin": "Afghanistan", "size": 5}},
                {"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}},
            ]
        }
    }
}

snapshots["TestHouseholdAreaQuery::test_household_many_admin_area_3_is_filtered_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 5, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots["TestHouseholdAreaQuery::test_household_with_no_admin_area_is_filtered_0_with_permission 1"] = {
    "data": {
        "allHouseholds": {"edges": [{"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}}]}
    }
}

snapshots["TestHouseholdAreaQuery::test_household_with_no_admin_area_is_filtered_1_without_permission 1"] = {
    "data": {"allHouseholds": None},
    "errors": [{"locations": [{"column": 5, "line": 3}], "message": "Permission Denied", "path": ["allHouseholds"]}],
}

snapshots[
    "TestHouseholdAreaQuery::test_households_area_filtered_when_partner_is_unicef_0_without_user_role_permission 1"
] = {
    "data": {
        "allHouseholds": {
            "edges": [
                {"node": {"address": "address_1", "countryOrigin": "Afghanistan", "size": 1}},
                {"node": {"address": "address_2", "countryOrigin": "Afghanistan", "size": 2}},
                {"node": {"address": "address_3", "countryOrigin": "Afghanistan", "size": 3}},
                {"node": {"address": "address_4", "countryOrigin": "Afghanistan", "size": 4}},
                {"node": {"address": "address_5", "countryOrigin": "Afghanistan", "size": 5}},
                {"node": {"address": "address_6", "countryOrigin": "Afghanistan", "size": 6}},
            ]
        }
    }
}
