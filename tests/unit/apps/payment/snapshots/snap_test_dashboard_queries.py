# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestDashboardQueries::test_charts_0_chartVolumeByDeliveryMechanism 1"] = {
    "data": {"chartVolumeByDeliveryMechanism": {"datasets": [{"data": [480.0, 600.0]}], "labels": ["Cash", "Voucher"]}}
}

snapshots["TestDashboardQueries::test_charts_1_chartPayment 1"] = {
    "data": {
        "chartPayment": {"datasets": [{"data": [7.0, 2.0]}], "labels": ["Successful Payments", "Unsuccessful Payments"]}
    }
}

snapshots["TestDashboardQueries::test_sections_0_sectionTotalTransferred 1"] = {
    "data": {"sectionTotalTransferred": {"total": 1080.0}}
}

snapshots["TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_0_admin2 1"] = {
    "data": {
        "tableTotalCashTransferredByAdministrativeArea": {
            "data": [
                {"admin2": "afghanistan city 1", "totalCashTransferred": 220.0, "totalHouseholds": 2},
                {"admin2": "afghanistan city 2", "totalCashTransferred": 360.0, "totalHouseholds": 3},
                {"admin2": "afghanistan city 3", "totalCashTransferred": 500.0, "totalHouseholds": 4},
            ]
        }
    }
}

snapshots["TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_1_totalCashTransferred 1"] = {
    "data": {
        "tableTotalCashTransferredByAdministrativeArea": {
            "data": [
                {"admin2": "afghanistan city 1", "totalCashTransferred": 220.0, "totalHouseholds": 2},
                {"admin2": "afghanistan city 2", "totalCashTransferred": 360.0, "totalHouseholds": 3},
                {"admin2": "afghanistan city 3", "totalCashTransferred": 500.0, "totalHouseholds": 4},
            ]
        }
    }
}

snapshots["TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_2_totalHouseholds 1"] = {
    "data": {
        "tableTotalCashTransferredByAdministrativeArea": {
            "data": [
                {"admin2": "afghanistan city 1", "totalCashTransferred": 220.0, "totalHouseholds": 2},
                {"admin2": "afghanistan city 2", "totalCashTransferred": 360.0, "totalHouseholds": 3},
                {"admin2": "afghanistan city 3", "totalCashTransferred": 500.0, "totalHouseholds": 4},
            ]
        }
    }
}

snapshots[
    "TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_for_global_business_area 1"
] = {
    "data": {"tableTotalCashTransferredByAdministrativeArea": None},
    "errors": [
        {
            "locations": [{"column": 9, "line": 7}],
            "message": "Permission Denied",
            "path": ["tableTotalCashTransferredByAdministrativeArea"],
        }
    ],
}

snapshots["TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_for_people_0_admin2 1"] = {
    "data": {"tableTotalCashTransferredByAdministrativeAreaForPeople": {"data": []}}
}

snapshots[
    "TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_for_people_1_totalCashTransferred 1"
] = {"data": {"tableTotalCashTransferredByAdministrativeAreaForPeople": {"data": []}}}

snapshots[
    "TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_for_people_2_totalHouseholds 1"
] = {"data": {"tableTotalCashTransferredByAdministrativeAreaForPeople": {"data": []}}}

snapshots[
    "TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area_for_people_for_global_business_area 1"
] = {
    "data": {"tableTotalCashTransferredByAdministrativeAreaForPeople": None},
    "errors": [
        {
            "locations": [{"column": 9, "line": 7}],
            "message": "Permission Denied",
            "path": ["tableTotalCashTransferredByAdministrativeAreaForPeople"],
        }
    ],
}
