# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestUserFilter::test_users_by_business_area 1"] = {
    "data": {
        "allUsers": {
            "edges": [
                {
                    "node": {
                        "partner": {"name": "UNICEF HQ"},
                        "partnerRoles": [
                            {
                                "businessArea": {"name": "Afghanistan"},
                                "program": None,
                                "role": {"name": "Role with all permissions", "permissions": ["PROGRAMME_VIEW_LIST"]},
                            }
                        ],
                        "userRoles": [],
                        "username": "unicef_user_without_role",
                    }
                },
                {
                    "node": {
                        "partner": {"name": "Partner With Test Role"},
                        "partnerRoles": [
                            {
                                "businessArea": {"name": "Afghanistan"},
                                "program": {"name": "Test Program"},
                                "role": {"name": "Test Role", "permissions": ["USER_MANAGEMENT_VIEW_LIST"]},
                            }
                        ],
                        "userRoles": [],
                        "username": "user_with_partner_with_test_role",
                    }
                },
                {
                    "node": {
                        "partner": {"name": "Default Empty Partner"},
                        "partnerRoles": [],
                        "userRoles": [
                            {
                                "businessArea": {"name": "Afghanistan"},
                                "program": {"name": "Different Program"},
                                "role": {"name": "Test Role", "permissions": ["USER_MANAGEMENT_VIEW_LIST"]},
                            }
                        ],
                        "username": "user_with_test_role",
                    }
                },
                {
                    "node": {
                        "partner": {"name": "Default Empty Partner"},
                        "partnerRoles": [],
                        "userRoles": [
                            {
                                "businessArea": {"name": "Afghanistan"},
                                "program": None,
                                "role": {"name": "Test Role", "permissions": ["USER_MANAGEMENT_VIEW_LIST"]},
                            }
                        ],
                        "username": "user_with_test_role_in_whole_ba",
                    }
                },
            ]
        }
    }
}

snapshots["TestUserFilter::test_users_by_program 1"] = {
    "data": {
        "allUsers": {
            "edges": [
                {"node": {"partner": {"name": "UNICEF HQ"}, "username": "unicef_user_without_role"}},
                {
                    "node": {
                        "partner": {"name": "Partner With Test Role"},
                        "username": "user_with_partner_with_test_role",
                    }
                },
                {"node": {"partner": {"name": "Default Empty Partner"}, "username": "user_with_test_role_in_whole_ba"}},
            ]
        }
    }
}

snapshots["TestUserFilter::test_users_by_roles 1"] = {
    "data": {
        "allUsers": {
            "edges": [
                {
                    "node": {
                        "partner": {"name": "Partner With Test Role"},
                        "partnerRoles": [
                            {
                                "businessArea": {"name": "Afghanistan"},
                                "program": {"name": "Test Program"},
                                "role": {"name": "Test Role", "permissions": ["USER_MANAGEMENT_VIEW_LIST"]},
                            }
                        ],
                        "userRoles": [],
                        "username": "user_with_partner_with_test_role",
                    }
                },
                {
                    "node": {
                        "partner": {"name": "Default Empty Partner"},
                        "partnerRoles": [],
                        "userRoles": [
                            {
                                "businessArea": {"name": "Afghanistan"},
                                "program": {"name": "Different Program"},
                                "role": {"name": "Test Role", "permissions": ["USER_MANAGEMENT_VIEW_LIST"]},
                            }
                        ],
                        "username": "user_with_test_role",
                    }
                },
                {
                    "node": {
                        "partner": {"name": "Default Empty Partner"},
                        "partnerRoles": [],
                        "userRoles": [
                            {
                                "businessArea": {"name": "Afghanistan"},
                                "program": None,
                                "role": {"name": "Test Role", "permissions": ["USER_MANAGEMENT_VIEW_LIST"]},
                            }
                        ],
                        "username": "user_with_test_role_in_whole_ba",
                    }
                },
            ]
        }
    }
}
