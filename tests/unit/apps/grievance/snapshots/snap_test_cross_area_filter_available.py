# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestCrossAreaFilterAvailable::test_cross_area_filter_available 1"] = {
    "data": {"crossAreaFilterAvailable": True}
}

snapshots["TestCrossAreaFilterAvailable::test_cross_area_filter_available_for_unicef_partner 1"] = {
    "data": {"crossAreaFilterAvailable": True}
}

snapshots["TestCrossAreaFilterAvailable::test_cross_area_filter_not_available_area_restrictions 1"] = {
    "data": {"crossAreaFilterAvailable": False}
}

snapshots["TestCrossAreaFilterAvailable::test_cross_area_filter_not_available_no_permission 1"] = {
    "data": {"crossAreaFilterAvailable": False}
}

snapshots[
    "TestCrossAreaFilterAvailable::test_cross_area_filter_not_available_no_permission_and_area_restrictions 1"
] = {"data": {"crossAreaFilterAvailable": False}}
