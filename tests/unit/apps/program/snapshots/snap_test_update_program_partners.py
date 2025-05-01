# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestUpdateProgramPartners::test_update_full_area_access_flag 1"] = {
    "data": {
        "updateProgramPartners": {
            "program": {
                "partnerAccess": "ALL_PARTNERS_ACCESS",
                "partners": [
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "Other Partner",
                    },
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "UNICEF",
                    },
                ],
            }
        }
    }
}

snapshots["TestUpdateProgramPartners::test_update_full_area_access_flag 2"] = {
    "data": {
        "updateProgramPartners": {
            "program": {
                "partnerAccess": "SELECTED_PARTNERS_ACCESS",
                "partners": [
                    {"areaAccess": "ADMIN_AREA", "areas": [{"name": "Area in AFG 1"}], "name": "Other Partner"},
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "UNICEF",
                    },
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "WFP",
                    },
                ],
            }
        }
    }
}

snapshots["TestUpdateProgramPartners::test_update_program_of_other_partner_raise_error 1"] = {
    "data": {"updateProgramPartners": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "['Please assign access to your partner before saving the programme.']",
            "path": ["updateProgramPartners"],
        }
    ],
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_0_valid 1"] = {
    "data": {
        "updateProgramPartners": {
            "program": {
                "partnerAccess": "SELECTED_PARTNERS_ACCESS",
                "partners": [
                    {
                        "areaAccess": "ADMIN_AREA",
                        "areas": [{"name": "Area1"}, {"name": "Area2"}],
                        "name": "Partner to be added",
                    },
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "UNICEF",
                    },
                    {"areaAccess": "ADMIN_AREA", "areas": [{"name": "Area1"}, {"name": "Area2"}], "name": "WFP"},
                ],
            }
        }
    }
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_1_invalid_all_partner_access 1"] = {
    "data": {"updateProgramPartners": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "['You cannot specify partners for the chosen access type']",
            "path": ["updateProgramPartners"],
        }
    ],
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_2_invalid_none_partner_access 1"] = {
    "data": {"updateProgramPartners": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "['You cannot specify partners for the chosen access type']",
            "path": ["updateProgramPartners"],
        }
    ],
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_all_partners_access 1"] = {
    "data": {
        "updateProgramPartners": {
            "program": {
                "partnerAccess": "ALL_PARTNERS_ACCESS",
                "partners": [
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "Other Partner",
                    },
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "UNICEF",
                    },
                ],
            }
        }
    }
}

snapshots[
    "TestUpdateProgramPartners::test_update_program_partners_all_partners_access_refresh_partners_after_update 1"
] = {
    "data": {
        "updateProgramPartners": {
            "program": {
                "partnerAccess": "ALL_PARTNERS_ACCESS",
                "partners": [
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "Other Partner",
                    },
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "UNICEF",
                    },
                ],
            }
        }
    }
}

snapshots[
    "TestUpdateProgramPartners::test_update_program_partners_all_partners_access_refresh_partners_after_update 2"
] = {
    "data": {
        "updateProgramPartners": {
            "program": {
                "partnerAccess": "ALL_PARTNERS_ACCESS",
                "partners": [
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "Other Partner",
                    },
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "Partner without role in in BA",
                    },
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "UNICEF",
                    },
                ],
            }
        }
    }
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_authenticated_0_with_permissions 1"] = {
    "data": {
        "updateProgramPartners": {
            "program": {
                "partnerAccess": "NONE_PARTNERS_ACCESS",
                "partners": [
                    {
                        "areaAccess": "BUSINESS_AREA",
                        "areas": [{"name": "Area in AFG 1"}, {"name": "Area in AFG 2"}],
                        "name": "UNICEF",
                    }
                ],
            }
        }
    }
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_authenticated_1_without_permissions 1"] = {
    "data": {"updateProgramPartners": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["updateProgramPartners"],
        }
    ],
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_invalid_access_type_from_object 1"] = {
    "data": {"updateProgramPartners": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "['You cannot specify partners for the chosen access type']",
            "path": ["updateProgramPartners"],
        }
    ],
}

snapshots["TestUpdateProgramPartners::test_update_program_partners_not_authenticated 1"] = {
    "data": {"updateProgramPartners": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "Permission Denied: User is not authenticated.",
            "path": ["updateProgramPartners"],
        }
    ],
}
