# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_admin2 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "status": 1,
                    }
                }
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_assigned_to_correct_user 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_assigned_to_incorrect_user 1"] = {
    "data": {"allGrievanceTicket": {"edges": []}}
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_category_0_category_positive_feedback 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_category_1_category_negative_feedback 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "status": 4,
                    }
                }
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_created_at 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_score 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "needsAdjudicationTicketDetails": {
                            "extraData": {
                                "goldenRecords": [
                                    {"distinct": True, "duplicate": False, "fullName": "full_name", "score": 1.2}
                                ],
                                "possibleDuplicate": [
                                    {"distinct": False, "duplicate": True, "fullName": "full_name", "score": 2.0}
                                ],
                            },
                            "scoreMax": 150.0,
                            "scoreMin": 100.0,
                            "selectedDistinct": [],
                        },
                        "status": 1,
                    }
                }
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_score 2"] = {
    "data": {"allGrievanceTicket": {"edges": []}}
}

snapshots["TestGrievanceQuery::test_grievance_list_filtered_by_status 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_query_all_0_with_permission 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_query_all_1_without_permission 1"] = {
    "data": {"allGrievanceTicket": None},
    "errors": [
        {"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allGrievanceTicket"]}
    ],
}

snapshots["TestGrievanceQuery::test_grievance_query_all_for_all_programs_0_with_permission 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-02-12T00:00:00+00:00",
                        "description": "Ticket with other program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 2"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_query_all_for_all_programs_1_without_permission 1"] = {
    "data": {"allGrievanceTicket": None},
    "errors": [
        {"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allGrievanceTicket"]}
    ],
}

snapshots[
    "TestGrievanceQuery::test_grievance_query_all_for_all_programs_permission_in_single_program_0_with_permission 1"
] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_query_all_for_all_programs_permission_in_single_program_1_without_permission 1"
] = {
    "data": {"allGrievanceTicket": None},
    "errors": [
        {"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allGrievanceTicket"]}
    ],
}

