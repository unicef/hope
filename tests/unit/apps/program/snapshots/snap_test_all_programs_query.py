# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestAllProgramsQuery::test_all_programs_query_0_with_permission 1"] = {
    "data": {"allPrograms": {"edges": [{"node": {"name": "Program for User Role"}}], "totalCount": 1}}
}

snapshots["TestAllProgramsQuery::test_all_programs_query_1_without_permission 1"] = {
    "data": {"allPrograms": None},
    "errors": [{"locations": [{"column": 9, "line": 3}], "message": "Permission Denied", "path": ["allPrograms"]}],
}

snapshots["TestAllProgramsQuery::test_all_programs_query_filter_beneficiary_group 1"] = {
    "data": {"allPrograms": {"edges": [{"node": {"name": "Other Program Beneficiary Group 1"}}], "totalCount": 1}}
}

snapshots["TestAllProgramsQuery::test_all_programs_query_filter_beneficiary_group 2"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {"node": {"name": "Other Program Beneficiary Group 1"}},
                {"node": {"name": "Program Beneficiary Group 1"}},
                {"node": {"name": "Program Beneficiary Group 2"}},
                {"node": {"name": "Program for Partner Role"}},
                {"node": {"name": "Program with all partners access"}},
                {"node": {"name": "Program with none partner access"}},
                {"node": {"name": "Program with partner access"}},
                {"node": {"name": "Program with selected partner access"}},
            ],
            "totalCount": 8,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_query_filter_dct 1"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {"node": {"name": "Program with all partners access"}},
                {"node": {"name": "Program with none partner access"}},
                {"node": {"name": "Program with partner access"}},
                {"node": {"name": "Program with selected partner access"}},
            ],
            "totalCount": 4,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_query_first_partner 1"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {"node": {"name": "Program for Partner Role"}},
                {"node": {"name": "Program with all partners access"}},
                {"node": {"name": "Program with partner access"}},
            ],
            "totalCount": 3,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_query_other_partner 1"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {"node": {"name": "Program for Partner Role"}},
                {"node": {"name": "Program with all partners access"}},
                {"node": {"name": "Program with selected partner access"}},
            ],
            "totalCount": 3,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_query_unicef_partner 1"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {"node": {"name": "Program for Partner Role"}},
                {"node": {"name": "Program with all partners access"}},
                {"node": {"name": "Program with none partner access"}},
                {"node": {"name": "Program with partner access"}},
                {"node": {"name": "Program with selected partner access"}},
            ],
            "totalCount": 5,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_query_user_not_authenticated 1"] = {
    "data": {"allPrograms": None},
    "errors": [
        {
            "locations": [{"column": 9, "line": 3}],
            "message": "Permission Denied: User is not authenticated.",
            "path": ["allPrograms"],
        }
    ],
}

snapshots["TestAllProgramsQuery::test_all_programs_query_without_ba_header 1"] = {
    "data": {"allPrograms": None},
    "errors": [
        {"locations": [{"column": 9, "line": 3}], "message": "Not found header Business-Area", "path": ["allPrograms"]}
    ],
}

snapshots["TestAllProgramsQuery::test_all_programs_with_cycles_filter 1"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {
                    "node": {
                        "cycles": {
                            "edges": [
                                {
                                    "node": {
                                        "status": "ACTIVE",
                                        "title": "Default Cycle",
                                        "totalDeliveredQuantityUsd": 0.0,
                                    }
                                }
                            ],
                            "totalCount": 1,
                        },
                        "name": "Program with all partners access",
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_with_cycles_filter 2"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {
                    "node": {
                        "cycles": {
                            "edges": [
                                {
                                    "node": {
                                        "status": "ACTIVE",
                                        "title": "Second CYCLE with total_delivered_quantity_usd",
                                        "totalDeliveredQuantityUsd": 999.0,
                                    }
                                }
                            ],
                            "totalCount": 1,
                        },
                        "name": "Program with all partners access",
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_with_cycles_filter 3"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {
                    "node": {
                        "cycles": {
                            "edges": [
                                {
                                    "node": {
                                        "status": "ACTIVE",
                                        "title": "Default Cycle",
                                        "totalDeliveredQuantityUsd": 0.0,
                                    }
                                },
                                {
                                    "node": {
                                        "status": "ACTIVE",
                                        "title": "Second CYCLE with total_delivered_quantity_usd",
                                        "totalDeliveredQuantityUsd": 999.0,
                                    }
                                },
                            ],
                            "totalCount": 2,
                        },
                        "name": "Program with all partners access",
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_with_cycles_filter 4"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {
                    "node": {
                        "cycles": {
                            "edges": [
                                {
                                    "node": {
                                        "status": "ACTIVE",
                                        "title": "Second CYCLE with total_delivered_quantity_usd",
                                        "totalDeliveredQuantityUsd": 999.0,
                                    }
                                }
                            ],
                            "totalCount": 1,
                        },
                        "name": "Program with all partners access",
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}

snapshots["TestAllProgramsQuery::test_all_programs_with_cycles_filter 5"] = {
    "data": {
        "allPrograms": {
            "edges": [
                {
                    "node": {
                        "cycles": {
                            "edges": [
                                {
                                    "node": {
                                        "status": "ACTIVE",
                                        "title": "Default Cycle",
                                        "totalDeliveredQuantityUsd": 0.0,
                                    }
                                },
                                {
                                    "node": {
                                        "status": "ACTIVE",
                                        "title": "Second CYCLE with total_delivered_quantity_usd",
                                        "totalDeliveredQuantityUsd": 999.0,
                                    }
                                },
                            ],
                            "totalCount": 2,
                        },
                        "name": "Program with all partners access",
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}

snapshots["TestAllProgramsQuery::test_program_can_run_deduplication_and_is_deduplication_disabled 1"] = {
    "data": {"canRunDeduplication": True, "isDeduplicationDisabled": True}
}

snapshots["TestAllProgramsQuery::test_program_can_run_deduplication_and_is_deduplication_disabled 2"] = {
    "data": {"canRunDeduplication": True, "isDeduplicationDisabled": False}
}

snapshots["TestAllProgramsQuery::test_program_can_run_deduplication_and_is_deduplication_disabled 3"] = {
    "data": {"canRunDeduplication": True, "isDeduplicationDisabled": True}
}