snapshots["TestGrievanceQuery::test_grievance_query_single_0_with_permission 1"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-22T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, in progress",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_query_single_1_without_permission 1"] = {
    "data": {"grievanceTicket": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["grievanceTicket"]}],
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_all_programs 1"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 8,
            "consent": True,
            "createdAt": "2020-03-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 1, new",
            "language": "Polish",
            "status": 1,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_all_programs 2"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 5,
            "consent": True,
            "createdAt": "2020-07-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, on hold",
            "language": "English",
            "status": 4,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_all_programs 3"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-22T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, in progress",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_all_programs 4"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_all_programs 5"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_all_programs 6"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_program 1"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 8,
            "consent": True,
            "createdAt": "2020-03-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 1, new",
            "language": "Polish",
            "status": 1,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_program 2"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 5,
            "consent": True,
            "createdAt": "2020-07-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, on hold",
            "language": "English",
            "status": 4,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_program 3"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-22T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, in progress",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_program 4"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_program 5"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_unicef_for_program 6"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_all_programs 1"
] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 8,
            "consent": True,
            "createdAt": "2020-03-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 1, new",
            "language": "Polish",
            "status": 1,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_all_programs 2"
] = {
    "data": {"grievanceTicket": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "User is not active creator/assignee and does not have 'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE' permission or user does not have access to the ticket's program or its admin area",
            "path": ["grievanceTicket"],
        }
    ],
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_all_programs 3"
] = {
    "data": {"grievanceTicket": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "User is not active creator/assignee and does not have 'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE' permission or user does not have access to the ticket's program or its admin area",
            "path": ["grievanceTicket"],
        }
    ],
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_all_programs 4"
] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_all_programs 5"
] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_all_programs 6"
] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_program 1"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 8,
            "consent": True,
            "createdAt": "2020-03-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 1, new",
            "language": "Polish",
            "status": 1,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_program 2"] = {
    "data": {"grievanceTicket": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "User is not active creator/assignee and does not have 'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE' permission or user does not have access to the ticket's program or its admin area",
            "path": ["grievanceTicket"],
        }
    ],
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_program 3"] = {
    "data": {"grievanceTicket": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "User is not active creator/assignee and does not have 'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE' permission or user does not have access to the ticket's program or its admin area",
            "path": ["grievanceTicket"],
        }
    ],
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_program 4"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_program 5"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_1_access_for_program 6"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_all_programs 1"
] = {
    "data": {"grievanceTicket": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "User is not active creator/assignee and does not have 'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE' permission or user does not have access to the ticket's program or its admin area",
            "path": ["grievanceTicket"],
        }
    ],
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_all_programs 2"
] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 5,
            "consent": True,
            "createdAt": "2020-07-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, on hold",
            "language": "English",
            "status": 4,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_all_programs 3"
] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-22T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, in progress",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_all_programs 4"
] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_all_programs 5"
] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_all_programs 6"
] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_program 1"] = {
    "data": {"grievanceTicket": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "User is not active creator/assignee and does not have 'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE' permission or user does not have access to the ticket's program or its admin area",
            "path": ["grievanceTicket"],
        }
    ],
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_program 2"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 5,
            "consent": True,
            "createdAt": "2020-07-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, on hold",
            "language": "English",
            "status": 4,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_program 3"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-22T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, in progress",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_program 4"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_program 5"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_admin_area_2_access_for_program 6"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_all_programs 1"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 8,
            "consent": True,
            "createdAt": "2020-03-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 1, new",
            "language": "Polish",
            "status": 1,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_all_programs 2"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 5,
            "consent": True,
            "createdAt": "2020-07-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, on hold",
            "language": "English",
            "status": 4,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_all_programs 3"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-22T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, in progress",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_all_programs 4"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_all_programs 5"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_all_programs 6"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_program 1"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 8,
            "consent": True,
            "createdAt": "2020-03-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 1, new",
            "language": "Polish",
            "status": 1,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_program 2"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 5,
            "consent": True,
            "createdAt": "2020-07-12T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, on hold",
            "language": "English",
            "status": 4,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_program 3"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Example",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-22T00:00:00+00:00",
            "description": "Ticket with program, in admin area 2, in progress",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_program 4"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-23T00:00:00+00:00",
            "description": "Ticket with program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_program 5"] = {
    "data": {
        "grievanceTicket": {
            "admin": None,
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-24T00:00:00+00:00",
            "description": "Ticket without program, without admin area",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_detail_partner_with_full_area_access_for_program 6"] = {
    "data": {
        "grievanceTicket": {
            "admin": "City Test",
            "category": 7,
            "consent": True,
            "createdAt": "2020-08-25T00:00:00+00:00",
            "description": "Ticket without program, in admin area 1",
            "language": "Polish, English",
            "status": 3,
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_list_for_all_programs_permission_in_specific_programs_1 1"
] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_list_for_all_programs_permission_in_specific_programs_2 1"
] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-02-12T00:00:00+00:00",
                        "description": "Ticket with other program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 2"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_list_for_all_programs_permission_in_specific_programs_3 1"
] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-02-12T00:00:00+00:00",
                        "description": "Ticket with other program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 2"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_list_partner_unicef_for_all_programs 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-02-12T00:00:00+00:00",
                        "description": "Ticket with other program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 2"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_list_partner_unicef_for_program 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_list_partner_with_admin_area_1_access_for_all_programs 1"
] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-02-12T00:00:00+00:00",
                        "description": "Ticket with other program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 2"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_list_partner_with_admin_area_1_access_for_program 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots[
    "TestGrievanceQuery::test_grievance_ticket_query_list_partner_with_admin_area_2_access_for_all_programs 1"
] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-02-12T00:00:00+00:00",
                        "description": "Ticket with other program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 2"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_list_partner_with_admin_area_2_access_for_program 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_list_partner_with_full_area_access_for_all_programs 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-02-12T00:00:00+00:00",
                        "description": "Ticket with other program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 2"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "programs": [{"name": "Program 1"}],
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "programs": [{"name": "Program 1"}],
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "programs": [{"name": "Program 1"}],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-24T00:00:00+00:00",
                        "description": "Ticket without program, without admin area",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": "City Test",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-25T00:00:00+00:00",
                        "description": "Ticket without program, in admin area 1",
                        "language": "Polish, English",
                        "programs": [],
                        "status": 3,
                    }
                },
            ]
        }
    }
}

snapshots["TestGrievanceQuery::test_grievance_ticket_query_list_partner_with_full_area_access_for_program 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "City Test",
                        "category": 8,
                        "consent": True,
                        "createdAt": "2020-03-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 1, new",
                        "language": "Polish",
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 5,
                        "consent": True,
                        "createdAt": "2020-07-12T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, on hold",
                        "language": "English",
                        "status": 4,
                    }
                },
                {
                    "node": {
                        "admin": "City Example",
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-22T00:00:00+00:00",
                        "description": "Ticket with program, in admin area 2, in progress",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
                {
                    "node": {
                        "admin": None,
                        "category": 7,
                        "consent": True,
                        "createdAt": "2020-08-23T00:00:00+00:00",
                        "description": "Ticket with program, without admin area",
                        "language": "Polish, English",
                        "status": 3,
                    }
                },
            ]
        }
    }
}
